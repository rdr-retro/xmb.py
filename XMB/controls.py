# controls.py
import pygame

# Mapas de teclas para navegación del menú
NAVIGATION_KEYS = {
    "LEFT": pygame.K_LEFT,
    "RIGHT": pygame.K_RIGHT,
    "UP": pygame.K_UP,
    "DOWN": pygame.K_DOWN,
    "SELECT": pygame.K_RETURN,
    "BACK": pygame.K_ESCAPE,
}

class MenuControls:
    def __init__(self):
        # Estado actual de navegación, para poder consultar
        self.direction = None
        self.select = False
        self.back = False

    def reset(self):
        self.direction = None
        self.select = False
        self.back = False

    # Procesa un evento pygame y actualiza el estado de navegación
    def handle_event(self, event):
        if event.type != pygame.KEYDOWN:
            return

        if event.key == NAVIGATION_KEYS["LEFT"]:
            self.direction = "LEFT"
        elif event.key == NAVIGATION_KEYS["RIGHT"]:
            self.direction = "RIGHT"
        elif event.key == NAVIGATION_KEYS["UP"]:
            self.direction = "UP"
        elif event.key == NAVIGATION_KEYS["DOWN"]:
            self.direction = "DOWN"
        elif event.key == NAVIGATION_KEYS["SELECT"]:
            self.select = True
        elif event.key == NAVIGATION_KEYS["BACK"]:
            self.back = True

    # Métodos auxiliares para consultar el estado
    def is_moving_left(self):
        return self.direction == "LEFT"

    def is_moving_right(self):
        return self.direction == "RIGHT"

    def is_moving_up(self):
        return self.direction == "UP"

    def is_moving_down(self):
        return self.direction == "DOWN"

    def is_select_pressed(self):
        return self.select

    def is_back_pressed(self):
        return self.back
