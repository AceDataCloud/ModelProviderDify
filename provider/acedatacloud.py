from dify_plugin.interfaces.model import ModelProvider

from models.llm.llm import AceDataCloudLLM


class AceDataCloudProvider(ModelProvider):
    def validate_provider_credentials(self, credentials: dict) -> None:
        """Save one provider key without generating a model response."""
        AceDataCloudLLM.available_model_ids(credentials)
