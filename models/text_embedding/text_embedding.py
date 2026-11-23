"""Ace embeddings through Dify's text-embedding interface, without hidden truncation."""

import math

import requests
from dify_plugin.entities.model import EmbeddingInputType
from dify_plugin.entities.model.text_embedding import TextEmbeddingResult
from dify_plugin.errors.model import (
    CredentialsValidateFailedError,
    InvokeConnectionError,
    InvokeError,
)
from dify_plugin.interfaces.model.openai_compatible.text_embedding import OAICompatEmbeddingModel

from models.llm.llm import API_BASE, AceDataCloudLLM


class AceDataCloudEmbedding(OAICompatEmbeddingModel):
    def validate_credentials(self, model: str, credentials: dict) -> None:
        # The SDK default embeds a ping. Saving credentials must stay read-only.
        if model not in AceDataCloudLLM.available_model_ids(credentials):
            raise CredentialsValidateFailedError(
                "Model ID not found in the Ace Data Cloud catalog."
            )

    def get_customizable_model_schema(self, model: str, credentials: dict):
        schema = super().get_customizable_model_schema(model, credentials)
        schema.pricing = None
        return schema

    def _invoke(
        self,
        model: str,
        credentials: dict,
        texts: list[str],
        user: str | None = None,
        input_type: EmbeddingInputType = EmbeddingInputType.DOCUMENT,
    ) -> TextEmbeddingResult:
        del user, input_type
        configured = AceDataCloudLLM._credentials(credentials)
        embeddings = []
        tokens = 0
        # One text per call is a conservative batching policy, not an asserted
        # upstream batch/context limit. Never silently truncate or retry input.
        for text in texts:
            try:
                response = requests.post(
                    f"{API_BASE}/embeddings",
                    headers={"Authorization": f"Bearer {configured['api_key']}"},
                    json={"model": model, "input": [text], "encoding_format": "float"},
                    timeout=(10, 120),
                    allow_redirects=False,
                )
            except requests.RequestException:
                raise InvokeConnectionError(
                    "Unable to connect to the Ace Data Cloud API."
                ) from None
            try:
                AceDataCloudLLM._check_response(response)
                payload = response.json()
                if len(payload["data"]) != 1:
                    raise ValueError("Unexpected embedding count")
                vector = payload["data"][0]["embedding"]
                if (
                    not isinstance(vector, list)
                    or not vector
                    or any(
                        isinstance(value, bool)
                        or not isinstance(value, (int, float))
                        or not math.isfinite(value)
                        for value in vector
                    )
                ):
                    raise ValueError("Invalid embedding")
                used = payload["usage"]["total_tokens"]
                if isinstance(used, bool) or not isinstance(used, int) or used < 0:
                    raise ValueError("Invalid usage")
                embeddings.append(vector)
                tokens += used
            except (requests.RequestException, ValueError, KeyError, TypeError):
                raise InvokeError(
                    "Ace Data Cloud returned an invalid embedding response."
                ) from None
            finally:
                response.close()
        return TextEmbeddingResult(
            model=model,
            embeddings=embeddings,
            usage=self._calc_response_usage(model, credentials, tokens),
        )
