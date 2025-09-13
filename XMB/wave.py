import pygame
import pygame.gfxdraw
import numpy as np
import math
import time

FPS = 30
MESH_SIZE = 40
BASE_ANIMATION_SPEED = 5.0
AMPLITUDE = 2

FOV = 256
CAMERA_DISTANCE = 25

# 🎨 Color presets (mesh_color, bg_top, bg_bottom)
COLOR_PRESETS = [
    ((255, 140, 200, 90), (90, 20, 90), (50, 10, 60)),  # Pink
    ((0, 105, 255, 80), (0, 20, 80), (0, 10, 40)),    # Blue
    ((0, 255, 0, 80), (0, 80, 0), (0, 40, 0)),        # Green
    ((255, 0, 0, 80), (80, 0, 0), (40, 0, 0)),        # Red
    ((0, 255, 255, 80), (0, 80, 80), (0, 40, 40)),    # Cyan
    ((255, 255, 0, 80), (80, 80, 0), (40, 40, 0)),    # Yellow
    ((128, 0, 255, 80), (40, 0, 80), (20, 0, 40)),    # Purple
    ((255, 165, 0, 80), (80, 40, 0), (40, 20, 0)),    # Orange
    ((0, 128, 128, 80), (0, 40, 40), (0, 20, 20)),    # Teal
    ((255, 0, 255, 80), (80, 0, 80), (40, 0, 40)),    # Magenta
]

# 🎨 Current color preset index
current_color_index = 0

# 🎨 Global color variables
PINK_COLOR = COLOR_PRESETS[current_color_index][0]
BG_TOP = COLOR_PRESETS[current_color_index][1]
BG_BOTTOM = COLOR_PRESETS[current_color_index][2]

# ⚡ Fuentes de luz (x, y, radio, intensidad)
LIGHTS = [
    (0, 5, 8, 2.0),    # luz arriba-izquierda
    (5, -3, 6, 1.8),   # luz derecha-abajo
    (-6, -4, 7, 1.5),  # luz extra izquierda
]

ANIMATION_SPEED_MAX = 1.0
ANIMATION_SPEED_MIN = 0.5
TOUCH_ACCEL_DURATION = 3.0

animation_speed_factor = ANIMATION_SPEED_MIN
last_touch_time = None

# --- Función para crear gradiente ---
def make_gradient(surface, top_color, bottom_color):
    """Crea un gradiente vertical de top_color a bottom_color."""
    width, height = surface.get_size()
    top_r, top_g, top_b = top_color
    bot_r, bot_g, bot_b = bottom_color
    for y in range(height):
        t = y / (height - 1)
        r = int(top_r + t * (bot_r - top_r))
        g = int(top_g + t * (bot_g - top_g))
        b = int(top_b + t * (bot_b - top_b))
        pygame.draw.line(surface, (r, g, b), (0, y), (width, y))

# --- Utils matemáticos ---
def rotate_x(point, angle_rad):
    x, y, z = point
    cos_ang = math.cos(angle_rad)
    sin_ang = math.sin(angle_rad)
    y_new = y * cos_ang - z * sin_ang
    z_new = y * sin_ang + z * cos_ang
    return [x, y_new, z_new]

def project_point(x, y, z, width, height):
    factor = FOV / (CAMERA_DISTANCE + z)
    px = width // 2 + int(x * factor)
    py = height // 2 - int(y * factor)
    return px, py

def generate_flow_mesh(size, stretch_x=2.0, stretch_y=0.7):
    points = []
    for i in range(size):
        for j in range(size):
            x = (i - size / 2) * stretch_x
            y = (j - size / 2) * stretch_y
            z = 0
            points.append([x, y, z])
    return np.array(points, dtype=np.float32)

def update_flow(points, time_sec, speed_factor=1.0):
    for idx, (x, y, _) in enumerate(points):
        z_new = (
            math.sin((x * 0.4 + time_sec * speed_factor)) +
            math.cos((y * 0.6 + time_sec * speed_factor * 0.5)) +
            math.sin((x * 0.3 + y * 0.3 + time_sec * speed_factor * 0.7))
        ) * AMPLITUDE
        points[idx][2] = z_new

# --- Función de luz ---
def compute_light_intensity(px, py, width, height):
    intensity = 0
    for lx, ly, radius, power in LIGHTS:
        lx_px = width // 2 + int(lx * 40)
        ly_px = height // 2 - int(ly * 40)
        dx, dy = px - lx_px, py - ly_px
        dist = math.sqrt(dx * dx + dy * dy)
        if dist < radius * 50:
            intensity += power * (1 - dist / (radius * 50))
    return min(intensity, 1.0)

def apply_lighting(color, alpha, light):
    r, g, b = color
    r = min(255, int(r * (0.5 + light)))
    g = min(255, int(g * (0.5 + light)))
    b = min(255, int(b * (0.5 + light)))
    return (r, g, b, alpha)

def draw_flow(screen, points, size, angle_x_rad, flow_surface):
    global PINK_COLOR
    flow_surface.fill((0, 0, 0, 0))
    width, height = flow_surface.get_size()

    for i in range(size - 1):
        for j in range(size - 1):
            idx = i * size + j
            p0 = points[idx]
            p1 = points[idx + 1]
            p2 = points[idx + size]
            p3 = points[idx + size + 1]

            p0r = rotate_x(p0, angle_x_rad)
            p1r = rotate_x(p1, angle_x_rad)
            p2r = rotate_x(p2, angle_x_rad)
            p3r = rotate_x(p3, angle_x_rad)

            pp0 = project_point(*p0r, width, height)
            pp1 = project_point(*p1r, width, height)
            pp2 = project_point(*p2r, width, height)
            pp3 = project_point(*p3r, width, height)

            cx = (pp0[0] + pp1[0] + pp2[0] + pp3[0]) // 4
            cy = (pp0[1] + pp1[1] + pp2[1] + pp3[1]) // 4
            light = compute_light_intensity(cx, cy, width, height)

            color = apply_lighting(PINK_COLOR[:3], PINK_COLOR[3], light)

            pygame.gfxdraw.filled_polygon(
                flow_surface,
                [pp0, pp1, pp3, pp2],
                color
            )

    screen.blit(flow_surface, (0, 0))

def handle_touch():
    global animation_speed_factor, last_touch_time
    animation_speed_factor = ANIMATION_SPEED_MAX
    last_touch_time = time.time()

def update_animation_speed():
    global animation_speed_factor, last_touch_time
    if last_touch_time is None:
        animation_speed_factor = ANIMATION_SPEED_MIN
        return
    elapsed = time.time() - last_touch_time
    if elapsed > TOUCH_ACCEL_DURATION:
        animation_speed_factor = ANIMATION_SPEED_MIN
    else:
        progress = elapsed / TOUCH_ACCEL_DURATION
        animation_speed_factor = ANIMATION_SPEED_MAX - (ANIMATION_SPEED_MAX - ANIMATION_SPEED_MIN) * progress

class CosmicWave:
    def __init__(self, width, height):
        global PINK_COLOR, BG_TOP, BG_BOTTOM
        self.width = width
        self.height = height
        self.size = MESH_SIZE
        self.angle_x = math.radians(85)
        self.points = generate_flow_mesh(self.size, stretch_x=2.0, stretch_y=0.7)
        self.flow_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        self.gradient_surface = pygame.Surface((width, height))  # Superficie para el gradiente
        self.update_gradient()  # Crear gradiente inicial
        self.start_time = time.time()

    def update_gradient(self):
        """Actualiza el gradiente con los colores actuales."""
        global BG_TOP, BG_BOTTOM
        make_gradient(self.gradient_surface, BG_TOP, BG_BOTTOM)
        print(f"[CosmicWave] Updated gradient: BG_TOP={BG_TOP}, BG_BOTTOM={BG_BOTTOM}")

    def update(self):
        elapsed_time = (time.time() - self.start_time) * BASE_ANIMATION_SPEED
        update_animation_speed()
        update_flow(self.points, elapsed_time, speed_factor=animation_speed_factor)

    def draw(self, surface, *args, **kwargs):
        global PINK_COLOR, BG_TOP, BG_BOTTOM
        if surface.get_width() != self.width or surface.get_height() != self.height:
            self.width, self.height = surface.get_width(), surface.get_height()
            self.flow_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            self.gradient_surface = pygame.Surface((self.width, self.height))
            self.update_gradient()
        surface.blit(self.gradient_surface, (0, 0))  # Dibujar gradiente
        draw_flow(surface, self.points, self.size, self.angle_x, self.flow_surface)

def build_waves(width, height):
    return [CosmicWave(width, height)]

# --- Función para cambiar el color ---
def change_color(index):
    global current_color_index, PINK_COLOR, BG_TOP, BG_BOTTOM
    if 0 <= index < len(COLOR_PRESETS):
        current_color_index = index
        PINK_COLOR = COLOR_PRESETS[current_color_index][0]
        BG_TOP = COLOR_PRESETS[current_color_index][1]
        BG_BOTTOM = COLOR_PRESETS[current_color_index][2]
        print(f"[change_color] Updated colors: PINK_COLOR={PINK_COLOR}, BG_TOP={BG_TOP}, BG_BOTTOM={BG_BOTTOM}")

# ---------- MAIN LOOP ----------
if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((800, 600), pygame.RESIZABLE)
    pygame.display.set_caption("Cosmic Wave - Iluminación Potente")
    clock = pygame.time.Clock()

    waves = build_waves(screen.get_width(), screen.get_height())

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                handle_touch()
            elif event.type == pygame.VIDEORESIZE:
                screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
                waves = build_waves(event.w, event.h)

        # No se usa screen.fill() porque el gradiente se dibuja en CosmicWave.draw()
        for wave in waves:
            wave.update()
            wave.draw(screen)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()