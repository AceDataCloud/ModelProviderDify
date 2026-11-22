"""Published Ace audio transcription through Dify's speech-to-text interface."""

from pathlib import Path

import requests
from dify_plugin.errors.model import InvokeBadRequestError, InvokeConnectionError, InvokeError
from dify_plugin.interfaces.model.speech2text_model import Speech2TextModel

from models.audio import AceAudioModel
from models.llm.llm import API_BASE, AceDataCloudLLM


class AceDataCloudSpeech2Text(AceAudioModel, Speech2TextModel):
    def _invoke(self, model, credentials, file, user=None):
        del user
        configured = AceDataCloudLLM._credentials(credentials)
        # The published transcription API explicitly limits files to 25 MB.
        content = file.read(25 * 1024 * 1024 + 1)
        if not content or len(content) > 25 * 1024 * 1024:
            raise InvokeBadRequestError("Provide an audio file no larger than 25 MB.")
        filename = Path(str(getattr(file, "name", "audio.wav"))).name
        try:
            response = requests.post(
                f"{API_BASE}/audio/transcriptions",
                headers={"Authorization": f"Bearer {configured['api_key']}"},
                data={"model": model, "response_format": "json", "stream": "false"},
                files={"file": (filename, content)},
                timeout=(10, 120),
                allow_redirects=False,
            )
        except requests.RequestException:
            raise InvokeConnectionError("Unable to connect to the Ace Data Cloud API.") from None
        try:
            AceDataCloudLLM._check_response(response)
            text = response.json()["text"]
            if not isinstance(text, str):
                raise TypeError("Invalid transcript")
            return text
        except (requests.RequestException, ValueError, KeyError, TypeError):
            raise InvokeError(
                "Ace Data Cloud returned an invalid transcription response."
            ) from None
        finally:
            response.close()
