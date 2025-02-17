from collections.abc import Generator
from typing import Any
from typing import Optional
from pydub import AudioSegment
import io
from dify_plugin.entities import I18nObject
from dify_plugin.entities.model import ModelType, ModelPropertyKey, AIModelEntity

from dify_plugin import Tool
from dify_plugin import TTSModel
from dify_plugin.entities.tool import ToolInvokeMessage
from dify_plugin.errors.model import (
    CredentialsValidateFailedError,
    InvokeBadRequestError,
    InvokeError,
    InvokeServerUnavailableError,
)
import httpx

class VoicevoxToolTool(Tool):

    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        """
        invoke tool
        """
        print("_invoke called")
        content = tool_parameters.get("content", "")
        if not content:
            yield self.create_text_message("Invalid parameter content")
        style_id = tool_parameters.get("style_id", "")
        if not style_id:
            yield self.create_text_message("Invalid parameter voice id")

        try:
            data = self._tts(content, style_id)
            yield self.create_blob_message(blob=data, meta={"mime_type": f"audio/mp3"})
        except Exception as e:
            yield self.create_text_message(f"Text to speech service error, please check the network; error: {e}")
        
    def _tts(self, content: str, style_id: str) -> bytes:
        api_base = self.runtime.credentials.get("api_base")

        # If the text is longer than max_length characters, split it into sentences
        sentences = list(TTSModel._split_text_into_sentences(org_text=content, max_length=500, pattern=r"[。.!?]+|\n"))
        # Remove trailing newline characters
        sentences = [sentence.rstrip("\n") for sentence in sentences]
        
        combined_audio = None
        for sentence in sentences:
            wav_binary = self._process_sentence(sentence, style_id, api_base)
            segment = AudioSegment.from_file(io.BytesIO(wav_binary), format="wav")
            combined_audio = segment if combined_audio is None else combined_audio + segment
        buffer = io.BytesIO()
        combined_audio.export(buffer, format="mp3")
        result_mp3 = buffer.getvalue()
        return result_mp3

    def _process_sentence(self, sentence: str, style_id: str, api_base: str) -> Optional[bytes]:
        print("_process_sentence called")   
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
                    params={"speaker": style_id, "text": sentence.strip()},
                    timeout=30.0
                )
                query_resp.raise_for_status()
                audio_query = query_resp.json()

                # Then synthesize audio
                audio_resp = client.post(
                    f"{api_base}/synthesis",
                    params={"speaker": style_id},
                    json=audio_query,
                    timeout=30.0
                )
                audio_resp.raise_for_status()

                return audio_resp.content if isinstance(audio_resp.content, bytes) else None
        except httpx.HTTPError as ex:
            raise InvokeBadRequestError(f"API request failed: {str(ex)}")
        except Exception as ex:
            raise InvokeBadRequestError(f"Failed to process sentence: {str(ex)}")
        
