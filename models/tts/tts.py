"""Published Ace speech synthesis through Dify's TTS interface."""

import requests
from dify_plugin.errors.model import InvokeBadRequestError, InvokeConnectionError, InvokeError
from dify_plugin.interfaces.model.tts_model import TTSModel

from models.audio import AceAudioModel
from models.llm.llm import API_BASE, AceDataCloudLLM


class AceDataCloudTTS(AceAudioModel, TTSModel):
    def get_tts_model_voices(self, model, credentials, language=None):
        # The API publishes one voice list without language-specific restrictions.
        return super().get_tts_model_voices(model, credentials, language=None)

    def _invoke(self, model, tenant_id, credentials, content_text, voice, user=None):
        del tenant_id, user
        configured = AceDataCloudLLM._credentials(credentials)
        if not content_text.strip():
            raise InvokeBadRequestError("Speech synthesis requires non-empty text.")
        voices = {item["value"] for item in self.get_tts_model_voices(model, credentials) or []}
        voice = voice or self._get_model_default_voice(model, credentials)
        if voice not in voices:
            raise InvokeBadRequestError("Choose a published voice for this model.")
        try:
            response = requests.post(
                f"{API_BASE}/audio/speech",
                headers={"Authorization": f"Bearer {configured['api_key']}"},
                json={
                    "model": model,
                    "input": content_text,
                    "voice": voice,
                    "response_format": "mp3",
                },
                timeout=(10, 120),
                allow_redirects=False,
            )
        except requests.RequestException:
            raise InvokeConnectionError("Unable to connect to the Ace Data Cloud API.") from None
        try:
            AceDataCloudLLM._check_response(response)
            if (
                not response.headers.get("Content-Type", "").lower().startswith("audio/")
                or not response.content
            ):
                raise InvokeError("Ace Data Cloud returned an invalid audio response.")
            return response.content
        finally:
            response.close()
