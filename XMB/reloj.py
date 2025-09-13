import pygame
import time
import math
from pygame import gfxdraw
import random

# --- Colores ---
COLOR_BG = (10, 10, 30)
COLOR_CLOCK_BG = (255, 255, 255, 50)  # transparente y ligeramente blanco
COLOR_HOUR = (220, 220, 220)
COLOR_MINUTE = (220, 220, 220)
COLOR_SECOND = (220, 220, 220)
COLOR_MARK = (200, 200, 200)
COLOR_CENTER = (255, 255, 255)  # blanco sólido
COLOR_NUM = (220, 220, 220)
COLOR_SECOND_MARK = (255, 255, 255)  # color de rallitas pequeñas

# --- Configuración del rastro ---
FADE_SPEED = 2        # más bajo = se apaga más lento
MARK_COUNT = 120      # más densidad (120 = cada 0.5 segundos)
TRAIL_LENGTH = 6      # cantidad de marcas que deja encendidas detrás
TRAIL_FADE_STEP = 40  # cuánto pierde de brillo cada paso atrás en la estela

# Inicializar lista de intensidades (0 = invisible, 255 = visible)
second_marks_alpha = [0 for _ in range(MARK_COUNT)]

def draw_fondo(screen):
    """Fondo dinámico tipo bokeh/lupa"""
    W, H = screen.get_size()
    fondo_surf = pygame.Surface((W, H), pygame.SRCALPHA)
    for _ in range(40):
        radius = random.randint(50, 150)
        x = random.randint(0, W)
        y = random.randint(0, H)
        alpha = random.randint(20, 60)
        color = (255, 255, 255, alpha)
        gfxdraw.filled_circle(fondo_surf, x, y, radius, color)
        gfxdraw.aacircle(fondo_surf, x, y, radius, color)
    screen.blit(fondo_surf, (0, 0))

def draw_lupa(screen, center, radius, zoom=1.2):
    """Crea el efecto lupa ampliando el fondo dentro del círculo"""
    rect = pygame.Rect(center[0]-radius, center[1]-radius, radius*2, radius*2)
    sub = screen.subsurface(rect).copy()
    size = int(radius*2*zoom)
    sub = pygame.transform.smoothscale(sub, (size, size))
    circle_surf = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)
    circle_surf.blit(sub, ((radius*2 - size)//2, (radius*2 - size)//2))
    mask = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)
    pygame.draw.circle(mask, (255,255,255,255), (radius,radius), radius)
    circle_surf.blit(mask, (0,0), special_flags=pygame.BLEND_RGBA_MIN)
    screen.blit(circle_surf, (center[0]-radius, center[1]-radius))

def draw_screen_lines(surface, center, radius, line_spacing=8, line_thickness=2, line_color=(255,255,255,30)):
    """Dibuja líneas horizontales más gruesas dentro del reloj para efecto pantalla"""
    lines_surf = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)
    for y in range(0, int(radius*2), line_spacing):
        pygame.draw.line(lines_surf, line_color, (0, y), (radius*2, y), line_thickness)
    # Crear máscara circular
    mask = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)
    pygame.draw.circle(mask, (255,255,255,255), (radius,radius), int(radius))
    lines_surf.blit(mask, (0,0), special_flags=pygame.BLEND_RGBA_MIN)
    surface.blit(lines_surf, (center[0]-radius, center[1]-radius))

def draw_reloj(screen):
    global second_marks_alpha

    W, H = screen.get_size()
    
    # --- Tiempo preciso ---
    t = time.time()
    now = time.localtime(t)
    frac_seconds = t % 60  # segundos con decimales
    hours = now.tm_hour % 12
    minutes = now.tm_min

    clock_radius = min(W, H) * 0.45
    center = (W // 2, H // 2)

    # --- Fondo lupa ---
    draw_lupa(screen, center, int(clock_radius), zoom=1.3)

    # --- Círculo principal transparente y blanco ---
    clock_surface = pygame.Surface((W, H), pygame.SRCALPHA)
    gfxdraw.filled_circle(clock_surface, center[0], center[1], int(clock_radius), COLOR_CLOCK_BG)

    # --- Marcas de horas ---
    mark_length = clock_radius * 0.25
    special_hours = [0,3,6,9]
    mark_width = 20
    for i in range(12):
        if i in special_hours:
            continue
        angle = math.radians(i*30 - 90)
        inner_radius = clock_radius - mark_length
        outer_radius = clock_radius
        x_inner = int(center[0] + inner_radius * math.cos(angle))
        y_inner = int(center[1] + inner_radius * math.sin(angle))
        x_outer = int(center[0] + outer_radius * math.cos(angle))
        y_outer = int(center[1] + outer_radius * math.sin(angle))
        dx = x_outer - x_inner
        dy = y_outer - y_inner
        length = math.hypot(dx, dy)
        angle_deg = math.degrees(math.atan2(dy, dx))
        mark_surf = pygame.Surface((length, mark_width), pygame.SRCALPHA)
        pygame.draw.rect(mark_surf, COLOR_MARK, (0,0,length,mark_width), border_radius=mark_width//2)
        mark_surf = pygame.transform.rotate(mark_surf, -angle_deg)
        rect = mark_surf.get_rect(center=((x_inner+x_outer)//2, (y_inner+y_outer)//2))
        clock_surface.blit(mark_surf, rect)

    # --- Números ---
    font = pygame.font.Font(None,100)
    numbers = {0:"12",3:"3",6:"6",9:"9"}
    for i,num in numbers.items():
        angle = math.radians(i*30-90)
        text = font.render(num, True, COLOR_NUM)
        rect = text.get_rect()
        radius_num = clock_radius - 40
        rect.center = (int(center[0]+radius_num*math.cos(angle)), int(center[1]+radius_num*math.sin(angle)))
        clock_surface.blit(text, rect)

    # --- Líneas finas horizontales efecto pantalla ---
    draw_screen_lines(clock_surface, center, int(clock_radius))

    # --- Pequeñas marcas de segundos (más largas y con rastro difuminado) ---
    for i in range(MARK_COUNT):
        angle = math.radians(i*(360/MARK_COUNT) - 90)
        inner = clock_radius - 25   # más hacia dentro
        outer = clock_radius - 2    # más hacia fuera
        x_inner = int(center[0] + inner*math.cos(angle))
        y_inner = int(center[1] + inner*math.sin(angle))
        x_outer = int(center[0] + outer*math.cos(angle))
        y_outer = int(center[1] + outer*math.sin(angle))

        # dibujar solo si tiene alpha > 0
        alpha = max(0, min(255, second_marks_alpha[i]))
        if alpha > 0:
            color = (*COLOR_SECOND_MARK[:3], alpha)
            pygame.draw.line(clock_surface, color, (x_inner, y_inner), (x_outer, y_outer), 2)

        # desvanecer poco a poco
        second_marks_alpha[i] = max(0, alpha - FADE_SPEED)

    # --- Agujas ---
    second_angle = math.radians(frac_seconds*6 - 90)
    minute_angle = math.radians(minutes*6 - 90 + (frac_seconds/60)*6)
    hour_angle = math.radians(hours*30 - 90 + (minutes/60)*30)

    def draw_hand(surface, center, angle, length, color, width=6):
        """Dibuja aguja con extremos redondeados"""
        end = (int(center[0]+length*math.cos(angle)), int(center[1]+length*math.sin(angle)))
        pygame.draw.line(surface, color, center, end, width)
        pygame.draw.circle(surface, color, end, width//2)  # extremo redondeado
        return end

    # Agujas más gruesas
    draw_hand(clock_surface, center, hour_angle, clock_radius*0.5, COLOR_HOUR, 12)
    draw_hand(clock_surface, center, minute_angle, clock_radius*0.7, COLOR_MINUTE, 8)
    end_second = draw_hand(clock_surface, center, second_angle, clock_radius*0.95, COLOR_SECOND, 4)

    # --- Activar marca de segundos actual con estela difuminada ---
    current_index = int(frac_seconds * (MARK_COUNT/60)) % MARK_COUNT
    for offset in range(0, TRAIL_LENGTH):
        idx = (current_index - offset) % MARK_COUNT
        # calcular brillo decreciente según offset
        intensity = max(0, 255 - offset * TRAIL_FADE_STEP)
        second_marks_alpha[idx] = max(second_marks_alpha[idx], intensity)

    # --- Centro más grande y totalmente blanco (sin borde) ---
    pygame.draw.circle(clock_surface, COLOR_CENTER, center, 15)

    screen.blit(clock_surface, (0,0))

def main():
    pygame.init()
    screen = pygame.display.set_mode((800,800))
    pygame.display.set_caption("Reloj PSP Vita con Estela Difuminada")
    clock = pygame.time.Clock()
    running = True

    while running:
        screen.fill(COLOR_BG)
        draw_fondo(screen)
        draw_reloj(screen)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT or event.type == pygame.KEYDOWN:
                running = False

        clock.tick(60)  # FPS alto para animación suave

    pygame.quit()

if __name__ == "__main__":
    main()
