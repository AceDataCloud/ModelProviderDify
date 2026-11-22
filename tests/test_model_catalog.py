import json

import dify_plugin  # noqa: F401 - patch network before requests/SSL imports
import pytest
import requests
from dify_plugin.config.config import DifyPluginEnv
from dify_plugin.core.plugin_registration import PluginRegistration
from dify_plugin.entities.model import ModelFeature, ModelType
from dify_plugin.entities.model.message import UserPromptMessage
from dify_plugin.errors.model import InvokeError, InvokeRateLimitError

from scripts.sync_model_catalog import ROOT, project, sync
from tests.test_provider import completion, response


def test_every_published_model_is_in_registered_dify_declaration():
    snapshot = json.loads((ROOT / "models/catalog.json").read_text())
    registration = PluginRegistration(DifyPluginEnv())
    provider = registration.get_model_provider_instance("acedatacloud")
    declared = provider.get_provider_schema().models
    assert {(m.model_type.value, m.model) for m in declared} == {
        (m["type"], m["id"]) for m in snapshot["models"]
    }
    assert not sync(snapshot, check=True)
    for item in snapshot["models"]:
        model = registration.get_model_instance("acedatacloud", ModelType(item["type"]))
        schema = model.get_model_schema(item["id"], {"api_key": "placeholder"})
        assert schema is not None
        assert schema.pricing is None
        assert "context_size" not in {key.value for key in schema.model_properties}
    chat = {m.model for m in declared if m.model_type == ModelType.LLM}
    assert {"gpt-6.2-astra", "gpt-6.2-sol", "gpt-4o-image"} <= chat
    assert not any(m.startswith("text-embedding-") for m in chat)


def test_generator_keeps_chat_image_and_maps_only_declared_capabilities(tmp_path):
    snapshot = project(
        {"data": [{"id": "new-chat", "label": "New", "type": "chat", "capabilities": ["vision"]}]},
        {
            "items": [
                {"id": "embed", "name": "Embed", "modality": "embedding"},
                {"id": "image-only", "name": "Image", "modality": "image"},
            ]
        },
    )
    assert [m["id"] for m in snapshot["models"]] == ["new-chat", "embed"]
    assert snapshot["models"][0]["features"] == ["vision"]
    sync(snapshot, tmp_path)
    assert not sync(snapshot, tmp_path, check=True)
    snapshot["models"][0]["id"] = "replacement-chat"
    sync(snapshot, tmp_path)
    assert not (tmp_path / "models/llm/new-chat.yaml").exists()


@pytest.mark.parametrize("data", [[], [{"id": "duplicate", "label": "A", "type": "chat"}] * 2])
def test_generator_rejects_empty_or_duplicate_catalog(data):
    with pytest.raises(ValueError):
        project({"data": data}, {"items": []})


def test_preset_vision_reaches_the_runtime_but_explicit_custom_settings_win(monkeypatch):
    llm = PluginRegistration(DifyPluginEnv()).get_model_instance("acedatacloud", ModelType.LLM)
    schema = llm.get_model_schema("gpt-6.2-astra", {"api_key": "placeholder"})
    assert ModelFeature.VISION in schema.features
    assert (
        llm._model_credentials("gpt-6.2-astra", {"api_key": "placeholder"})["vision_support"]
        == "support"
    )
    assert (
        llm._model_credentials(
            "gpt-6.2-astra", {"api_key": "placeholder", "vision_support": "no_support"}
        )["vision_support"]
        == "no_support"
    )
    sent = {}

    def post(url, **kwargs):
        sent.update(kwargs["json"])
        return response(completion())

    monkeypatch.setattr(requests, "post", post)
    llm._invoke(
        "gpt-6.2-astra",
        {"api_key": "placeholder"},
        [UserPromptMessage(content="Hello")],
        {},
        stream=False,
    )
    assert sent["model"] == "gpt-6.2-astra"


@pytest.fixture
def embedding():
    return PluginRegistration(DifyPluginEnv()).get_model_instance(
        "acedatacloud", ModelType.TEXT_EMBEDDING
    )


def test_embedding_save_only_reads_catalog(embedding, monkeypatch):
    monkeypatch.setattr(
        requests, "get", lambda *a, **k: response({"data": [{"id": "text-embedding-3-small"}]})
    )
    monkeypatch.setattr(
        requests, "post", lambda *a, **k: pytest.fail("saving generated billable embeddings")
    )
    embedding.validate_credentials("text-embedding-3-small", {"api_key": "placeholder"})


def test_embedding_preserves_full_input_order_usage_and_fixed_destination(embedding, monkeypatch):
    seen = []
    responses = []

    def post(url, **kwargs):
        seen.append((url, kwargs))
        r = response(
            {"data": [{"embedding": [float(len(seen)), 0.25]}], "usage": {"total_tokens": 3}}
        )
        responses.append(r)
        return r

    monkeypatch.setattr(requests, "post", post)
    texts = ["full input " * 9000, "second"]
    result = embedding._invoke(
        "text-embedding-3-small",
        {"api_key": "placeholder", "endpoint_url": "https://example.org"},
        texts,
    )
    assert [call[1]["json"]["input"][0] for call in seen] == texts
    assert all(
        call[0] == "https://api.acedata.cloud/v1/embeddings" and call[1]["allow_redirects"] is False
        for call in seen
    )
    assert result.embeddings == [[1.0, 0.25], [2.0, 0.25]]
    assert result.usage.total_tokens == 6
    assert all(r.was_closed for r in responses)


@pytest.mark.parametrize(
    "body",
    [
        {"data": [], "usage": {"total_tokens": 1}},
        {"data": [{"embedding": [float("nan")]}], "usage": {"total_tokens": 1}},
    ],
)
def test_invalid_embedding_response_is_sanitized_and_closed(embedding, monkeypatch, body):
    r = response(body)
    monkeypatch.setattr(requests, "post", lambda *a, **k: r)
    with pytest.raises(InvokeError, match="invalid embedding response"):
        embedding._invoke("text-embedding-3-small", {"api_key": "placeholder"}, ["private"])
    assert r.was_closed


def test_embedding_rate_limit_is_not_retried(embedding, monkeypatch):
    calls = []
    r = response({"error": "private"}, 429)

    def post(*args, **kwargs):
        calls.append(1)
        return r

    monkeypatch.setattr(requests, "post", post)
    with pytest.raises(InvokeRateLimitError):
        embedding._invoke("text-embedding-3-small", {"api_key": "placeholder"}, ["first", "second"])
    assert calls == [1] and r.was_closed
