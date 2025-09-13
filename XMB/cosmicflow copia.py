import pygame
import numpy as np
import math
import time

WIDTH, HEIGHT = 800, 600
FPS = 60

MESH_SIZE = 100
BASE_ANIMATION_SPEED = 0.6
AMPLITUDE = 8

FOV = 256
CAMERA_DISTANCE = 70

# Color rosa translúcido (RGBA)
PINK_COLOR = (255, 105, 180, 120)  # Hot pink con alpha 120

BACKGROUND_COLOR = (10, 10, 30)

ANIMATION_SPEED_MAX = 1.0
ANIMATION_SPEED_MIN = 0.5
TOUCH_ACCEL_DURATION = 3.0

animation_speed_factor = ANIMATION_SPEED_MIN
last_touch_time = None


def rotate_x(point, angle_rad):
    x, y, z = point
    cos_ang = math.cos(angle_rad)
    sin_ang = math.sin(angle_rad)
    y_new = y * cos_ang - z * sin_ang
    z_new = y * sin_ang + z * cos_ang
    return [x, y_new, z_new]


def rotate_y(point, angle_rad):
    x, y, z = point
    cos_ang = math.cos(angle_rad)
    sin_ang = math.sin(angle_rad)
    x_new = x * cos_ang + z * sin_ang
    z_new = -x * sin_ang + z * cos_ang
    return [x_new, y, z_new]


def project_point(x, y, z):
    factor = FOV / (CAMERA_DISTANCE + z)
    px = WIDTH // 2 + int(x * factor)
    py = HEIGHT // 2 - int(y * factor)
    return px, py


def generate_flow_mesh(size):
    points = []
    for i in range(size):
        for j in range(size):
            x = (i - size / 2)
            y = (j - size / 2) * 0.7
            z = 0
            points.append([x, y, z])
    return np.array(points, dtype=np.float32)


def update_flow(points, time_sec, speed_factor=1.0):
    for idx, (x, y, z) in enumerate(points):
        z_new = (
            math.sin((x * 0.4 + time_sec * speed_factor)) +
            math.cos((y * 0.6 + time_sec * speed_factor * 0.5)) +
            math.sin((x * 0.3 + y * 0.3 + time_sec * speed_factor * 0.7))
        ) * AMPLITUDE
        points[idx][2] = z_new


def draw_flow(screen, points, size, angle_x_rad, angle_y_rad, flow_surface):
    flow_surface.fill((0, 0, 0, 0))  # Limpiar superficie con transparencia

    for i in range(size - 1):
        for j in range(size - 1):
            idx = i * size + j

            # Obtener 4 puntos vecinos para un rectángulo
            p0 = points[idx]
            p1 = points[idx + 1]
            p2 = points[idx + size]
            p3 = points[idx + size + 1]

            # Rotar cada punto
            p0r = rotate_y(rotate_x(p0, angle_x_rad), angle_y_rad)
            p1r = rotate_y(rotate_x(p1, angle_x_rad), angle_y_rad)
            p2r = rotate_y(rotate_x(p2, angle_x_rad), angle_y_rad)
            p3r = rotate_y(rotate_x(p3, angle_x_rad), angle_y_rad)

            # Proyectar a 2D
            pp0 = project_point(*p0r)
            pp1 = project_point(*p1r)
            pp2 = project_point(*p2r)
            pp3 = project_point(*p3r)

            # Dibujar dos triángulos para formar el rectángulo rellenado
            pygame.gfxdraw.filled_trigon(flow_surface, pp0[0], pp0[1], pp1[0], pp1[1], pp2[0], pp2[1], PINK_COLOR)
            pygame.gfxdraw.filled_trigon(flow_surface, pp1[0], pp1[1], pp2[0], pp2[1], pp3[0], pp3[1], PINK_COLOR)

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


def main():
    global animation_speed_factor

    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Cosmic Flow con superficie rosa translúcida")
    clock = pygame.time.Clock()

    points = generate_flow_mesh(MESH_SIZE)

    # Superficie con canal alfa para dibujar poligonos translucidos
    global flow_surface
    flow_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)

    angle_x_rad = math.radians(85)
    angle_y_rad = 0

    running = True
    start_time = time.time()

    while running:
        elapsed_time = (time.time() - start_time) * BASE_ANIMATION_SPEED

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                handle_touch()

        update_animation_speed()
        update_flow(points, elapsed_time, speed_factor=animation_speed_factor)

        angle_y_rad += 0.002

        screen.fill(BACKGROUND_COLOR)
        draw_flow(screen, points, MESH_SIZE, angle_x_rad, angle_y_rad, flow_surface)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()


# Necesita importar pygame.gfxdraw para rellenar triángulos
import pygame.gfxdraw

if __name__ == "__main__":
    main()
