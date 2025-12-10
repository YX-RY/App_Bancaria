import flet as ft
from database import init_db
from ui.screens import main_view


def main(page: ft.Page):
    # Configuración de la página
    page.title = "Gestor Financiero Personal"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 0
    page.window_width = 1200
    page.window_height = 800
    page.window_resizable = True

    # Inicializar base de datos
    init_db()

    # Cargar la vista principal
    page.add(main_view(page))

    # Función para cambiar tema
    def toggle_theme(e):
        page.theme_mode = ft.ThemeMode.DARK if page.theme_mode == ft.ThemeMode.LIGHT else ft.ThemeMode.LIGHT
        page.update()

    page.theme_toggle = toggle_theme


if __name__ == "__main__":
    ft.app(target=main)