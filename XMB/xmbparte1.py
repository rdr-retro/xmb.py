import pygame
import os
import time
import math
import unicodedata
import sys
from utils import lerp
from users import UserManager
from user_input_screen import UserInputScreen
import reloj  # Módulo reloj para dibujar reloj y olas
from images import get_image  # 🔥 Ahora usamos solo hexadecimales
from screen import ScreenSettings


def clean_name(name):
    nfkd_form = unicodedata.normalize("NFKD", name)
    only_ascii = nfkd_form.encode("ASCII", "ignore").decode("ASCII")
    return only_ascii.lower().replace(" ", "")


class XMBMenu:
    def __init__(self, screen, font, items):
        self.screen = screen
        self.font = font
        try:
            pygame.mixer.init()
        except Exception as e:
            print(f"⚠️ Error iniciando mixer: {e}")
        sound_path = os.path.join("sounds", "snd_option.wav")
        self.option_sound = pygame.mixer.Sound(sound_path) if os.path.isfile(sound_path) else None

        # ---------------- SONIDO MENÚ OSCURO ----------------
        dark_sound_path = os.path.join("sounds", "snd_system_ok.wav")
        self.dark_menu_sound = pygame.mixer.Sound(dark_sound_path) if os.path.isfile(dark_sound_path) else None

        self.user_manager = UserManager()
        items_with_users = dict(items)

        for forced in ["Fotos", "Música", "Videos"]:
            if forced in items_with_users:
                items_with_users[forced] = ["Archivos", "Favoritos"]

        if "Juegos" in items_with_users:
            items_with_users["Juegos"] = ["Archivos", "Accesos directos", "Favoritos"]

        items_with_users["Reloj"] = ["Reloj"]
        items_with_users["Usuarios"] = self.user_manager.get_menu_items()
        items_with_users["Ajustes"] = ["Ajustes de pantalla"]
        self.ajustes_pantalla_items = ["Ajustes de salida de video"]

        sections = list(items_with_users.keys())
        ordered_sections = []
        if "Reloj" in sections:
            ordered_sections.append("Reloj")
            sections.remove("Reloj")
        if "Usuarios" in sections:
            ordered_sections.append("Usuarios")
            sections.remove("Usuarios")
        if "Ajustes" in sections:
            ordered_sections.append("Ajustes")
            sections.remove("Ajustes")
        if "Juegos" in sections:
            sections.remove("Juegos")
            games_section = ["Juegos"]
        else:
            games_section = []
        ordered_sections += sections + games_section

        self.items = ordered_sections
        self.submenus = items_with_users
        self.section = self.items.index("Usuarios")
        self.prev_section = 0
        self.subsection = 0
        self.prev_subsection = None
        self.state = "menu"
        self.input_screen = None
        self.active_user = self.user_manager.users[0]

        # ---------------- POSICIONAMIENTO ----------------
        self.spacing = 250
        self.line_height = 120
        self.offset_x = 0.0
        self.target_offset_x = 0.0
        self.offset_y = 0.0
        self.target_offset_y = 0.0
        self.jump_offset = 0.0
        self.jump_speed = 200
        self.square_size_h = 100
        self.horz_y = 250
        self.vert_x_center = None
        self.vert_y_center = 350
        self.text_scale_vertical_selected = 0.7
        self.text_scale_vertical_unselected = 0.5
        self.menu_offset_x = -260
        self.menu_offset_y = 180
        self.start_time = time.time()
        self.blink_duration = 1.5

        self.last_y_positions = {}
        self.last_y_positions_files = {}
        self.file_list = []
        self.file_index = 0
        self.showing_files = False
        self.current_path = os.getcwd()

        self.showing_ajustes_pantalla = False
        self.ajustes_pantalla_index = 0
        self.screen_settings = None  # Instancia de screen.py para ajustes pantalla

        self.horizontal_images = {
            "Reloj": get_image("A92F11"),
            "Usuarios": get_image("99CC00"),
            "Ajustes": get_image("DD44CC"),
            "Fotos": get_image("11AAFF"),
            "Música": get_image("22BB66"),
            "Videos": get_image("FFAA33"),
            "Juegos": get_image("BB00FF"),
        }

        self.vertical_images = {
            "Archivos": get_image("EFA295"),
            "Accesos directos": get_image("33AAFF"),
            "Favoritos": get_image("C1B3F0"),
            "Apagar sistema": get_image("FF0000"),
            "Nuevo usuario": get_image("33AA77"),
            "Usuario ya creado": get_image("7799CC"),
            "Ajustes de pantalla": get_image("998877"),
            "Ajustes de salida de video": get_image("4455FF"),
        }

        self.arrow_image = get_image("F1F1F1")
        self.show_waves_only = False

        # ---------------- MENÚ OSCURO ----------------
        self.dark_menu_active = False
        W, H = self.screen.get_size()
        self.dark_menu_surf = pygame.Surface((W, H), pygame.SRCALPHA)
        self.dark_menu_surf.fill((0, 0, 0, 180))  # Negro semitransparente
        self.dark_menu_font = pygame.font.SysFont(None, 72)
