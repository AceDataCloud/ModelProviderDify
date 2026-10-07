"""Ace Data Cloud's fixed Chat Completions endpoint using Dify's message adapters."""

from collections.abc import Generator

import requests
from dify_plugin.errors.model import (
    CredentialsValidateFailedError,
    InvokeAuthorizationError,
    InvokeBadRequestError,
    InvokeConnectionError,
    InvokeError,
    InvokeRateLimitError,
    InvokeServerUnavailableError,
)
from dify_plugin.interfaces.model.openai_compatible import llm as compatible

API_BASE = "https://api.acedata.cloud/v1"


class AceDataCloudLLM(compatible.OAICompatLargeLanguageModel):
    @staticmethod
    def _credentials(credentials: dict) -> dict:
        # Allowlist configuration so callers cannot override the endpoint or headers.
        key = str(credentials.get("api_key", "")).strip()
        if not key:
            raise CredentialsValidateFailedError("An Ace Data Cloud API key is required.")
        limits = {}
        for name, default in (("context_size", 4096), ("max_tokens_to_sample", 1024)):
            try:
                value = int(credentials.get(name, default))
            except (TypeError, ValueError):
                raise CredentialsValidateFailedError(
                    f"{name} must be a positive integer."
                ) from None
            if value <= 0:
                raise CredentialsValidateFailedError(f"{name} must be a positive integer.")
            limits[name] = value
        tool_call = credentials.get("function_calling_type") == "tool_call"
        return {
            "api_key": key,
            "endpoint_url": API_BASE,
            "mode": "chat",
            **limits,
            "function_calling_type": "tool_call" if tool_call else "no_call",
            "stream_function_calling": (
                "supported"
                if tool_call and credentials.get("stream_function_calling") == "supported"
                else "not_supported"
            ),
            "vision_support": (
                "support" if credentials.get("vision_support") == "support" else "no_support"
            ),
        }

    @staticmethod
    def _check_response(response: requests.Response) -> None:
        status = response.status_code
        if status == 200:
            return
        # Do not expose raw upstream bodies, which can contain request data.
        errors = {
            400: (InvokeBadRequestError, "Check the model, parameters and API key permissions."),
            401: (InvokeAuthorizationError, "Check your Ace Data Cloud API key."),
            403: (
                InvokeAuthorizationError,
                "Access denied. Check model access and content policy.",
            ),
            404: (InvokeBadRequestError, "The requested model or endpoint is unavailable."),
            429: (InvokeRateLimitError, "Rate limit reached. Retry later."),
        }
        error, hint = errors.get(
            status, (InvokeServerUnavailableError, "The model service is temporarily unavailable.")
        )
        raise error(f"Ace Data Cloud API returned HTTP {status}. {hint}")

    def get_customizable_model_schema(self, model: str, credentials: dict):
        schema = super().get_customizable_model_schema(model, self._credentials(credentials))
        # No static price claim: actual Credit charges and the user's package rate vary.
        schema.pricing = None
        return schema

    def validate_credentials(self, model: str, credentials: dict) -> None:
        credentials = self._credentials(credentials)
        try:
            # Read-only auth/model check: saving credentials never generates paid output.
            with requests.get(
                f"{API_BASE}/models",
                headers={"Authorization": f"Bearer {credentials['api_key']}"},
                timeout=(10, 30),
                allow_redirects=False,
            ) as response:
                self._check_response(response)
                available = {item["id"] for item in response.json()["data"]}
                if model not in available:
                    raise CredentialsValidateFailedError(
                        "Model ID not found. Use an exact ID from the Ace Data Cloud model catalog."
                    )
        except CredentialsValidateFailedError:
            raise
        except (InvokeError, requests.RequestException, ValueError, KeyError, TypeError):
            raise CredentialsValidateFailedError(
                "Unable to validate this model. Check the API key, model access and network connection."
            ) from None

    def _invoke(
        self,
        model,
        credentials,
        prompt_messages,
        model_parameters,
        tools=None,
        stop=None,
        stream=True,
        user=None,
    ):
        credentials = self._credentials(credentials)
        params = {
            k: v
            for k, v in model_parameters.items()
            if k in {"temperature", "top_p", "max_tokens", "frequency_penalty", "presence_penalty"}
        }
        payload = {
            **params,
            "model": model,
            "messages": [
                self._convert_prompt_message_to_dict(m, credentials) for m in prompt_messages
            ],
            "stream": stream,
        }
        if tools:
            if credentials["function_calling_type"] != "tool_call":
                raise InvokeBadRequestError("Enable tool calling for a model that supports it.")
            payload["tools"] = [{"type": "function", "function": t.model_dump()} for t in tools]
            payload["tool_choice"] = "auto"
        if stop:
            payload["stop"] = stop
        if stream:
            payload["stream_options"] = {"include_usage": True}
        try:
            response = requests.post(
                f"{API_BASE}/chat/completions",
                headers={"Authorization": f"Bearer {credentials['api_key']}"},
                json=payload,
                stream=stream,
                timeout=(10, 120),
                allow_redirects=False,
            )
        except requests.RequestException:
            raise InvokeConnectionError("Unable to connect to the Ace Data Cloud API.") from None
        try:
            self._check_response(response)
            response.encoding = "utf-8"
            if stream:
                return self._stream(model, credentials, response, prompt_messages)
            return self._handle_generate_response(model, credentials, response, prompt_messages)
        except InvokeError:
            response.close()
            raise
        except (requests.RequestException, ValueError, KeyError, TypeError):
            response.close()
            raise InvokeError("Ace Data Cloud returned an invalid model response.") from None
        finally:
            if not stream:
                response.close()

    def _stream(self, model, credentials, response, prompt_messages) -> Generator:
        try:
            for chunk in self._handle_generate_stream_response(
                model, credentials, response, prompt_messages
            ):
                if chunk.delta.finish_reason == "Non-JSON encountered.":
                    raise InvokeError("Ace Data Cloud returned an invalid response stream.")
                yield chunk
        except (requests.RequestException, ValueError, KeyError, TypeError):
            raise InvokeError(
                "The Ace Data Cloud response stream was interrupted or invalid."
            ) from None
        finally:
            response.close()
