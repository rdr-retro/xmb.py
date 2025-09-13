import sys
import time
import pygame
from utils import clamp  # Assuming utils.py has clamp
from warning_screen import show_warning
from xmbparte2 import XMBMenu
from wave import build_waves, change_color, COLOR_PRESETS
from screen import ScreenSettings
from theme import open_theme_settings  # Import open_theme_settings

# ---------------- CONFIG ----------------
FPS = 500
pygame.init()
clock = pygame.time.Clock()

# ---------------- FUENTES ----------------
try:
    font = pygame.font.Font("FOT-NewRodin Pro DB.otf", 22)
except Exception as e:
    print(f"[Error] No se pudo cargar la fuente 'FOT-NewRodin Pro DB.otf': {e}")
    font = pygame.font.SysFont(None, 22)  # Fallback to default system font
    print("[Info] Usando fuente del sistema por defecto")

fps_font = pygame.font.SysFont("Consolas", 18)  # FPS font remains unchanged

# ---------------- SONIDO MENÚ OSCURO ----------------
dark_menu_sound = None
try:
    pygame.mixer.init()
    dark_menu_sound = pygame.mixer.Sound("sounds/snd_system_ok.wav")
except Exception as e:
    print(f"⚠️ Error cargando sonido del menú oscuro: {e}")

# ---------------- MENÚ OSCURO INICIAL ----------------
def ask_fullscreen(screen, font):
    options = ["Pantalla completa: Sí", "Pantalla completa: No"]
    selected = 0

    overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))

    line_color = (200, 200, 200, 180)
    line_surf = pygame.Surface((screen.get_width(), 2), pygame.SRCALPHA)
    line_surf.fill(line_color)

    if dark_menu_sound:
        try:
            dark_menu_sound.play()
        except Exception as e:
            print(f"[Error] No se pudo reproducir el sonido del menú oscuro: {e}")

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key in [pygame.K_UP, pygame.K_DOWN]:
                    selected = (selected + 1) % 2
                elif event.key in [pygame.K_RETURN, pygame.K_KP_ENTER]:
                    return selected == 0

        screen.blit(overlay, (0, 0))
        top_y = int(screen.get_height() * 0.1)
        bottom_y = int(screen.get_height() * 0.9)

        screen.blit(line_surf, (0, top_y))
        screen.blit(line_surf, (0, bottom_y))

        # ✅ Solo mostrar opciones
        for i, opt in enumerate(options):
            color = (0, 255, 0) if i == selected else (200, 200, 200)
            try:
                txt = font.render(opt, True, color)
                rect = txt.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2 + i * 60))
                screen.blit(txt, rect)
            except Exception as e:
                print(f"[Error] No se pudo renderizar texto con la fuente: {e}")

        pygame.display.flip()
        clock.tick(60)

# ---------------- CONFIG PANTALLA ----------------
def init_screen():
    preview_flags = pygame.SCALED | pygame.DOUBLEBUF
    try:
        preview_screen = pygame.display.set_mode((1280, 720), preview_flags)
        pygame.display.set_caption("PS3 Waves Purple Theme")
    except Exception as e:
        print(f"[Error] No se pudo inicializar la pantalla de vista previa: {e}")
        pygame.quit()
        sys.exit()

    fullscreen = ask_fullscreen(preview_screen, font)

    if fullscreen:
        info = pygame.display.Info()
        W, H = info.current_w, info.current_h
        flags = pygame.FULLSCREEN | pygame.SCALED | pygame.DOUBLEBUF
        try:
            flags |= pygame.VSYNC
        except AttributeError:
            flags |= 1
            print("[Info] VSYNC no soportado, usando bandera alternativa")
    else:
        W, H = 1280, 720
        flags = pygame.SCALED | pygame.DOUBLEBUF

    try:
        screen = pygame.display.set_mode((W, H), flags)
        pygame.display.set_caption("PS3 Waves Purple Theme")
    except Exception as e:
        print(f"[Error] No se pudo inicializar la pantalla principal: {e}")
        pygame.quit()
        sys.exit()

    return screen, W, H

# ---------------- CALLBACK DE RESOLUCIÓN ----------------
def on_resolution_change(new_w, new_h):
    global W, H, waves, screen, theme_settings
    try:
        W, H = int(new_w), int(new_h)
        screen = pygame.display.set_surface()
        if screen is None:
            screen = pygame.display.set_mode((W, H))
        waves = build_waves(W, H)
        if theme_settings:
            theme_settings.width, theme_settings.height = W, H
            theme_settings.panel_width = int(W * 0.4)
            theme_settings.start_animation()
        print(f"[on_resolution_change] Resolución cambiada a {W}x{H}")
    except Exception as e:
        print(f"[Error] Error en on_resolution_change: {e}")

# ---------------- MAIN ----------------
if __name__ == "__main__":
    try:
        screen, W, H = init_screen()
    except Exception as e:
        print(f"[Error] No se pudo inicializar la pantalla: {e}")
        pygame.quit()
        sys.exit()

    # Aviso inicial
    try:
        show_warning(screen, font)
    except Exception as e:
        print(f"[Error] No se pudo mostrar la pantalla de advertencia: {e}")

    # Menú XMB con opción de Themes
    xmb_items = {
        "Juegos": ["PS2", "PS3", "PSP"],
        "Fotos": ["Álbum", "Capturas"],
        "Música": ["Biblioteca", "Listas"],
        "Videos": ["Películas", "Clips"],
        "Ajustes": ["Red", "Pantalla", "Sonido", "Themes"]
    }
    try:
        xmb_menu = XMBMenu(screen, font, xmb_items)
    except Exception as e:
        print(f"[Error] No se pudo inicializar XMBMenu: {e}")
        pygame.quit()
        sys.exit()

    # Configuración de pantalla
    try:
        if hasattr(xmb_menu, "screen_settings") and xmb_menu.screen_settings:
            xmb_menu.screen_settings.on_resolution_change = on_resolution_change
        else:
            xmb_menu.screen_settings = ScreenSettings(screen, font, on_resolution_change=on_resolution_change)
    except Exception as e:
        print(f"[Error] No se pudo configurar ScreenSettings: {e}")

    # Crear olas
    try:
        waves = build_waves(W, H)
    except Exception as e:
        print(f"[Error] No se pudo construir las olas: {e}")
        pygame.quit()
        sys.exit()

    # Estado para manejar ThemeSettings
    theme_settings = None

    # ---------------- LOOP PRINCIPAL ----------------
    t0 = time.perf_counter()
    running = True
    fps_smooth = 60  # valor inicial

    while running:
        dt = clock.tick(FPS) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            else:
                print(f"[main] Processing event: {event.type}")
                if theme_settings is not None:
                    # Handle ThemeSettings events
                    try:
                        result = theme_settings.handle_event(event)
                        if result == "exit":
                            print(f"[main] ThemeSettings closed, returning to XMB")
                            theme_settings = None
                            xmb_menu.state = "menu"  # Set to "menu" to ensure XMB rendering
                            xmb_menu.update(dt)  # Update XMB state
                            print(f"[main] XMB state set to 'menu'")
                        else:
                            # Update gradients after every theme selection
                            for wave in waves:
                                wave.update_gradient()
                            print(f"[main] Gradients updated after theme selection")
                    except Exception as e:
                        print(f"[Error] Error procesando eventos de ThemeSettings: {e}")
                else:
                    # Pass events to XMBMenu
                    try:
                        xmb_menu.handle_event(event)
                        print(f"[main] XMB state: {xmb_menu.state}")
                        # Check if Themes is selected
                        if xmb_menu.state == "show_theme_settings":
                            theme_settings = open_theme_settings(screen, font)
                            print(f"[main] Opened ThemeSettings")
                    except Exception as e:
                        print(f"[Error] Error procesando eventos de XMBMenu: {e}")

        # Detectar resize externo
        try:
            current_size = screen.get_size()
            if (current_size[0] != W) or (current_size[1] != H):
                W, H = current_size
                waves = build_waves(W, H)
                if xmb_menu.screen_settings:
                    xmb_menu.screen_settings.W, xmb_menu.screen_settings.H = W, H
                if theme_settings:
                    theme_settings.width, theme_settings.height = W, H
                    theme_settings.panel_width = int(W * 0.4)
                    theme_settings.start_animation()
                xmb_menu.update_layout()  # Update XMB layout on resize
                print(f"[main] Cambio de tamaño -> {W}x{H}")
        except Exception as e:
            print(f"[Error] Error detectando cambio de tamaño: {e}")

        t = time.perf_counter() - t0

        # Dibujar olas (incluye el gradiente de fondo)
        try:
            for w in waves:
                w.update()
                w.draw(screen, W, H, t)
                print(f"[main] Waves drawn")
        except Exception as e:
            print(f"[Error] Error dibujando olas: {e}")

        # Dibujar menú o configuración
        try:
            if theme_settings is not None:
                theme_settings.update(dt)
                theme_settings.draw(W, H, t)
                print(f"[main] ThemeSettings drawn")
            elif xmb_menu.state == "show_screen_settings" and xmb_menu.screen_settings:
                xmb_menu.screen_settings.update(dt)
                xmb_menu.screen_settings.draw(waves, W, H, t)
                print(f"[main] ScreenSettings drawn")
            else:
                xmb_menu.update(dt)
                xmb_menu.draw()
                print(f"[main] XMB menu drawn, state: {xmb_menu.state}")
        except Exception as e:
            print(f"[Error] Error dibujando menú/configuración: {e}")

        # FPS suavizado
        try:
            raw_fps = clock.get_fps()
            fps_smooth = 0.9 * fps_smooth + 0.1 * raw_fps
            fps = int(fps_smooth)

            if fps >= 58:
                fps_color = (0, 255, 0)
            elif fps >= 40:
                fps_color = (255, 200, 0)
            else:
                fps_color = (255, 0, 0)

            fps_text = fps_font.render(f"FPS: {fps}", True, fps_color)
            screen.blit(fps_text, (10, 10))
        except Exception as e:
            print(f"[Error] Error renderizando FPS: {e}")

        try:
            pygame.display.flip()
            print(f"[main] Frame rendered, FPS: {fps}")
        except Exception as e:
            print(f"[Error] Error actualizando pantalla: {e}")

    pygame.quit()
    sys.exit()