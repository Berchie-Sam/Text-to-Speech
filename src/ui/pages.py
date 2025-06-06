# src/ui/pages.py
import requests
import logging
import flet as ft
from .ui_config import *
from src.services.tts_client import MurfTTSClient

styles = load_styles()
tts_client = MurfTTSClient()
voices = tts_client.get_voices()

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


def build_main_page(page: ft.Page):
    page.title = "AI friend"
    page.padding = styles["padding"]["page"]
    page.bgcolor = styles["colors"]["background"]
    
    # Create UI widgets
    title = ft.Text(
        page.title, size=styles["fonts"]["title_size"],
        weight=ft.FontWeight.BOLD,
        color=styles["colors"]["primary_text"])
    
    txt_input = ft.TextField(
        label="Enter some text here...",
        width=350,
        bgcolor=styles["colors"]["container"],
        color=styles["colors"]["secondary_text"],
        border_radius=styles["borders"]["radius"],
        border_color=styles["colors"]["border"]
    )
    
    # voice_selection
    voice_selection = ft.Dropdown(
        label="Select Voice",
        options = [
            ft.dropdown.Option(voice) for voice in VOICE_MOODS.keys()
        ],
        width=350,
        bgcolor=styles["colors"]["container"],
        color=styles["colors"]["secondary_text"],
        # border_radius=styles["borders"]["radius"],
        # border_color=styles["colors"]["border"],
        value="Miles"
    )   
     
    # mood_selection
    mood_selection = ft.Dropdown(
        label="Choose Mood",
        width=350,
        bgcolor=styles["colors"]["container"],
        color=styles["colors"]["secondary_text"],
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
        label="{value}%",active_color=styles["colors"]["primary_text"]
    )
    
    # Generate AI voice
    def generate_audio():
        selected_voice = voice_selection.value
        voice_id = VOICE_MOODS.get(selected_voice, {}).get("voice_id")
        if not txt_input.value.strip():
            print("ERROR, you need some text...")
            return None
        
        return tts_client.generate_audio(
        text=txt_input.value,
        voice_id=voice_id,
        mood=mood_selection.value,
        pitch=voice_speed.value
    )
    
    progress_bar = ft.ProgressBar(width=350, visible=False, color=styles["colors"]["primary_text"])    
        
    def save_and_play():
        audio_url = generate_audio()
        if not audio_url:
            print("Error: no audio found..")
            return
        progress_bar.visible = True
        btn_enter.disabled = True
        page.update()
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
        finally:
            progress_bar.visible = False
            btn_enter.disabled = False
            page.update()
    
    
    # enter_button
    btn_enter = ft.ElevatedButton(
        "Generate Voice",
        bgcolor=styles["colors"]["button_bg"],
        color=styles["colors"]["button_text"],
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
                btn_enter, ft.Text("Adjust Pitch", size=styles["fonts"]["label_size"], 
                                   weight=ft.FontWeight.BOLD, color=styles["colors"]["primary_text"]), 
                voice_speed, 
                progress_bar,
            ],
            spacing=15,
            alignment=ft.MainAxisAlignment.CENTER,
        ),
        padding=styles["padding"]["container"],
        border_radius=styles["borders"]["container_radius"],
        bgcolor=styles["colors"]["container"],
        shadow=ft.BoxShadow(
            blur_radius=styles["shadow"]["blur_radius"],
            spread_radius=styles["shadow"]["spread_radius"],
            color=styles["colors"]["shadow"]
        )
    )
    
    page.add(
        ft.Column(
            controls=[input_container],
            spacing=20,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        )
    )
    page.update()
