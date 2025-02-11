import logging
import httpx
from collections.abc import Mapping

from dify_plugin import ModelProvider
from dify_plugin.entities.model import ModelType
from dify_plugin.errors.model import CredentialsValidateFailedError

from utils.yaml_updater import update_tts_yaml

logger = logging.getLogger(__name__)

class VoicevoxModelProvider(ModelProvider):
    def validate_provider_credentials(self, credentials: Mapping) -> None:
        """
        Validate provider credentials and update TTS yaml file with current speaker list
        
        :param credentials: provider credentials
        :raises: CredentialsValidateFailedError if validation fails
        """
        try:
            # Check if API base is provided
            if "voicevox_api_base" not in credentials:
                raise CredentialsValidateFailedError("VOICEVOX API Base URL is required")

            # Validate model credentials
            model_instance = self.get_model_instance(ModelType.TTS)
            model_instance.validate_credentials(
                model='voicevox',
                credentials=credentials
            )

        except CredentialsValidateFailedError as ex:
            raise ex
        except Exception as ex:
            logger.exception(
                f"{self.get_provider_schema().provider} credentials validate failed"
            )
            raise ex