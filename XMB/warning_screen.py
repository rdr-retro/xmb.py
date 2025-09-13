import sys, time, datetime, math
import pygame
from PIL import Image, ImageFilter
import numpy as np
from utils import make_gradient, month_color, render_multiline_text_surface, clamp, sample_spline

# --- Clase de ola rellena ---
class FilledWave:
    def __init__(self, base_y, speed, amp1, amp2, color, alpha=255):
        self.base_y = base_y
        self.speed = speed
        self.amp1 = amp1
        self.amp2 = amp2
        self.color = color
        self.alpha = alpha

    def make_points(self, W, t, segs=6, samples=120):
        ctrl = []
        for i in range(segs + 1):
            x = i * (W / segs)
            y = self.base_y + self.amp1 * math.sin((x * 0.004) + (t * self.speed * 0.02)) \
                                  + self.amp2 * math.sin((x * 0.009) - (t * self.speed * 0.015))
            ctrl.append((x, y))
        return sample_spline([ctrl[0]] + ctrl + [ctrl[-1]], samples)

    def draw(self, surface, W, H, t):
        pts = self.make_points(W, t)
        poly = pts + [(W, H), (0, H)]
        s = pygame.Surface((W, H), pygame.SRCALPHA)
        pygame.draw.polygon(s, (*self.color, self.alpha), poly)
        surface.blit(s, (0, 0))

def apply_blur(surf, radius=4):
    """Aplica desenfoque usando PIL"""
    arr = pygame.image.tostring(surf, "RGBA", False)
    img = Image.frombytes("RGBA", surf.get_size(), arr)
    img = img.filter(ImageFilter.GaussianBlur(radius))
    return pygame.image.fromstring(img.tobytes(), img.size, "RGBA")

def show_warning(screen, font):
    W, H = screen.get_size()
    warning_text = (
        "SOBRE LA EPILEPSIA FOTOSENSIBLE\n\n"
        "SI HA PADECIDO EPISODIOS PREVIOS DE EPILEPSIA O CONVULSIONES, CONSULTE A SU MÉDICO ANTES DE UTILIZAR ESTE PRODUCTO. "
        "CIERTOS PATRONES LUMÍNICOS PUEDEN PROVOCAR CONVULSIONES A USUARIOS QUE NO TENGAN UN HISTORIAL PREVIO. "
        "ANTES DE UTILIZAR ESTE PRODUCTO, LEA EL MANUAL DE INSTRUCCIONES DETENIDAMENTE."
    )

    # Inicializar mixer y reproducir sonido startup
    pygame.mixer.init()
    try:
        pygame.mixer.music.load("sounds/startup.mp3")
        pygame.mixer.music.play()
    except Exception as e:
        print(f"Error cargando o reproduciendo sonido: {e}")

    aviso_duracion = 4.0
    aviso_fade_time = 0.7
    aviso_start = time.perf_counter()
    clock = pygame.time.Clock()

    # Crear olas de fondo
    base_color = month_color(datetime.datetime.now())
    wave1 = FilledWave(H * 0.55, 20, 40, 16, base_color, alpha=255)
    darker = tuple(clamp(int(c * 0.7), 0, 255) for c in base_color)
    wave2 = FilledWave(H * 0.58, 15, 32, 12, darker, alpha=160)
    waves = [wave1, wave2]

    t0 = time.perf_counter()
    show_warning_flag = True

    while show_warning_flag:
        dt = clock.tick(60) / 1000.0
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif e.type == pygame.KEYDOWN or e.type == pygame.MOUSEBUTTONDOWN:
                show_warning_flag = False

        now = datetime.datetime.now()
        bg = month_color(now)
        bg_bottom = tuple(int(c * 0.55) for c in bg)
        make_gradient(screen, bg, bg_bottom)

        wave_layer = pygame.Surface((W, H), pygame.SRCALPHA)
        t = time.perf_counter() - t0
        for w in waves:
            w.draw(wave_layer, W, H, t)

        blurred = apply_blur(wave_layer, radius=6)
        screen.blit(blurred, (0, 0))

        overlay = pygame.Surface((W, H), pygame.SRCALPHA)
        overlay.fill((15, 15, 15, 170))
        screen.blit(overlay, (0, 0))

        text_surf = render_multiline_text_surface(warning_text, font, (255, 255, 255), int(W * 0.92))
        scale_factor = min(W * 0.9 / text_surf.get_width(), H * 0.65 / text_surf.get_height())
        new_size = (int(text_surf.get_width() * scale_factor), int(text_surf.get_height() * scale_factor))
        scaled_text = pygame.transform.smoothscale(text_surf, new_size)
        x = (W - scaled_text.get_width()) // 2
        y = (H - scaled_text.get_height()) // 2

        elapsed = time.perf_counter() - aviso_start
        alpha = 255
        if elapsed > aviso_duracion - aviso_fade_time:
            alpha = int(255 * max(0, (aviso_duracion - elapsed) / aviso_fade_time))
        if elapsed > aviso_duracion:
            break

        scaled_text.set_alpha(alpha)
        screen.blit(scaled_text, (x, y))

        pygame.display.flip()
