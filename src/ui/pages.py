# src/ui/pages.py

import os
import requests
import logging

import flet as ft
from murf import Murf
from dotenv import load_dotenv
from .ui_config import *

# API client
path = "D:/RGT/Projects/Flet/Tutorial/app.env"
load_dotenv(path)
API_KEY = os.getenv("murf_api")
# print(API_KEY)
 
client = Murf(api_key=API_KEY)

voices = client.text_to_speech.get_voices()

styles = load_styles()

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
                voice_speed
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
