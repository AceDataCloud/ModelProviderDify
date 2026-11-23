import io

import dify_plugin  # noqa: F401 - patch network before requests/SSL imports
import pytest
import requests
from dify_plugin.config.config import DifyPluginEnv
from dify_plugin.core.plugin_registration import PluginRegistration
from dify_plugin.entities.model import ModelType
from dify_plugin.errors.model import InvokeBadRequestError, InvokeError, InvokeRateLimitError

from tests.test_provider import response


@pytest.fixture
def registration():
    return PluginRegistration(DifyPluginEnv())


@pytest.mark.parametrize(
    "kind,expected",
    [
        (ModelType.TTS, {"tts-1", "tts-1-hd"}),
        (ModelType.SPEECH2TEXT, {"whisper-1", "gpt-transcribe"}),
    ],
)
def test_audio_models_are_native_and_credentials_never_generate(
    registration, monkeypatch, kind, expected
):
    model = registration.get_model_instance("acedatacloud", kind)
    assert {item.model for item in model.predefined_models()} == expected
    # Audio IDs are intentionally not in this OpenAI chat/embedding discovery response.
    monkeypatch.setattr(
        requests, "get", lambda *a, **k: response({"data": [{"id": "gpt-6.2-astra"}]})
    )
    monkeypatch.setattr(
        requests, "post", lambda *a, **k: pytest.fail("audio credential Save generated output")
    )
    for item in expected:
        model.validate_credentials(item, {"api_key": "placeholder"})


def test_tts_uses_documented_voices_and_returns_audio_bytes(registration, monkeypatch):
    model = registration.get_model_instance("acedatacloud", ModelType.TTS)
    assert {v["value"] for v in model.get_tts_model_voices("tts-1", {}, language="en-US")} == {
        "alloy",
        "echo",
        "fable",
        "onyx",
        "nova",
        "shimmer",
    }
    r = response({})
    r._content = b"ID3offline-audio-fixture"
    r.headers["Content-Type"] = "audio/mpeg"
    sent = {}

    def post(url, **kwargs):
        sent.update(url=url, **kwargs)
        return r

    monkeypatch.setattr(requests, "post", post)
    result = model._invoke(
        "tts-1-hd",
        "private-tenant",
        {"api_key": "placeholder", "endpoint_url": "https://example.org"},
        "Hello",
        "nova",
        "private-user",
    )
    assert result == r.content and r.was_closed
    assert sent["url"] == "https://api.acedata.cloud/v1/audio/speech"
    assert sent["json"] == {
        "model": "tts-1-hd",
        "input": "Hello",
        "voice": "nova",
        "response_format": "mp3",
    }
    assert sent["allow_redirects"] is False


def test_tts_rejects_an_error_body_masquerading_as_audio(registration, monkeypatch):
    model = registration.get_model_instance("acedatacloud", ModelType.TTS)
    r = response({"error": "private"})
    r.headers["Content-Type"] = "application/json"
    monkeypatch.setattr(requests, "post", lambda *a, **k: r)
    with pytest.raises(InvokeError, match="invalid audio response"):
        model._invoke("tts-1", "tenant", {"api_key": "placeholder"}, "Hello", "alloy")
    assert r.was_closed


def test_transcription_preserves_audio_and_uses_multipart_contract(registration, monkeypatch):
    model = registration.get_model_instance("acedatacloud", ModelType.SPEECH2TEXT)
    audio = io.BytesIO(b"complete offline audio")
    audio.name = "/local/private-directory/recording.webm"
    r = response({"text": "A complete transcript"})
    sent = {}

    def post(url, **kwargs):
        sent.update(url=url, **kwargs)
        return r

    monkeypatch.setattr(requests, "post", post)
    result = model._invoke("gpt-transcribe", {"api_key": "placeholder"}, audio, "private-user")
    assert result == "A complete transcript" and r.was_closed
    assert sent["url"] == "https://api.acedata.cloud/v1/audio/transcriptions"
    assert sent["files"] == {"file": ("recording.webm", b"complete offline audio")}
    assert sent["data"] == {"model": "gpt-transcribe", "response_format": "json", "stream": "false"}
    assert sent["allow_redirects"] is False


def test_transcription_rejects_oversize_without_paid_request(registration, monkeypatch):
    model = registration.get_model_instance("acedatacloud", ModelType.SPEECH2TEXT)
    monkeypatch.setattr(
        requests, "post", lambda *a, **k: pytest.fail("oversize file was submitted")
    )
    with pytest.raises(InvokeBadRequestError, match="25 MB"):
        model._invoke(
            "whisper-1", {"api_key": "placeholder"}, io.BytesIO(b"x" * (25 * 1024 * 1024 + 1))
        )


def test_audio_rate_limit_is_preserved_without_retry(registration, monkeypatch):
    model = registration.get_model_instance("acedatacloud", ModelType.SPEECH2TEXT)
    calls = []
    r = response({"error": "private"}, 429)

    def post(*args, **kwargs):
        calls.append(1)
        return r

    monkeypatch.setattr(requests, "post", post)
    with pytest.raises(InvokeRateLimitError):
        model._invoke("whisper-1", {"api_key": "placeholder"}, io.BytesIO(b"audio"))
    assert calls == [1] and r.was_closed
