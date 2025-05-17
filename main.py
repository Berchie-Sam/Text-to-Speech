# Imports
import flet as ft
import requests
import os
import logging
from murf import Murf
from dotenv import load_dotenv

# API client
path = "D:/RGT/Projects/Flet/Tutorial/app.env"
load_dotenv(path)
API_KEY = os.getenv("murf_api")
# print(API_KEY)
 
client = Murf(api_key=API_KEY)

voices = client.text_to_speech.get_voices()
# for voice in voices:
    # print(f"Voice ID: {voice.voice_id}, Name: {voice.display_name}")
    # if voice.voice_id == "en-US-natalie": 
    #     print(f"Voice ID: {voice.voice_id}, Name: {voice.display_name}")
    # print(f"Languages: {voice.display_language}, Moods: {voice.available_styles}")

# Voice Settings
VOICE_MOODS = {
    "Miles": {
        "voice_id": "en-US-miles",
        "moods": [
            'Conversational', 'Promo', 'Sports Commentary', 
            'Narration', 'Newscast', 'Sad', 'Angry', 
            'Calm', 'Terrified', 'Inspirational', 'Pirate'
            ]
    },
    
    "Shane": {
        "voice_id": "en-AU-shane",
        "moods": ['Conversational', 'Narration']    
    },
    
    "Natalie": {
        "voice_id": "en-US-natalie",
        "moods": [
            'Promo', 'Narration', 'Newscast Formal', 
            'Meditative', 'Sad', 'Angry', 'Conversational', 
            'Newscast Casual', 'Furious', 'Sorrowful', 
            'Terrified', 'Inspirational']
    }
}

# Flet App
def main(page: ft.Page):
    page.title = "AI friend"
    page.padding = 40
    page.bgcolor = "#1E1E2F"
    
    # Create UI widgets
    title = ft.Text(
        page.title, size=42, 
        weight=ft.FontWeight.BOLD, color="#FFD700")
    
    txt_input = ft.TextField(
        label="Enter some text here...",
        width=350,
        bgcolor="#2A2A3B",
        color="#ffffff",
        border_radius=15,
        border_color="#FFD700"
    )
    
    # voice_selection
    voice_selection = ft.Dropdown(
        label="Select Voice",
        options = [
            ft.dropdown.Option(voice) for voice in VOICE_MOODS.keys()
        ],
        width=350,
        bgcolor="#2A2A3B",
        color="#ffffff",
        value="Miles"
    )   
     
    # mood_selection
    mood_selection = ft.Dropdown(
        label="Choose Mood",
        width=350,
        bgcolor="#2A2A3B",
        color="#ffffff",
    )
    
    def update_moods(e=None):
        selected_voice = voice_selection.value
        mood_selection.options = [
            ft.dropdown.Option(mood) 
            for mood in VOICE_MOODS.get(selected_voice, {}).get("moods", [])
        ]
        mood_selection.value = mood_selection.options[0].text if mood_selection.options else None
        logging.info("Selected mood: {mood_selection}")
        page.update()
        
    voice_selection.on_change = update_moods
    update_moods()
    
    voice_speed = ft.Slider(
        min=-30, max=30,
        value=0, divisions=10,
        label="{value}%",active_color="#FFD700"
    )
    
    # Generate AI voice
    def generate_audio():
        selected_voice = voice_selection.value
        voice_id = VOICE_MOODS.get(selected_voice, {}).get("voice_id")
        if not txt_input.value.strip():
            print("ERROR, you need some text...")
            return None
        try:
            response = client.text_to_speech.generate(
                format="MP3",
                sample_rate=48000.0,
                channel_type="STEREO",
                text=txt_input.value,
                voice_id=voice_id,
                style=mood_selection.value,
                pitch=voice_speed.value
            )
            return response.audio_file if hasattr(response, "audio_file") else None
        except Exception as e:
            print(f"Error: {e}")
            return None
        
        
    def save_and_play():
        audio_url = generate_audio()
        if not audio_url:
            print("Error: no audio found..")
            return
        
        try:
            response = requests.get(audio_url, stream=True)
            if response.status_code == 200:
                file_path = os.path.abspath("audio.mp3")
                with open(file_path, "wb") as file:
                    for chunk in response.iter_content(chunk_size=1024):
                        file.write(chunk)
                         
                print("Audio saved as:", file_path)
                page.overlay.clear()
                page.overlay.append(ft.Audio(src="audio.mp3", autoplay=True))
                page.update()
            else:
                print("Failed to get audio")
        except Exception as e:
            print("ERROR", e)
                
    # enter_button
    btn_enter = ft.ElevatedButton(
        "Generate Voice",
        bgcolor="#FFD700",
        color="#1E1E2F",
        on_click=lambda e: save_and_play(),
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=15))
    )
       
    # UI Container
    input_container = ft.Container(
        content = ft.Column(
            controls=[
                txt_input, 
                voice_selection, 
                mood_selection,
                btn_enter, ft.Text("Adjust Pitch", size=18, 
                                   weight=ft.FontWeight.BOLD, color="#FFD700"), 
                voice_speed
            ],
            spacing=15,
            alignment=ft.MainAxisAlignment.CENTER,
        ),
        padding=20,
        border_radius=20,
        bgcolor="#2A2A3B",
        shadow=ft.BoxShadow(blur_radius=12, spread_radius=2, color="#FFD700")
    )
    
    page.add(
        ft.Column(
            controls=[input_container],
            spacing=20,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        )
    )
    page.update()
    
    # page.add(title)
    # page.add(txt_input)
    
# Run App
if __name__ == "__main__":
    ft.app(target=main,assets_dir=".")