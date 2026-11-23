"""Shared read-only credentials and safe errors for the published audio interfaces."""

from dify_plugin.errors.model import (
    CredentialsValidateFailedError,
    InvokeAuthorizationError,
    InvokeBadRequestError,
    InvokeConnectionError,
    InvokeError,
    InvokeRateLimitError,
    InvokeServerUnavailableError,
)

from models.llm.llm import AceDataCloudLLM


class AceAudioModel:
    def validate_credentials(self, model: str, credentials: dict) -> None:
        if self.get_model_schema(model) is None:
            raise CredentialsValidateFailedError("Unknown model for this audio interface.")
        # Audio models are published separately from /v1/models.data. The latter
        # authenticates the key without generating audio; it is not a type list.
        AceDataCloudLLM.available_model_ids(credentials)

    @property
    def _invoke_error_mapping(self):
        return {
            error: [error]
            for error in (
                InvokeAuthorizationError,
                InvokeBadRequestError,
                InvokeConnectionError,
                InvokeRateLimitError,
                InvokeServerUnavailableError,
                InvokeError,
            )
        }
