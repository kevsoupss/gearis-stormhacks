import struct, wave, time, queue, os
import sounddevice as sd
import pvporcupine
import webrtcvad
import requests

from dotenv import load_dotenv
load_dotenv()

pico_api_key = os.getenv("PICO_API_KEY")
WAKEWORDS = ["jarvis"]  # built-in keywords: "picovoice", "bumblebee", etc.
SAMPLE_RATE = 16000
FRAME_LENGTH = 512      # Porcupine expects 512 samples @16kHz (~32ms)
OUTPUT_WAV = "utterance.wav"

# VAD / capture tuning
VAD_AGGRESSIVENESS = 2      # 0..3 (higher = more aggressive)
VAD_CHUNK_MS = 20           # WebRTC VAD supports 10/20/30ms
END_SILENCE_SEC = 1.0       # stop after this much continuous silence
MAX_UTTERANCE_SEC = 12.0    # safety cap so it never records forever

def save_wav(raw_bytes: bytes, path: str, samplerate=SAMPLE_RATE):
    with wave.open(path, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)  # int16
        wf.setframerate(samplerate)
        wf.writeframes(raw_bytes)
        files = {"audio": ("utterance.wav", open("utterance.wav", "rb"), "audio/wav")}
        response = requests.post("http://localhost:8000/api/upload-audio?toggle_voice=true", files=files)
        print("Server response:", response.status_code, response.text)

def simple_intent_router(text: str):
    t = text.lower()
    if "set timer" in t or "timer" in t:
        print("→ Intent: set_timer(duration=5m)")
    elif "weather" in t:
        print("→ Intent: get_weather(Vancouver)")
    else:
        print("→ Intent: fallback / smalltalk")

def transcribe_stub(path: str) -> str:
    print(f"[stub] Would transcribe {path} here.")
    return "set a five minute timer"

def main():
    porcupine = pvporcupine.create(
        keywords=WAKEWORDS,
        access_key=pico_api_key,
    )

    # --- Audio stream set-up (16k, int16, mono) ---
    audio_q = queue.Queue()

    def on_audio(indata, frames, time_info, status):
        if status:
            pass  # you could log over/underflows
        audio_q.put(bytes(indata))  # int16 bytes

    stream = sd.InputStream(
        channels=1,
        samplerate=SAMPLE_RATE,
        dtype='int16',
        blocksize=FRAME_LENGTH,
        callback=on_audio,
    )
    stream.start()
    print("Listening for wake word… (say 'jarvis')")

    # --- VAD init ---
    vad = webrtcvad.Vad(VAD_AGGRESSIVENESS)
    vad_chunk_bytes = int(SAMPLE_RATE * (VAD_CHUNK_MS / 1000.0)) * 2  # bytes (int16)

    try:
        leftover = b""
        capturing = False
        captured = bytearray()
        vad_buf = b""
        last_voice_time = 0.0
        start_time = 0.0

        while True:
            block = audio_q.get()  # grab mic bytes
            leftover += block

            # Always feed Porcupine with exact 512-sample frames
            while len(leftover) >= FRAME_LENGTH * 2:
                chunk = leftover[:FRAME_LENGTH * 2]
                leftover = leftover[FRAME_LENGTH * 2:]

                # Porcupine processing
                pcm = struct.unpack_from("h" * FRAME_LENGTH, chunk)
                result = porcupine.process(pcm)

                if not capturing:
                    # Still in wake-word mode
                    if result >= 0:
                        print("Wake word detected! Speak…")
                        capturing = True
                        captured = bytearray()
                        vad_buf = b""
                        last_voice_time = time.time()
                        start_time = last_voice_time
                        # (Optional) seed a tiny pre-roll if you keep a ring buffer
                        # For now, just start fresh after trigger
                        # Fall through to capture this chunk as well
                        captured.extend(chunk)
                        vad_buf += chunk
                else:
                    # Already capturing speech
                    captured.extend(chunk)
                    vad_buf += chunk

                # While we have 20ms (or chosen VAD_CHUNK_MS) available, run VAD
                while capturing and len(vad_buf) >= vad_chunk_bytes:
                    vad_chunk = vad_buf[:vad_chunk_bytes]
                    vad_buf = vad_buf[vad_chunk_bytes:]
                    if vad.is_speech(vad_chunk, SAMPLE_RATE):
                        last_voice_time = time.time()

                # Check for end-of-speech or timeout
                if capturing:
                    now = time.time()
                    if (now - last_voice_time) >= END_SILENCE_SEC:
                        print("🛑 End of speech detected.")
                        save_wav(bytes(captured), OUTPUT_WAV)
                        text = transcribe_stub(OUTPUT_WAV)
                        
                        print("You said:", text)
                        simple_intent_router(text)
                        print("Listening for wake word…")
                        capturing = False
                        captured.clear()
                        vad_buf = b""
                    elif (now - start_time) >= MAX_UTTERANCE_SEC:
                        print("⏱️ Max utterance reached; stopping capture.")
                        save_wav(bytes(captured), OUTPUT_WAV)
                        text = transcribe_stub(OUTPUT_WAV)
                        print("You said:", text)
                        simple_intent_router(text)
                        print("Listening for wake word…")
                        capturing = False
                        captured.clear()
                        vad_buf = b""

    except KeyboardInterrupt:
        pass
    finally:
        stream.stop(); stream.close()
        porcupine.delete()

if __name__ == "__main__":
    main()
