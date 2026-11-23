"""Translate Dify's OpenAI-shaped messages to the published Anthropic Messages API."""

import json

from dify_plugin.errors.model import InvokeBadRequestError, InvokeError


def content_blocks(content):
    if isinstance(content, str):
        return [{"type": "text", "text": content}] if content else []
    blocks = []
    for part in content or []:
        if part["type"] == "text":
            blocks.append({"type": "text", "text": part["text"]})
        elif part["type"] == "image_url":
            url = part["image_url"]["url"]
            if url.startswith("data:"):
                header, data = url.split(",", 1)
                if not header.endswith(";base64"):
                    raise InvokeBadRequestError(
                        "Messages image input requires base64 or an HTTPS URL."
                    )
                source = {"type": "base64", "media_type": header[5:-7], "data": data}
            elif url.startswith("https://"):
                source = {"type": "url", "url": url}
            else:
                raise InvokeBadRequestError("Messages image input requires base64 or an HTTPS URL.")
            blocks.append({"type": "image", "source": source})
        else:
            raise InvokeBadRequestError("Unsupported input block for this Messages model.")
    return blocks


def request_payload(openai):
    result = {
        "model": openai["model"],
        "stream": openai["stream"],
        "max_tokens": openai.get("max_tokens", 1024),
        "messages": [],
    }
    system = []
    for message in openai["messages"]:
        role = message["role"]
        if role in {"system", "developer"}:
            system.extend(content_blocks(message.get("content")))
            continue
        if role == "tool":
            role = "user"
            blocks = [
                {
                    "type": "tool_result",
                    "tool_use_id": message["tool_call_id"],
                    "content": content_blocks(message.get("content")),
                }
            ]
        else:
            blocks = content_blocks(message.get("content"))
            for call in message.get("tool_calls") or []:
                try:
                    arguments = json.loads(call["function"]["arguments"])
                except (ValueError, TypeError):
                    raise InvokeBadRequestError("Tool arguments must be a JSON object.") from None
                if not isinstance(arguments, dict):
                    raise InvokeBadRequestError("Tool arguments must be a JSON object.")
                blocks.append(
                    {
                        "type": "tool_use",
                        "id": call["id"],
                        "name": call["function"]["name"],
                        "input": arguments,
                    }
                )
        if result["messages"] and result["messages"][-1]["role"] == role:
            result["messages"][-1]["content"].extend(blocks)
        else:
            result["messages"].append({"role": role, "content": blocks})
    if system:
        result["system"] = system
    for name in ("temperature", "top_p"):
        if name in openai:
            result[name] = openai[name]
    if openai.get("stop"):
        result["stop_sequences"] = openai["stop"]
    if openai.get("tools"):
        result["tools"] = [
            {
                "name": tool["function"]["name"],
                "description": tool["function"].get("description", ""),
                "input_schema": tool["function"]["parameters"],
            }
            for tool in openai["tools"]
        ]
        result["tool_choice"] = {"type": "auto"}
    return result


def usage_counts(usage):
    prompt = sum(
        usage.get(key, 0)
        for key in ("input_tokens", "cache_read_input_tokens", "cache_creation_input_tokens")
    )
    output = usage.get("output_tokens", 0)
    return {"prompt_tokens": prompt, "completion_tokens": output, "total_tokens": prompt + output}


def finish_reason(reason):
    return {"tool_use": "tool_calls", "max_tokens": "length"}.get(reason, "stop")


class MessagesResponse:
    """Adapt the response to Dify SDK's existing tested result/usage converter."""

    def __init__(self, response):
        self.response = response

    def close(self):
        self.response.close()

    def json(self):
        data = self.response.json()
        if data.get("type") != "message" or not isinstance(data.get("content"), list):
            raise InvokeError("Ace Data Cloud returned an invalid Messages response.")
        text = []
        calls = []
        for block in data["content"]:
            if block["type"] == "text":
                text.append(block["text"])
            elif block["type"] == "tool_use":
                calls.append(
                    {
                        "id": block["id"],
                        "type": "function",
                        "function": {
                            "name": block["name"],
                            "arguments": json.dumps(block["input"]),
                        },
                    }
                )
        return {
            "id": data["id"],
            "choices": [
                {
                    "message": {
                        "role": "assistant",
                        "content": "".join(text),
                        "tool_calls": calls or None,
                    },
                    "finish_reason": finish_reason(data.get("stop_reason")),
                }
            ],
            "usage": usage_counts(data["usage"]),
        }

    def iter_lines(self, **kwargs):
        del kwargs
        usage = {}
        tool_indices = {}
        stopped = False
        for raw in self.response.iter_lines(decode_unicode=True):
            line = raw.decode() if isinstance(raw, bytes) else raw
            if not line.startswith("data:"):
                continue
            event = json.loads(line[5:].strip())
            kind = event.get("type")
            delta = None
            if kind == "error":
                raise InvokeError("The Ace Data Cloud Messages stream failed.")
            if kind == "message_start":
                usage.update(event["message"].get("usage", {}))
            elif kind == "content_block_start":
                block = event["content_block"]
                if block["type"] == "tool_use":
                    index = len(tool_indices)
                    tool_indices[event["index"]] = index
                    delta = {
                        "tool_calls": [
                            {
                                "index": index,
                                "id": block["id"],
                                "type": "function",
                                "function": {"name": block["name"], "arguments": ""},
                            }
                        ]
                    }
                elif block["type"] == "text" and block.get("text"):
                    delta = {"content": block["text"]}
            elif kind == "content_block_delta":
                block = event["delta"]
                if block["type"] == "text_delta":
                    delta = {"content": block["text"]}
                elif block["type"] == "input_json_delta":
                    delta = {
                        "tool_calls": [
                            {
                                "index": tool_indices[event["index"]],
                                "function": {"arguments": block["partial_json"]},
                            }
                        ]
                    }
            elif kind == "message_delta":
                usage.update(event.get("usage", {}))
                yield "data: " + json.dumps(
                    {
                        "choices": [
                            {
                                "delta": {},
                                "finish_reason": finish_reason(event["delta"].get("stop_reason")),
                            }
                        ]
                    }
                )
            elif kind == "message_stop":
                stopped = True
                yield "data: " + json.dumps({"choices": [], "usage": usage_counts(usage)})
                yield "data: [DONE]"
                break
            if delta is not None:
                yield "data: " + json.dumps({"choices": [{"delta": delta, "finish_reason": None}]})
        if not stopped:
            raise InvokeError("The Ace Data Cloud Messages stream ended before completion.")
