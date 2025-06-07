import os
from murf import Murf
from dotenv import load_dotenv
# API client
path = "D:/RGT/Projects/Flet/Tutorial/app.env"
load_dotenv(path)


class MurfTTSClient:
    def __init__(self):
        api_key = os.getenv("murf_api")
        if not api_key:
            raise ValueError("MURF API key not found in environment.")
        
        self.client = Murf(api_key=api_key)
    
    def get_voices(self):
        try:
            return self.client.text_to_speech.get_voices()
        except Exception as e:
            print(f"[MurfTTSClient] Error fetching voices: {e}")
            return []
    
    def generate_audio(self, text, voice_id, mood=None, pitch=0):
        try:
            response = self.client.text_to_speech.generate(
                format="MP3",
                sample_rate=48000.0,
                channel_type="STEREO",
                text=text,
                voice_id=voice_id,
                style=mood,
                pitch=pitch
            )
            return response.audio_file if hasattr(response, "audio_file") else None
        except Exception as e:
            print(f"[MurfTTSClient] Error generating audio: {e}")
            return None