from io import BytesIO
from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs
from elevenlabs.play import play
import logging
import os

load_dotenv()

logging.basicConfig(
    level=logging.INFO,  # Options: DEBUG, INFO, WARNING, ERROR, CRITICAL
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)

logger = logging.getLogger(__name__)

class ElevenLabsService:
    def __init__(self):
        self.client = ElevenLabs(api_key=os.getenv("ELEVENLABS_KEY"))
    
    def stt(self, audio_data):
        print(self.client.speech_to_text)
        transcription = self.client.speech_to_text.convert(
            file=audio_data,
            model_id="scribe_v1", # Model to use, for now only "scribe_v1" is supported
            language_code="eng", # Language of the audio file. If set to None, the model will detect the language automatically.
            diarize=True, # Whether to annotate who is speaking
        )
        return transcription
        logger.info("Starting speech-to-text conversion...")
        try:
            transcription = self.client.speech_to_text.convert(
                file=audio_data,
                model_id="scribe_v1",  # Supported model
                language_code="eng",
                diarize=True
            )
            logger.info("Transcription completed successfully.")
            return transcription
        except Exception as e:
            logger.exception("Error during speech-to-text conversion.")
            raise e

    def tts(self):
        pass

    def mp3_to_bytes(self, path):
        with open(path, "rb") as f:
            mp3_bytes = f.read()
        return BytesIO(mp3_bytes)

if __name__ == "__main__":
    client = ElevenLabsService()
    print(client.stt(client.mp3_to_bytes("elabs/test.mp3")))

    
