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
        audio = bytearray()
        try:
            for chunk in self.client.audio_isolation.convert(audio=audio_data):
                audio.extend(chunk)
            audio = BytesIO(audio)
        except:
            audio = audio_data
        transcription = self.client.speech_to_text.convert(
            file=audio,
            model_id="scribe_v1", # Model to use, for now only "scribe_v1" is supported
            language_code="eng", # Language of the audio file. If set to None, the model will detect the language automatically.
            diarize=True, # Whether to annotate who is speaking
        )
        return transcription

    def tts(self, text):
        audio = self.client.text_to_speech.convert(
            text=text,
            voice_id="iP95p4xoKVk53GoZ742B",
            model_id="eleven_flash_v2_5",
            output_format="mp3_44100_128",
        ) 
        play(audio)

    def mp3_to_bytes(self, path):
        with open(path, "rb") as f:
            mp3_bytes = f.read()
        return BytesIO(mp3_bytes)

if __name__ == "__main__":
    client = ElevenLabsService()
    print(client.stt(client.mp3_to_bytes("elabs/test.mp3")))

    
