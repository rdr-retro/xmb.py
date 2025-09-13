# user_input_screen.py
import pygame
import time
import math
from utils import make_gradient
from warning_screen import FilledWave, apply_blur   # reutilizamos ola y blur

class UserInputScreen:
    def __init__(self, font, default_name="Usuario 1"):
        self.font = font
        self.username = default_name
        self.start_time = time.perf_counter()

        # Olas como en main.py (puedes ajustar alturas si quieres)
        self.waves = [
            FilledWave(400, 20, 40, 16, (200, 140, 255), alpha=255),
            FilledWave(420, 15, 32, 12, (150, 80, 200), alpha=160),
        ]

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:   # OK
                return "confirm"
            elif event.key == pygame.K_BACKSPACE:
                self.username = self.username[:-1]
            else:
                if len(self.username) < 20:
                    self.username += event.unicode
        return None

    def draw(self, screen):
        W, H = screen.get_size()

        # --- Fondo con gradiente ---
        make_gradient(screen, (50, 0, 80), (20, 0, 40))

        # --- Capa de olas + desenfoque (solo el fondo) ---
        t = time.perf_counter() - self.start_time
        wave_layer = pygame.Surface((W, H), pygame.SRCALPHA)
        for w in self.waves:
            w.draw(wave_layer, W, H, t)
        blurred_waves = apply_blur(wave_layer, radius=6)  # ajusta el radio si quieres más/menos blur
        screen.blit(blurred_waves, (0, 0))

        # --- Barras blancas (no se desenfocan porque van encima) ---
        top_margin = 80           # a 80px del borde superior
        bottom_margin = H - 100   # a 100px del borde inferior
        pygame.draw.line(screen, (255, 255, 255), (0, top_margin), (W, top_margin), 3)
        pygame.draw.line(screen, (255, 255, 255), (0, bottom_margin), (W, bottom_margin), 3)

        # --- Contenido centrado entre las barras ---
        center_y = (top_margin + bottom_margin) // 2

        # Título
        title_font = pygame.font.Font(None, 32)
        title = title_font.render("Introduzca un nombre de usuario.", True, (255, 255, 255))
        screen.blit(title, (W // 2 - title.get_width() // 2, center_y - 80))

        # Caja de entrada
        input_rect = pygame.Rect(W // 2 - 250, center_y - 30, 500, 40)
        box_surface = pygame.Surface(input_rect.size, pygame.SRCALPHA)
        pygame.draw.rect(box_surface, (120, 120, 140, 180), box_surface.get_rect(), border_radius=4)
        pygame.draw.rect(box_surface, (255, 255, 255), box_surface.get_rect(), 2, border_radius=4)
        screen.blit(box_surface, input_rect.topleft)

        # Texto del input
        text_surface = self.font.render(self.username, True, (255, 255, 255))
        screen.blit(text_surface, (input_rect.x + 10, input_rect.y + 8))

        # Botón OK (parpadeante)
        ok_rect = pygame.Rect(W // 2 - 35, input_rect.bottom + 30, 70, 32)
        elapsed = (time.perf_counter() - self.start_time) % 1.5
        alpha = (math.sin(elapsed * math.pi * 2 / 1.5) + 1) / 2  # 0..1
        ok_color = (
            int(180 + 40 * alpha),
            int(180 + 40 * alpha),
            int(180 + 40 * alpha)
        )
        pygame.draw.rect(screen, ok_color, ok_rect, border_radius=4)
        pygame.draw.rect(screen, (255, 255, 255), ok_rect, 2, border_radius=4)

        ok_text = self.font.render("OK", True, (0, 0, 0))
        screen.blit(ok_text, (ok_rect.centerx - ok_text.get_width() // 2,
                              ok_rect.centery - ok_text.get_height() // 2))

        # Instrucciones bajo la barra inferior
        instr_font = pygame.font.Font(None, 26)
        instr_text = instr_font.render("✕ Editar        ○ Atrás", True, (255, 255, 255))
        screen.blit(instr_text, (W // 2 - instr_text.get_width() // 2, bottom_margin + 30))

        return input_rect, ok_rect
