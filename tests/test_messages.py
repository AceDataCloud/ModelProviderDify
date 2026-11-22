import json

import dify_plugin  # noqa: F401 - patch network before requests/SSL imports
import pytest
import requests
from dify_plugin.config.config import DifyPluginEnv
from dify_plugin.core.plugin_registration import PluginRegistration
from dify_plugin.entities.model import ModelType
from dify_plugin.entities.model.message import SystemPromptMessage, UserPromptMessage
from dify_plugin.errors.model import InvokeError

from models.llm.messages import request_payload
from scripts.sync_model_catalog import project
from tests.test_provider import response


@pytest.fixture
def llm():
    return PluginRegistration(DifyPluginEnv()).get_model_instance("acedatacloud", ModelType.LLM)


def test_messages_only_model_uses_declared_protocol_with_bearer_auth(llm, monkeypatch):
    r = response(
        {
            "id": "msg_fixture",
            "type": "message",
            "content": [{"type": "text", "text": "Hello"}],
            "stop_reason": "end_turn",
            "usage": {"input_tokens": 4, "cache_read_input_tokens": 3, "output_tokens": 2},
        }
    )
    sent = {}

    def post(url, **kwargs):
        sent.update(url=url, **kwargs)
        return r

    monkeypatch.setattr(requests, "post", post)
    result = llm._invoke(
        "claude-sonnet-5-5",
        {"api_key": "placeholder"},
        [SystemPromptMessage(content="Be concise"), UserPromptMessage(content="Hello")],
        {"temperature": 0.2, "max_tokens": 64, "presence_penalty": 0.8},
        stream=False,
    )
    assert sent["url"] == "https://api.acedata.cloud/v1/messages"
    assert (
        sent["headers"]["Authorization"] == "Bearer placeholder"
        and "x-api-key" not in sent["headers"]
    )
    assert sent["json"]["system"] == [{"type": "text", "text": "Be concise"}]
    assert sent["json"]["messages"] == [
        {"role": "user", "content": [{"type": "text", "text": "Hello"}]}
    ]
    assert sent["json"]["max_tokens"] == 64 and "presence_penalty" not in sent["json"]
    assert (
        result.message.content == "Hello"
        and result.usage.prompt_tokens == 7
        and result.usage.completion_tokens == 2
    )
    assert r.was_closed


def test_messages_image_and_tool_history_are_not_sent_as_openai_blocks():
    payload = request_payload(
        {
            "model": "fixture",
            "stream": False,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "image_url", "image_url": {"url": "data:image/png;base64,YQ=="}}
                    ],
                },
                {
                    "role": "assistant",
                    "content": None,
                    "tool_calls": [
                        {"id": "call_1", "function": {"name": "lookup", "arguments": '{"key":"a"}'}}
                    ],
                },
                {"role": "tool", "tool_call_id": "call_1", "content": "42"},
            ],
            "tools": [
                {
                    "type": "function",
                    "function": {"name": "lookup", "parameters": {"type": "object"}},
                }
            ],
        }
    )
    assert payload["messages"][0]["content"][0] == {
        "type": "image",
        "source": {"type": "base64", "media_type": "image/png", "data": "YQ=="},
    }
    assert payload["messages"][1]["content"][0]["input"] == {"key": "a"}
    assert payload["messages"][2]["content"][0]["tool_use_id"] == "call_1"
    assert payload["tools"][0]["input_schema"] == {"type": "object"}


def test_messages_stream_text_usage_and_close(llm, monkeypatch):
    events = [
        {"type": "message_start", "message": {"usage": {"input_tokens": 5}}},
        {"type": "content_block_start", "index": 0, "content_block": {"type": "text", "text": ""}},
        {
            "type": "content_block_delta",
            "index": 0,
            "delta": {"type": "text_delta", "text": "Hello"},
        },
        {
            "type": "message_delta",
            "delta": {"stop_reason": "end_turn"},
            "usage": {"output_tokens": 2},
        },
        {"type": "message_stop"},
    ]
    r = response({})
    r.iter_lines = lambda **kw: iter("data: " + json.dumps(event) for event in events)
    monkeypatch.setattr(requests, "post", lambda *a, **kw: r)
    chunks = list(
        llm._invoke(
            "claude-sonnet-5-5",
            {"api_key": "placeholder"},
            [UserPromptMessage(content="Hello")],
            {},
        )
    )
    assert "".join(chunk.delta.message.content or "" for chunk in chunks) == "Hello"
    assert (
        chunks[-1].delta.usage.prompt_tokens == 5 and chunks[-1].delta.usage.completion_tokens == 2
    )
    assert r.was_closed


@pytest.mark.parametrize("events", [[], [{"type": "error", "error": {"message": "private"}}]])
def test_messages_stream_cannot_silently_finish_on_error(llm, monkeypatch, events):
    r = response({})
    r.iter_lines = lambda **kw: iter("data: " + json.dumps(event) for event in events)
    monkeypatch.setattr(requests, "post", lambda *a, **kw: r)
    with pytest.raises(InvokeError) as error:
        list(
            llm._invoke(
                "claude-sonnet-5-5",
                {"api_key": "placeholder"},
                [UserPromptMessage(content="Hello")],
                {},
            )
        )
    assert "private" not in str(error.value) and r.was_closed


def test_protocol_projection_uses_endpoint_metadata_not_names():
    snapshot = project(
        {
            "data": [
                {
                    "id": "arbitrary-model-name",
                    "label": "Example",
                    "type": "chat",
                    "endpoints": [
                        {
                            "protocol": "messages",
                            "path": "/v1/messages",
                            "auth": "bearer",
                            "api_id": "api",
                        }
                    ],
                }
            ]
        },
        {"items": [{"id": "embed", "name": "Embed", "modality": "embedding"}]},
    )
    assert snapshot["models"][0]["endpoint"]["protocol"] == "messages"
    with pytest.raises(ValueError, match="No supported published chat protocol"):
        project(
            {"data": [{"id": "looks-like-gpt", "label": "Example", "type": "chat"}]}, {"items": []}
        )


def test_messages_stream_tool_json_reaches_dify(llm, monkeypatch):
    events = [
        {"type": "message_start", "message": {"usage": {"input_tokens": 5}}},
        {
            "type": "content_block_start",
            "index": 2,
            "content_block": {"type": "tool_use", "id": "call_1", "name": "lookup", "input": {}},
        },
        {
            "type": "content_block_delta",
            "index": 2,
            "delta": {"type": "input_json_delta", "partial_json": '{"key":'},
        },
        {
            "type": "content_block_delta",
            "index": 2,
            "delta": {"type": "input_json_delta", "partial_json": '"a"}'},
        },
        {
            "type": "message_delta",
            "delta": {"stop_reason": "tool_use"},
            "usage": {"output_tokens": 4},
        },
        {"type": "message_stop"},
    ]
    r = response({})
    r.iter_lines = lambda **kw: iter("data: " + json.dumps(event) for event in events)
    monkeypatch.setattr(requests, "post", lambda *a, **kw: r)
    chunks = list(
        llm._invoke(
            "claude-sonnet-5-5",
            {"api_key": "placeholder", "function_calling_type": "tool_call"},
            [UserPromptMessage(content="Lookup")],
            {},
        )
    )
    calls = [call for chunk in chunks for call in chunk.delta.message.tool_calls]
    assert len(calls) == 1 and calls[0].id == "call_1"
    assert calls[0].function.name == "lookup" and json.loads(calls[0].function.arguments) == {
        "key": "a"
    }
    assert chunks[-1].delta.finish_reason == "tool_calls" and r.was_closed


def test_messages_stream_cancel_closes_the_original_connection(llm, monkeypatch):
    r = response({})
    r.iter_lines = lambda **kw: iter(
        ['data: {"type":"content_block_delta","index":0,"delta":{"type":"text_delta","text":"Hi"}}']
    )
    monkeypatch.setattr(requests, "post", lambda *a, **kw: r)
    stream = llm._invoke(
        "claude-sonnet-5-5", {"api_key": "placeholder"}, [UserPromptMessage(content="Hello")], {}
    )
    next(stream)
    stream.close()
    assert r.was_closed
