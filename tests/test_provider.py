import json

import dify_plugin  # noqa: F401 - patch network before requests/SSL imports
import pytest
import requests
from dify_plugin.entities.model import ModelFeature
from dify_plugin.entities.model.message import (
    AssistantPromptMessage,
    PromptMessageTool,
    ToolPromptMessage,
    UserPromptMessage,
)
from dify_plugin.errors.model import (
    CredentialsValidateFailedError,
    InvokeAuthorizationError,
    InvokeBadRequestError,
    InvokeError,
    InvokeRateLimitError,
    InvokeServerUnavailableError,
)

from models.llm.llm import API_BASE, AceDataCloudLLM


@pytest.fixture
def llm():
    return AceDataCloudLLM([])


def response(body, status=200):
    r = requests.Response()
    r.status_code = status
    r._content = json.dumps(body).encode()
    r.close = lambda: setattr(r, "was_closed", True)
    r.was_closed = False
    return r


def completion(content="OK", tool_calls=None):
    return {
        "id": "test",
        "model": "gpt-4.1-mini",
        "choices": [
            {
                "message": {"role": "assistant", "content": content, "tool_calls": tool_calls},
                "finish_reason": "stop",
            }
        ],
        "usage": {"prompt_tokens": 7, "completion_tokens": 2, "total_tokens": 9},
    }


def test_fixed_endpoint_and_conservative_capabilities(llm):
    c = llm._credentials(
        {
            "api_key": "test-placeholder",
            "endpoint_url": "https://example.org",
            "extra_headers": {"Authorization": "other"},
            "vision_support": "support",
        }
    )
    assert c["endpoint_url"] == API_BASE and "extra_headers" not in c
    schema = llm.get_customizable_model_schema("gpt-4.1-mini", {"api_key": "test-placeholder"})
    assert not schema.features and schema.pricing is None
    assert (
        ModelFeature.STREAM_TOOL_CALL
        not in llm.get_customizable_model_schema(
            "gpt-4.1-mini", {"api_key": "test-placeholder", "stream_function_calling": "supported"}
        ).features
    )


@pytest.mark.parametrize(
    "credentials",
    [{}, {"api_key": "x", "context_size": "oops"}, {"api_key": "x", "max_tokens_to_sample": 0}],
)
def test_invalid_configuration(llm, credentials):
    with pytest.raises(CredentialsValidateFailedError):
        llm._credentials(credentials)


def test_validation_is_read_only_and_rejects_unknown_model(llm, monkeypatch):
    calls = []

    def get(url, **kwargs):
        calls.append((url, kwargs))
        return response({"data": [{"id": "gpt-4.1-mini"}]})

    monkeypatch.setattr(requests, "get", get)
    monkeypatch.setattr(
        requests, "post", lambda *a, **k: pytest.fail("validation generated output")
    )
    llm.validate_credentials("gpt-4.1-mini", {"api_key": "test-placeholder"})
    assert calls[0][0] == API_BASE + "/models"
    assert calls[0][1]["allow_redirects"] is False
    with pytest.raises(CredentialsValidateFailedError):
        llm.validate_credentials("missing", {"api_key": "test-placeholder"})


@pytest.mark.parametrize(
    "status,error",
    [
        (400, InvokeBadRequestError),
        (401, InvokeAuthorizationError),
        (403, InvokeAuthorizationError),
        (429, InvokeRateLimitError),
        (503, InvokeServerUnavailableError),
    ],
)
def test_errors_are_classified_without_raw_body(llm, monkeypatch, status, error):
    r = response({"error": "private-request-data"}, status)
    monkeypatch.setattr(requests, "post", lambda *a, **k: r)
    with pytest.raises(error) as exc:
        llm._invoke(
            "gpt-4.1-mini",
            {"api_key": "test-placeholder"},
            [UserPromptMessage(content="Hello")],
            {},
            stream=False,
        )
    assert "private-request-data" not in str(exc.value)
    assert r.was_closed


def test_non_stream_tool_round_trip_and_usage(llm, monkeypatch):
    tool = {
        "id": "call_1",
        "type": "function",
        "function": {"name": "get_value", "arguments": '{"key":"a"}'},
    }
    r = response(completion(None, [tool]))
    sent = {}

    def post(url, **kwargs):
        sent.update(url=url, **kwargs)
        return r

    monkeypatch.setattr(requests, "post", post)
    result = llm._invoke(
        "gpt-4.1-mini",
        {"api_key": "test-placeholder", "function_calling_type": "tool_call"},
        [UserPromptMessage(content="Lookup a")],
        {"max_tokens": 64},
        tools=[
            PromptMessageTool(
                name="get_value",
                description="lookup",
                parameters={"type": "object", "properties": {}},
            )
        ],
        stream=False,
        user="private-user",
    )
    assert result.usage.prompt_tokens == 7
    assert result.message.tool_calls[0].function.name == "get_value"
    assert "user" not in sent["json"]
    assert sent["url"] == API_BASE + "/chat/completions"
    assert sent["allow_redirects"] is False
    assert sent["json"]["tools"][0]["type"] == "function"
    assert r.was_closed
    assistant = AssistantPromptMessage(content=None, tool_calls=result.message.tool_calls)
    assert (
        llm._convert_prompt_message_to_dict(
            assistant, llm._credentials({"api_key": "x", "function_calling_type": "tool_call"})
        )["tool_calls"][0]["id"]
        == "call_1"
    )
    assert (
        llm._convert_prompt_message_to_dict(
            ToolPromptMessage(tool_call_id="call_1", content="42"),
            {"function_calling_type": "tool_call"},
        )["tool_call_id"]
        == "call_1"
    )


def test_stream_chunks_usage_and_connection_close(llm, monkeypatch):
    r = response({})
    chunks = [
        {"choices": [{"delta": {"content": "OK"}, "finish_reason": None}]},
        {"choices": [{"delta": {}, "finish_reason": "stop"}]},
        {"choices": [], "usage": {"prompt_tokens": 7, "completion_tokens": 2, "total_tokens": 9}},
    ]
    r.iter_lines = lambda **kw: iter(["data: " + json.dumps(x) for x in chunks] + ["data: [DONE]"])
    sent = {}

    def post(url, **kw):
        sent.update(kw)
        return r

    monkeypatch.setattr(requests, "post", post)
    result = list(
        llm._invoke(
            "gpt-4.1-mini",
            {"api_key": "test-placeholder"},
            [UserPromptMessage(content="Hello")],
            {},
            stream=True,
        )
    )
    assert sent["json"]["stream_options"] == {"include_usage": True}
    assert "".join(x.delta.message.content or "" for x in result) == "OK"
    assert result[-1].delta.usage.prompt_tokens == 7
    assert r.was_closed


def test_stream_error_does_not_leak_body(llm, monkeypatch):
    r = response({})
    r.iter_lines = lambda **kw: iter(['data: {"error": "private-request-data"}'])
    monkeypatch.setattr(requests, "post", lambda *a, **k: r)
    with pytest.raises(InvokeError) as exc:
        list(llm._invoke("gpt-4.1-mini", {"api_key": "x"}, [UserPromptMessage(content="Hi")], {}))
    assert "private-request-data" not in str(exc.value)
    assert r.was_closed


def test_stream_cancel_closes_connection(llm, monkeypatch):
    r = response({})
    r.iter_lines = lambda **kw: iter(['data: {"choices":[{"delta":{"content":"Hello"}}]}'])
    monkeypatch.setattr(requests, "post", lambda *a, **k: r)
    stream = llm._invoke("gpt-4.1-mini", {"api_key": "x"}, [UserPromptMessage(content="Hi")], {})
    next(stream)
    stream.close()
    assert r.was_closed


def test_non_json_stream_fails(llm, monkeypatch):
    r = response({})
    r.iter_lines = lambda **kw: iter(["<html>not a completion</html>"])
    monkeypatch.setattr(requests, "post", lambda *a, **k: r)
    with pytest.raises(InvokeError):
        list(llm._invoke("gpt-4.1-mini", {"api_key": "x"}, [UserPromptMessage(content="Hi")], {}))
    assert r.was_closed


def test_plugin_registration_loads_provider_and_model():
    from dify_plugin.config.config import DifyPluginEnv
    from dify_plugin.core.plugin_registration import PluginRegistration
    from dify_plugin.entities.model import ModelType

    registration = PluginRegistration(DifyPluginEnv())
    assert registration.get_model_provider_instance("acedatacloud") is not None
    model = registration.get_model_instance("acedatacloud", ModelType.LLM)
    assert (
        model.get_customizable_model_schema("gpt-4.1-mini", {"api_key": "test"}).model
        == "gpt-4.1-mini"
    )
