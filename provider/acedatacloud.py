from dify_plugin.interfaces.model import ModelProvider


class AceDataCloudProvider(ModelProvider):
    def validate_provider_credentials(self, credentials: dict) -> None:
        """This provider validates credentials separately for each custom model."""
