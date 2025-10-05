from io import BytesIO
from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs
from elevenlabs.play import play
import os

load_dotenv()

class ElevenLabsService:
    def __init__(self):
        self.client = ElevenLabs(api_key=os.getenv("ELEVENLABS_KEY"))
    
    def stt(self, audio_data):
        transcription = self.client.speech_to_text.convert(
            file=audio_data,
            model_id="scribe_v1", # Model to use, for now only "scribe_v1" is supported
            language_code="eng", # Language of the audio file. If set to None, the model will detect the language automatically.
            diarize=True, # Whether to annotate who is speaking
        )
        return transcription

    def tts(self):
        pass

    def mp3_to_bytes(self, path):
        with open(path, "rb") as f:
            mp3_bytes = f.read()
        return BytesIO(mp3_bytes)

if __name__ == "__main__":
    client = ElevenLabsService()
    print(client.stt(client.mp3_to_bytes("elevenlabs/test.mp3")))

    
