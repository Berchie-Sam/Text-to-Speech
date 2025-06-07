# Imports
import flet as ft
from src.ui.pages import build_main_page

# Run App
if __name__ == "__main__":
    ft.app(target=build_main_page,assets_dir=".")