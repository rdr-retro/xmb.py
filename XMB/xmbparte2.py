import pygame
import os
import sys
import time
import math
from utils import lerp
import reloj
from screen import ScreenSettings
from user_input_screen import UserInputScreen
from users import UserManager
from images import get_image
from xmbparte1 import XMBMenu as XMBMenuBase
from music import MusicVisualizer
from theme import open_theme_settings


class XMBMenu(XMBMenuBase):
    def __init__(self, screen, font, *args, **kwargs):
        super().__init__(screen, font, *args, **kwargs)
        self.base_font = font
        self.waves = None  # Define waves to prevent AttributeError
        self.W, self.H = self.screen.get_size()
        self._init_layout()
        self.font = self._create_font(int(self.H * 0.025))
        self.dark_menu_font = pygame.font.SysFont('arial', int(self.H * 0.028)) if hasattr(self, 'dark_menu_font') else None
        self.text_fonts = {
            'normal': pygame.font.SysFont('arial', int(self.font.get_height() * self.vertical_text_scale)),
            'selected': pygame.font.SysFont('arial', int(self.font.get_height() * self.vertical_text_selected_scale))
        }
        self.icon_alpha = self.target_icon_alpha = 100
        self.fade_speed = 800
        self.file_list_offset_x = self.target_file_list_offset_x = 0
        self.ajustes_list_offset_x = self.target_ajustes_list_offset_x = 0
        self.submenu_transition_speed = 8
        self.jump_speed = 300
        self.blink_duration = 1.0
        self.theme_settings = None


        # Force specific order for "Ajustes" submenu
        if "Ajustes" in self.submenus:
            desired_order = [
                "Actualización del sistema",
                "Ajustes de pantalla",
                "Ajustes de tema",
                "Huevo"
            ]
            self.submenus["Ajustes"] = desired_order


        self._default_image = pygame.Surface((64, 64), pygame.SRCALPHA)
        self._default_image.fill((150, 150, 150))
        self.vertical_images.update({
            "Ajustes de pantalla": get_image("1A3F7C") or self._default_image,
            "Actualización del sistema": get_image("B45E2F") or self._default_image,
            "Ajustes de tema": get_image("08D9A3") or self._default_image,
            "Huevo": get_image("4F7A2B") or self._default_image,
            "Archivos": get_image("EFA295") or self._default_image,  # Folder icon added here
            "Audio": get_image("B544D5") or self._default_image  # B544D5 for audio files
        })


        self.horizontal_icon_cache = {}
        for name in self.items:
            image = self.horizontal_images.get(name, self._default_image)
            square_size = int(self.square_size_h * self.horizontal_icon_scale)
            scale_factor = square_size / max(image.get_size())
            self.horizontal_icon_cache[name] = {
                'normal': pygame.transform.smoothscale(image, (int(image.get_width() * scale_factor), int(image.get_height() * scale_factor))),
                'selected': pygame.transform.smoothscale(image, (int(image.get_width() * scale_factor * self.selected_icon_scale), int(image.get_height() * scale_factor * self.selected_icon_scale)))
            }


        arrow_image = get_image("F1F1F1") or self._create_default_arrow()
        self.arrow_image = pygame.transform.smoothscale(arrow_image, (self.arrow_size, self.arrow_size))
        self.music_player = None


    def _init_layout(self):
        self.menu_offset_x = int(self.W * -0.15)
        self.horz_y = int(self.H * 0.20)
        self.vert_y_center = int(self.H * 0.40)
        self.square_size_h = int(self.H * 0.20)
        self.horizontal_icon_scale = 0.65
        self.selected_icon_scale = 1.20
        self.vertical_icon_scale = 0.75
        self.vertical_icon_selected_scale = 1.0
        self.vertical_text_scale = 0.75
        self.vertical_text_selected_scale = 1.0
        self.spacing = int(self.W * 0.14)
        self.line_height = int(self.H * 0.13)
        self.submenu_indent = int(self.W * 0.15)
        self.arrow_size = int(self.H * 0.06)
        self.icon_size_base = int(self.H * 0.128)
        self.text_offset = int(self.W * 0.015)
        self.submenu_offset = int(self.W * 0.05)


    def _create_font(self, size):
        return pygame.font.Font(self.base_font, size) if isinstance(self.base_font, str) and os.path.exists(self.base_font) else pygame.font.SysFont('arial', size)


    def _create_default_arrow(self):
        arrow = pygame.Surface((self.arrow_size, self.arrow_size), pygame.SRCALPHA)
        pygame.draw.polygon(arrow, (241, 241, 241), [
            (int(self.arrow_size * 0.25), int(self.arrow_size * 0.5)),
            (int(self.arrow_size * 0.75), int(self.arrow_size * 0.2)),
            (int(self.arrow_size * 0.75), int(self.arrow_size * 0.8))
        ])
        return arrow


    def update_layout(self):
        self.W, self.H = self.screen.get_size()
        self._init_layout()
        arrow_image = get_image("F1F1F1") or self._create_default_arrow()
        self.arrow_image = pygame.transform.smoothscale(arrow_image, (self.arrow_size, self.arrow_size))
        self.target_offset_x = -self.section * self.spacing
        self.font = self._create_font(int(self.H * 0.025))
        self.text_fonts.update({
            'normal': pygame.font.SysFont('arial', int(self.font.get_height() * self.vertical_text_scale)),
            'selected': pygame.font.SysFont('arial', int(self.font.get_height() * self.vertical_text_selected_scale))
        })
        if self.dark_menu_font:
            self.dark_menu_font = pygame.font.SysFont('arial', int(self.H * 0.028))
        for name in self.items:
            image = self.horizontal_images.get(name, self._default_image)
            square_size = int(self.square_size_h * self.horizontal_icon_scale)
            scale_factor = square_size / max(image.get_size())
            self.horizontal_icon_cache[name] = {
                'normal': pygame.transform.smoothscale(image, (int(image.get_width() * scale_factor), int(image.get_height() * scale_factor))),
                'selected': pygame.transform.smoothscale(image, (int(image.get_width() * scale_factor * self.selected_icon_scale), int(image.get_height() * scale_factor * self.selected_icon_scale)))
            }


    def on_resolution_change(self, width, height):
        self.update_layout()


    def play_option_sound(self):
        if self.option_sound:
            self.option_sound.play()


    def handle_external_signal(self, signal):
        self.show_waves_only = self.state = "show_waves" if signal == "SHOW_WAVES" else False if signal == "SHOW_MENU" else self.show_waves_only
        if signal == "SHOW_MENU":
            self.state = "menu"

    # NUEVO MÉTODO AGREGADO
    def exit_file_manager(self):
        self.showing_files = False
        self.file_list = []
        self.file_index = 0
        self.current_path = None
        self.file_list_offset_x = 0
        self.target_file_list_offset_x = 0
        self.play_option_sound()


    def handle_event(self, event):
        if self.state == "music_player" and self.music_player:
            self.music_player.handle_event(event)
            if not self.music_player.is_running():
                self.music_player = None
                self.state = "menu"
            return
        if self.dark_menu_active and event.type == pygame.KEYDOWN:
            self.dark_menu_active = False
            return
        if self.show_waves_only and event.type == pygame.KEYDOWN:
            self.show_waves_only = False
            self.state = "menu"
        elif self.state == "show_screen_settings":
            if self.screen_settings and self.screen_settings.handle_event(event) == "exit":
                self.screen_settings = None
                self.state = "menu"
            elif not self.screen_settings:
                self.state = "menu"
        elif self.state == "show_theme_settings":
            if self.theme_settings and self.theme_settings.handle_event(event) == "exit":
                self.theme_settings = None
                self.state = "menu"
            elif not self.theme_settings:
                self.state = "menu"
        elif self.state == "create_user":
            if self.input_screen.handle_event(event) == "confirm":
                new_name = self.input_screen.username.strip()
                if new_name and (created := self.user_manager.add_user(new_name)):
                    self.submenus["Usuarios"] = self.user_manager.get_menu_items()
                    self.active_user = created
                self.state = "menu"
                self.input_screen = None
        elif self.state == "show_clock" and event.type == pygame.KEYDOWN:
            self.state = "menu"
        elif self.state == "menu":
            self.handle_event_menu(event)


    def handle_event_menu(self, event):
        if event.type != pygame.KEYDOWN:
            return
        if event.key == pygame.K_a:
            self.dark_menu_active = not self.dark_menu_active
            if self.dark_menu_active and self.dark_menu_sound:
                self.dark_menu_sound.play()
            return
        old_section, old_subsection = self.section, self.subsection
        old_ajustes_idx = self.ajustes_pantalla_index
        old_file_index = self.file_index


        if self.showing_ajustes_pantalla:
            if event.key == pygame.K_UP and self.ajustes_pantalla_index > 0:
                self.ajustes_pantalla_index -= 1
                self.jump_offset = int(self.H * 0.065)
            elif event.key == pygame.K_DOWN and self.ajustes_pantalla_index < len(self.ajustes_pantalla_items) - 1:
                self.ajustes_pantalla_index += 1
                self.jump_offset = int(self.H * 0.065)
            elif event.key == pygame.K_LEFT:
                self.showing_ajustes_pantalla = False
                self.ajustes_pantalla_index = 0
            elif event.key == pygame.K_RETURN and self.ajustes_pantalla_items[self.ajustes_pantalla_index] == "Ajustes de salida de video":
                self.screen_settings = ScreenSettings(self.screen, self.base_font, on_resolution_change=self.on_resolution_change)
                self.state = "show_screen_settings"
                self.showing_ajustes_pantalla = False
                self.play_option_sound()
            if self.ajustes_pantalla_index != old_ajustes_idx:
                self.play_option_sound()
            return


        if self.showing_files:
            if event.key == pygame.K_UP and self.file_index > 0:
                self.file_index -= 1
                self.jump_offset = int(self.H * 0.065)
            elif event.key == pygame.K_DOWN and self.file_index < len(self.file_list) - 1:
                self.file_index += 1
                self.jump_offset = int(self.H * 0.065)
            elif event.key == pygame.K_LEFT:
                if os.path.dirname(self.current_path) != self.current_path:  # Check if not at root
                    self.current_path = os.path.dirname(self.current_path)
                    self.file_list = os.listdir(self.current_path) or []
                    self.file_index = 0
                    self.play_option_sound()
                else:
                    self.exit_file_manager()
            elif event.key == pygame.K_RETURN and self.file_list:
                selected = self.file_list[self.file_index]
                path = os.path.join(self.current_path, selected)
                if os.path.isdir(path):
                    self.current_path = path
                    self.file_list = os.listdir(self.current_path) or []
                    self.file_index = 0
                elif os.path.isfile(path) and selected.lower().endswith((".mp3", ".wav", ".aac", ".wma")):
                    try:
                        self.music_player = MusicVisualizer(self.screen, path)
                        self.state = "music_player"
                    except Exception as e:
                        print(f"Error launching MusicVisualizer: {e}")
                self.play_option_sound()
            if self.file_index != old_file_index:
                self.play_option_sound()
            return


        if event.key == pygame.K_LEFT:
            self.prev_section = self.section
            self.section = max(0, self.section - 1)
            self.subsection = 0
            self.target_offset_x = -self.section * self.spacing
        elif event.key == pygame.K_RIGHT:
            self.prev_section = self.section
            self.section = min(len(self.items) - 1, self.section + 1)
            self.subsection = 0
            self.target_offset_x = -self.section * self.spacing
        elif event.key == pygame.K_UP and self.subsection > 0:
            self.prev_subsection = self.subsection
            self.subsection -= 1
            self.jump_offset = int(self.H * 0.065)
        elif event.key == pygame.K_DOWN and self.subsection < len(self.submenus[self.items[self.section]]) - 1:
            self.subsection += 1
            self.jump_offset = int(self.H * 0.065)
        elif event.key == pygame.K_RETURN:
            self.execute_action()
        if self.section != old_section or self.subsection != old_subsection:
            self.play_option_sound()


    def execute_action(self):
        category, option = self.get_selected()
        actions = {
            "Usuarios": {
                "Apagar sistema": lambda: (pygame.quit(), sys.exit()),
                "Crear nuevo usuario": lambda: setattr(self, 'state', "create_user") or setattr(self, 'input_screen', UserInputScreen(self.font, f"Usuario{len(self.user_manager.users) + 1}")),
                None: lambda: setattr(self, 'active_user', option) or print(f"👤 Sesión iniciada con {option}")
            },
            "Reloj": lambda: setattr(self, 'state', "show_clock"),
            "Ajustes": {
                "Ajustes de pantalla": lambda: setattr(self, 'showing_ajustes_pantalla', True),
                "Actualización del sistema": lambda: print("Iniciando proceso de actualización del sistema..."),
                "Ajustes de tema": lambda: (setattr(self, 'theme_settings', open_theme_settings(self.screen, self.base_font)),
                                           setattr(self, 'state', "show_theme_settings")),
                "Huevo": lambda: print("¡Huevo activado! 🥚")
            },
            "Ajustes de salida de video": lambda: (setattr(self, 'screen_settings', ScreenSettings(self.screen, self.base_font, on_resolution_change=self.on_resolution_change)),
                                                  setattr(self, 'state', "show_screen_settings"),
                                                  setattr(self, 'showing_ajustes_pantalla', False)),
            "Archivos": lambda: (setattr(self, 'showing_files', True),
                                 setattr(self, 'current_path', os.path.join(os.getcwd(), "music") if category == "Música" else os.getcwd()),
                                 setattr(self, 'file_list', os.listdir(self.current_path) or []),
                                 setattr(self, 'file_index', 0))
        }
        action = actions.get(category, actions.get(option))
        if action:
            if isinstance(action, dict):
                action = action.get(option, action.get(None) if option in self.user_manager.users else lambda: None)
            action()


    def update(self, dt):
        if self.state == "music_player" and self.music_player:
            self.music_player.update(dt)
            if not self.music_player.is_running():
                self.music_player = None
                self.state = "menu"
            return
        if self.state == "show_theme_settings" and self.theme_settings:
            self.theme_settings.update(dt)
            return
        if self.state != "menu" or self.show_waves_only:
            return
        self.offset_x = lerp(self.offset_x, self.target_offset_x, dt * 6)
        self.offset_y = lerp(self.offset_y, self.target_offset_y, dt * 6)
        self.file_list_offset_x = lerp(self.file_list_offset_x, self.target_file_list_offset_x, dt * self.submenu_transition_speed)


        if (self.showing_ajustes_pantalla and self.items[self.section] == "Ajustes" and
            self.submenus.get(self.items[self.section], []) and
            self.submenus[self.items[self.section]][self.subsection] == "Ajustes de pantalla"):
            target_ajustes_offset = self.submenu_indent
        else:
            target_ajustes_offset = self.ajustes_list_offset_x


        self.ajustes_list_offset_x = lerp(self.ajustes_list_offset_x, target_ajustes_offset, dt * self.submenu_transition_speed)


        self.jump_offset = max(0, self.jump_offset - self.jump_speed * dt)
        second_level_active = (
            (self.showing_ajustes_pantalla and self.items[self.section] == "Ajustes" and
             self.submenus.get(self.items[self.section], []) and self.submenus[self.items[self.section]][self.subsection] == "Ajustes de pantalla") or
            (self.showing_files and self.items[self.section] in ["Fotos", "Música", "Videos"] and
             self.submenus.get(self.items[self.section], []) and self.submenus[self.items[self.section]][self.subsection] == "Archivos")
        )
        self.target_icon_alpha = 0 if second_level_active else 100
        self.icon_alpha = lerp(self.icon_alpha, self.target_icon_alpha, dt * self.fade_speed / 100)
        self.target_file_list_offset_x = self.submenu_indent if second_level_active and self.showing_files else 0


    def draw_text_with_alpha_outline(self, surface, font, text_str, color, alpha, pos):
        x, y = pos
        base_text = font.render(text_str, True, color)
        outline_surf = font.render(text_str, True, (255, 255, 255))
        outline_surf.set_alpha(int(alpha * 100 / 255))
        for ox, oy in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]:
            surface.blit(outline_surf, (x + ox, y + oy))
        surface.blit(base_text, pos)


    def draw_vertical_list(self, items, active_index, x_center, y_center, last_positions, alpha, icon_map=None, folder_icon=None, base_path=None):
        drawn_rects = []
        audio_extensions = (".mp3", ".wav", ".aac", ".wma")
        for idx, item in enumerate(items):
            if self.showing_ajustes_pantalla and self.items[self.section] == "Ajustes" and item == "Ajustes de pantalla":
                icon = self.vertical_images.get(item, None)
                if icon:
                    is_active = idx == active_index
                    icon_scale = self.vertical_icon_selected_scale if is_active else self.vertical_icon_scale
                    icon_size = int(self.icon_size_base * icon_scale)
                    icon_scaled = pygame.transform.smoothscale(icon, (icon_size, icon_size))
                    icon_rect = icon_scaled.get_rect(midtop=(x_center, y_center + (idx - active_index) * self.line_height))
                    self.screen.blit(icon_scaled, icon_rect)
                continue
            relative_index = idx - active_index
            spacing = self.line_height if relative_index == 0 else (self.line_height * 3.0 if relative_index < 0 else self.line_height)
            target_y = y_center + (relative_index * spacing)
            last_positions[item] = lerp(last_positions.get(item, target_y) - self.jump_offset, target_y, 0.15)
            # Determine icon based on context
            if self.items[self.section] == "Usuarios":
                icon = self.vertical_images.get("Usuario ya creado" if item in self.user_manager.users else "Nuevo usuario" if item == "Crear nuevo usuario" else item, None)
            elif base_path and os.path.isfile(os.path.join(base_path, item)) and item.lower().endswith(audio_extensions):
                icon = self.vertical_images.get("Audio", None)  # Use B544D5 for audio files
            elif base_path and os.path.isdir(os.path.join(base_path, item)):
                icon = folder_icon or self._default_image  # Use folder_icon or default for folders
            else:
                icon = icon_map.get(item) if icon_map else None
            is_active = idx == active_index
            icon_scale = self.vertical_icon_selected_scale if is_active else self.vertical_icon_scale
            font = self.text_fonts['selected'] if is_active else self.text_fonts['normal']
            icon_size = int(self.icon_size_base * icon_scale)
            text_surface = font.render(item, True, (255, 255, 255))
            if icon:
                icon_scaled = pygame.transform.smoothscale(icon, (icon_size, icon_size))
                icon_rect = icon_scaled.get_rect(midtop=(x_center, last_positions[item]))
                self.screen.blit(icon_scaled, icon_rect)
                text_rect = text_surface.get_rect(midleft=(icon_rect.right + self.text_offset, icon_rect.centery))
            else:
                text_rect = text_surface.get_rect(midtop=(x_center, last_positions[item]))
            if is_active:
                self.draw_text_with_alpha_outline(self.screen, font, item, (255, 255, 255), alpha, text_rect.topleft)
            else:
                self.screen.blit(text_surface, text_rect)
            drawn_rects.append(text_rect)
        return drawn_rects


    def draw_submenu(self, items, active_index, selected_rect, x_center, y_center, last_positions, alpha, empty_message, offset_x, icon_map=None, folder_icon=None, base_path=None):
        if not items:
            text_surface = self.text_fonts['normal'].render(empty_message, True, (200, 200, 200))
            self.screen.blit(text_surface, text_surface.get_rect(center=(self.W // 2, self.H // 2)))
            return
        vertical_offset = -int(self.H * 0.10)
        submenu_y = (selected_rect.centery if selected_rect else y_center) + vertical_offset
        arrow_x = x_center + self.submenu_indent
        arrow_y = submenu_y
        arrow_rect = self.arrow_image.get_rect(center=(arrow_x, arrow_y))
        self.screen.blit(self.arrow_image, arrow_rect)
        submenu_x = arrow_x + self.arrow_size + self.submenu_offset + offset_x
        self.draw_vertical_list(items, active_index, submenu_x, submenu_y, last_positions, alpha, icon_map, folder_icon, base_path)


    def draw(self):
        if self.state == "music_player" and self.music_player:
            self.music_player.draw()
        elif self.show_waves_only:
            self.draw_waves()
        elif self.state == "menu":
            self.draw_menu()
        elif self.state == "create_user":
            self.input_screen.draw(self.screen)
        elif self.state == "show_clock":
            self.draw_clock()
        elif self.state == "show_screen_settings":
            if self.screen_settings:
                self.screen_settings.draw(self.waves, self.W, self.H, time.time())
            else:
                placeholder = self.font.render("Pantalla: Ajustes de salida de video", True, (255, 255, 0))
                self.screen.blit(placeholder, (int(self.W * 0.05) - int(self.W * 0.20), int(self.H * 0.23)))
        elif self.state == "show_theme_settings":
            if self.theme_settings:
                self.theme_settings.draw(self.W, self.H, time.time())
            else:
                placeholder = self.font.render("Pantalla: Ajustes de tema", True, (255, 255, 0))
                self.screen.blit(placeholder, (int(self.W * 0.05) - int(self.W * 0.20), int(self.H * 0.23)))
        if self.dark_menu_active and self.dark_menu_font:
            self.screen.blit(self.dark_menu_surf, (0, 0))
            text_surf = self.dark_menu_font.render("MENU OSCURO", True, (255, 255, 255))
            self.screen.blit(text_surf, text_surf.get_rect(center=(self.W // 2, self.H // 2)))


    def draw_menu(self):
        W, H = self.W, self.H
        start_x = (W // 2) + self.menu_offset_x
        cat_positions = []
        alpha = int((math.sin((time.time() - self.start_time) % self.blink_duration / self.blink_duration * 2 * math.pi - math.pi / 2) + 1) / 2 * 255)


        if not self.items or self.section < 0 or self.section >= len(self.items):
            placeholder = self.font.render("Error: Menú no inicializado", True, (255, 0, 0))
            self.screen.blit(placeholder, (int(self.W * 0.05), int(self.H * 0.05)))
            print(f"Error: self.items is {self.items}, self.section is {self.section}")
            return


        for idx, name in enumerate(self.items):
            if idx != self.section and self.icon_alpha <= 0:
                continue
            img_scaled = self.horizontal_icon_cache[name]['selected' if idx == self.section else 'normal']
            img_rect = img_scaled.get_rect(center=(start_x + idx * self.spacing + self.offset_x, self.horz_y))
            img_scaled.set_alpha(255 if idx == self.section else int(self.icon_alpha))
            self.screen.blit(img_scaled, img_rect)
            cat_positions.append(img_rect.centerx)
            if idx == self.section:
                text_surface = self.font.render(name, True, (255, 255, 255))
                self.screen.blit(text_surface, text_surface.get_rect(midtop=(img_rect.centerx, img_rect.bottom + int(self.H * 0.015))))


        if not cat_positions:
            print(f"Error: cat_positions is empty, self.section is {self.section}")
            placeholder = self.font.render("Error: No se encontraron categorías", True, (255, 0, 0))
            self.screen.blit(placeholder, (int(self.W * 0.05), int(self.H * 0.05)))
            return


        active_cat = self.items[self.section]
        submenu = self.submenus.get(active_cat, [])
        self.vert_x_center = cat_positions[min(self.section, len(cat_positions) - 1)]
        drawn_rects = self.draw_vertical_list(
            submenu, self.subsection if self.subsection < len(submenu) else 0, self.vert_x_center, self.vert_y_center,
            self.last_y_positions, alpha, icon_map=self.vertical_images, folder_icon=self.vertical_images.get("Archivos")
        )
        selected_rect = drawn_rects[self.subsection] if self.subsection < len(drawn_rects) else None


        if self.showing_ajustes_pantalla and active_cat == "Ajustes" and submenu and submenu[self.subsection] == "Ajustes de pantalla":
            self.draw_submenu(
                self.ajustes_pantalla_items, self.ajustes_pantalla_index, selected_rect, self.vert_x_center, self.vert_y_center,
                self.last_y_positions_files, alpha, "No hay ajustes disponibles", self.ajustes_list_offset_x, self.vertical_images
            )
        elif self.showing_files and active_cat in ["Fotos", "Música", "Videos"] and submenu and submenu[self.subsection] == "Archivos":
            self.draw_submenu(
                self.file_list, self.file_index, selected_rect, self.vert_x_center, self.vert_y_center,
                self.last_y_positions_files, alpha, "No se encontraron archivos", self.file_list_offset_x,
                folder_icon=self.vertical_images.get("Archivos"), base_path=self.current_path
            )


        user_text = f"Usuario activo: {self.active_user}"
        user_surface = self.font.render(user_text, True, (200, 200, 200))
        self.screen.blit(user_surface, (W - user_surface.get_width() - int(self.W * 0.03), H - int(self.H * 0.04)))


    def draw_clock(self):
        reloj.draw_reloj(self.screen)


    def draw_waves(self):
        pass  # Placeholder, as waves is None


    def get_selected(self):
        cat = self.items[self.section]
        submenu_list = self.submenus.get(cat, [])
        return cat, submenu_list[self.subsection] if self.subsection < len(submenu_list) else None
