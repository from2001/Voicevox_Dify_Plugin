import concurrent.futures
from collections.abc import Generator
from typing import Optional
from io import BytesIO
from pydub import AudioSegment
import httpx

from dify_plugin import TTSModel
from dify_plugin.errors.model import (
    CredentialsValidateFailedError,
    InvokeBadRequestError,
    InvokeError,
    InvokeServerUnavailableError,
)

class VoicevoxText2SpeechModel(TTSModel):
    """
    Model class for VOICEVOX Text to Speech model.
    """
    def _invoke(
        self,
        model: str,
        credentials: dict,
        content_text: str,
        voice: str,
        user: Optional[str] = None,
        tenant_id: Optional[str] = None,  # Added tenant_id parameter
    ) -> bytes | Generator[bytes, None, None]:
        """
        Invoke text2speech model

        :param model: model name
        :param credentials: model credentials
        :param content_text: text content to be translated
        :param voice: model timbre
        :param user: unique user id
        :param tenant_id: tenant id for multi-tenant setups
        :return: audio data in bytes
        """
        # Validate required credentials
        if "voicevox_api_base" not in credentials:
            raise InvokeBadRequestError("VOICEVOX API Base URL is required")

        # Use default voice if none provided or invalid
        voice_id = voice or self._get_model_default_voice(model, credentials) or '1'

        yield from self._tts_invoke(model=model, credentials=credentials, content_text=content_text, voice=voice_id)

    def validate_credentials(
        self, model: str, credentials: dict, user: Optional[str] = None
    ) -> None:
        """
        Validate credentials for text2speech model

        :param model: model name
        :param credentials: model credentials
        :param user: unique user id
        :raises: CredentialsValidateFailedError if validation fails
        """
        # Check required credentials
        if "voicevox_api_base" not in credentials:
            raise CredentialsValidateFailedError("VOICEVOX API Base URL is required")

        # Test the API endpoint
        try:
            with httpx.Client() as client:
                # Try to get available speakers
                response = client.get(f"{credentials['voicevox_api_base']}/speakers", timeout=10.0)
                response.raise_for_status()
                speakers = response.json()
                
                if not speakers:
                    raise CredentialsValidateFailedError("No speakers available in VOICEVOX API")

                # Get the first available speaker ID
                first_speaker = '1'  # Default to speaker 1
                for speaker in speakers:
                    if 'styles' in speaker and speaker['styles']:
                        first_speaker = str(speaker['styles'][0]['id'])
                        break

                # Test audio synthesis with a simple text
                next(self._tts_invoke(
                    model=model,
                    credentials=credentials,
                    content_text="こんにちは。",
                    voice=first_speaker,
                ))
        except httpx.HTTPError as ex:
            raise CredentialsValidateFailedError(f"Failed to connect to VOICEVOX API: {str(ex)}")
        except Exception as ex:
            raise CredentialsValidateFailedError(f"Failed to validate VOICEVOX credentials: {str(ex)}")

    def _tts_invoke(self, model: str, credentials: dict, content_text: str, voice: str) -> Generator[bytes, None, None]:
        """
        Internal method to handle TTS invocation

        :param model: model name
        :param credentials: model credentials
        :param content_text: text to convert
        :param voice: voice ID
        :return: Generator yielding audio chunks
        """
        try:
            audio_type = self._get_model_audio_type(model, credentials) or 'wav'
            word_limit = self._get_model_word_limit(model, credentials) or 500
            max_workers = self._get_model_workers_limit(model, credentials) or 5
            
            sentences = list(self._split_text_into_sentences(org_text=content_text, max_length=word_limit))
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
                futures = [
                    executor.submit(
                        self._process_sentence,
                        sentence=sentence,
                        voice=voice,
                        api_base=credentials["voicevox_api_base"]
                    ) for sentence in sentences
                ]
                
                for future in futures:
                    result = future.result()
                    if result:
                        buffer = BytesIO()
                        segment = AudioSegment.from_file(BytesIO(result), format=audio_type)
                        segment.export(buffer, format="mp3")
                        buffer.seek(0)
                        yield buffer.read()

        except Exception as ex:
            raise InvokeBadRequestError(f"Failed to process text: {str(ex)}")

    def _process_sentence(self, sentence: str, voice: str, api_base: str) -> Optional[bytes]:
        """
        Process a single sentence

        :param sentence: text to convert
        :param voice: voice ID
        :param api_base: VOICEVOX API base URL
        :return: audio data in bytes
        """
        try:
            with httpx.Client() as client:
                # First get the audio query
                query_resp = client.post(
                    f"{api_base}/audio_query",
                    params={"speaker": voice, "text": sentence.strip()},
                    timeout=30.0
                )
                query_resp.raise_for_status()
                audio_query = query_resp.json()

                # Then synthesize audio
                audio_resp = client.post(
                    f"{api_base}/synthesis",
                    params={"speaker": voice},
                    json=audio_query,
                    timeout=30.0
                )
                audio_resp.raise_for_status()

                return audio_resp.content if isinstance(audio_resp.content, bytes) else None
        except httpx.HTTPError as ex:
            raise InvokeBadRequestError(f"API request failed: {str(ex)}")
        except Exception as ex:
            raise InvokeBadRequestError(f"Failed to process sentence: {str(ex)}")

    @property
    def _invoke_error_mapping(self) -> dict[type[InvokeError], list[type[Exception]]]:
        """
        Map internal exceptions to plugin framework exceptions
        """
        return {
            InvokeServerUnavailableError: [httpx.RequestError, httpx.TimeoutException],
            InvokeBadRequestError: [httpx.HTTPStatusError],
        }