"""Opt-in live check: three small billable calls; never emits the API key."""

import json
import os

import dify_plugin  # noqa: F401
from dify_plugin.entities.model.message import (
    PromptMessageTool,
    ToolPromptMessage,
    UserPromptMessage,
)

from models.llm.llm import AceDataCloudLLM


def run():
    llm = AceDataCloudLLM([])
    credentials = {
        "api_key": os.environ["ACEDATACLOUD_API_TOKEN"],
        "function_calling_type": "tool_call",
        "stream_function_calling": "supported",
    }
    model = "gpt-4.1-mini"
    llm.validate_credentials(model, credentials)
    result_chunks = list(
        llm.invoke(
            model,
            credentials,
            [UserPromptMessage(content="Reply only DIFY_OK")],
            {"max_tokens": 16, "temperature": 0},
            stream=False,
        )
    )
    result = result_chunks[0]
    message = result.delta.message
    usage = result.delta.usage
    assert "DIFY_OK" in message.content
    print(
        json.dumps(
            {
                "case": "non_stream",
                "model": result.model,
                "text": message.content,
                "prompt_tokens": usage.prompt_tokens,
                "completion_tokens": usage.completion_tokens,
            }
        )
    )
    messages = [
        UserPromptMessage(content="Call lookup_value with key alpha. Do not guess its value.")
    ]
    tool = PromptMessageTool(
        name="lookup_value",
        description="Look up a value by key.",
        parameters={
            "type": "object",
            "properties": {"key": {"type": "string"}},
            "required": ["key"],
            "additionalProperties": False,
        },
    )
    chunks = list(
        llm.invoke(
            model,
            credentials,
            messages,
            {"max_tokens": 64, "temperature": 0},
            tools=[tool],
            stream=True,
        )
    )
    calls = [t for c in chunks for t in c.delta.message.tool_calls]
    assert calls
    # The SDK emits accumulated tool calls before the final usage chunk.
    assistant = next(c.delta.message for c in reversed(chunks) if c.delta.message.tool_calls)
    assert assistant.tool_calls and assistant.tool_calls[0].function.name == "lookup_value"
    call = assistant.tool_calls[0]
    assert json.loads(call.function.arguments)["key"] == "alpha"
    print(
        json.dumps(
            {
                "case": "stream_tool",
                "tool": call.function.name,
                "arguments": call.function.arguments,
                "prompt_tokens": chunks[-1].delta.usage.prompt_tokens,
                "completion_tokens": chunks[-1].delta.usage.completion_tokens,
            }
        )
    )
    messages.extend(
        [
            assistant,
            ToolPromptMessage(tool_call_id=call.id, content="DIFY_TOOL_OK"),
            UserPromptMessage(content="Repeat the tool result verbatim and nothing else."),
        ]
    )
    chunks = list(
        llm.invoke(model, credentials, messages, {"max_tokens": 32, "temperature": 0}, stream=True)
    )
    content = "".join(c.delta.message.content or "" for c in chunks)
    assert "DIFY_TOOL_OK" in content, repr(content)
    print(
        json.dumps(
            {
                "case": "stream_tool_result",
                "text": content,
                "prompt_tokens": chunks[-1].delta.usage.prompt_tokens,
                "completion_tokens": chunks[-1].delta.usage.completion_tokens,
            }
        )
    )


if __name__ == "__main__":
    run()
