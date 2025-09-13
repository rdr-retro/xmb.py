import pygame
from images import get_image
from utils import make_gradient


def gaussian_blur(surface, scale_factor=0.18, passes=3):
    w, h = surface.get_size()
    if w == 0 or h == 0:
        return surface
    surf = surface.convert_alpha()
    for _ in range(max(1, int(passes))):
        dw = max(1, int(w * scale_factor))
        dh = max(1, int(h * scale_factor))
        down = pygame.transform.smoothscale(surf, (dw, dh))
        surf = pygame.transform.smoothscale(down, (w, h))
    return surf


class ScreenSettings:
    def __init__(self, screen, font, on_resolution_change=None):
        self.screen = screen
        self.base_font = font
        self.on_resolution_change = on_resolution_change
        self.items_main = ["Automáticos", "Personalizados"]

        modes = pygame.display.list_modes()
        if modes == -1 or not modes:
            self.items_resolutions = ["1280x720", "1920x1080", "2560x1440", "3840x2160"]
        else:
            self.items_resolutions = [f"{w}x{h}" for (w, h) in modes]

        mid = (len(self.items_resolutions) + 1) // 2
        self.res_left = self.items_resolutions[:mid]
        self.res_right = self.items_resolutions[mid:]

        self.page = 0
        self.current_index_main = 0
        self.current_res_col = 0
        self.current_res_idx = 0

        self.offset_x = 0.1
        self.start_offset_x = 0.1  # Para animación suave
        self.target_offset_x = 0.1
        self.anim_duration = 0.2  # duración en segundos
        self.anim_time = 0.0  # tiempo animado acumulado

        self.W, self.H = self.screen.get_size()
        self.update_font()
        self.update_arrow()

        self.blur_scale = 0.18
        self.blur_passes = 3

    def update_font(self):
        font_size = int(self.H * 0.04)
        if isinstance(self.base_font, str) or self.base_font is None:
            self.font = pygame.font.SysFont(self.base_font or 'arial', font_size)
        else:
            try:
                self.font = pygame.font.Font(self.base_font.get_default_font(), font_size)
            except AttributeError:
                self.font = pygame.font.SysFont('arial', font_size)

    def update_arrow(self):
        arrow_width = int(self.W * 0.02)
        arrow_height = int(self.H * 0.05)
        arrow_image_orig = get_image("F1F1F1")
        if arrow_image_orig:
            self.arrow_image = pygame.transform.smoothscale(arrow_image_orig, (arrow_width, arrow_height))
        else:
            self.arrow_image = pygame.Surface((arrow_width, arrow_height), pygame.SRCALPHA)
            pygame.draw.polygon(
                self.arrow_image,
                (241, 241, 241),
                [(int(arrow_width * 0.25), int(arrow_height * 0.5)),
                 (int(arrow_width * 0.75), int(arrow_height * 0.1)),
                 (int(arrow_width * 0.75), int(arrow_height * 0.9))]
            )

    def start_animation(self, new_target):
        self.start_offset_x = self.offset_x
        self.target_offset_x = new_target
        self.anim_time = 0.0

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if self.page == 0:
                if event.key == pygame.K_RIGHT:
                    if self.current_index_main == 1:
                        self.page = 1
                        self.current_res_col = 0
                        self.current_res_idx = 0
                        self.start_animation(-self.W)
                elif event.key == pygame.K_LEFT:
                    pass
                elif event.key == pygame.K_ESCAPE:
                    return "exit"
                elif event.key == pygame.K_DOWN:
                    if self.current_index_main < len(self.items_main) - 1:
                        self.current_index_main += 1
                elif event.key == pygame.K_UP:
                    if self.current_index_main > 0:
                        self.current_index_main -= 1
                elif event.key == pygame.K_RETURN:
                    if self.current_index_main == 0:
                        if self.items_resolutions:
                            largest_res = self.items_resolutions[0]
                            width, height = map(int, largest_res.split("x"))
                            flags = self.screen.get_flags() | pygame.FULLSCREEN
                            self.screen = pygame.display.set_mode((width, height), flags)
                            self.W, self.H = self.screen.get_size()
                            self.start_animation(0)
                            self.update_font()
                            self.update_arrow()
                            if callable(self.on_resolution_change):
                                try:
                                    self.on_resolution_change(self.W, self.H)
                                except Exception as e:
                                    print(f"Error en on_resolution_change: {e}")
                    elif self.current_index_main == 1:
                        self.page = 1
                        self.current_res_col = 0
                        self.current_res_idx = 0
                        self.start_animation(-self.W)

            elif self.page == 1:
                current_list = self.res_left if self.current_res_col == 0 else self.res_right
                max_idx = len(current_list) - 1
                if event.key == pygame.K_RIGHT:
                    if self.current_res_col == 0 and len(self.res_right) > 0:
                        self.current_res_col = 1
                        if self.current_res_idx >= len(self.res_right):
                            self.current_res_idx = len(self.res_right) - 1
                elif event.key == pygame.K_LEFT:
                    if self.current_res_col == 1:
                        self.current_res_col = 0
                        if self.current_res_idx >= len(self.res_left):
                            self.current_res_idx = len(self.res_left) - 1
                    else:
                        self.page = 0
                        self.current_index_main = 1
                        self.start_animation(0)
                elif event.key == pygame.K_ESCAPE:
                    self.page = 0
                    self.current_index_main = 1
                    self.start_animation(0)
                elif event.key == pygame.K_DOWN:
                    if self.current_res_idx < max_idx:
                        self.current_res_idx += 1
                elif event.key == pygame.K_UP:
                    if self.current_res_idx > 0:
                        self.current_res_idx -= 1
                elif event.key == pygame.K_RETURN:
                    selected = current_list[self.current_res_idx]
                    print(f"Resolución seleccionada: {selected}")
                    self.apply_resolution(selected)

    def apply_resolution(self, resolution_str):
        width, height = map(int, resolution_str.split("x"))
        flags = self.screen.get_flags()
        is_fullscreen = (flags & pygame.FULLSCREEN) != 0
        if is_fullscreen:
            no_fs_flags = flags & ~pygame.FULLSCREEN
            self.screen = pygame.display.set_mode((width, height), no_fs_flags)
            self.W, self.H = self.screen.get_size()
            fs_flags = no_fs_flags | pygame.FULLSCREEN
            self.screen = pygame.display.set_mode((width, height), fs_flags)
            self.W, self.H = self.screen.get_size()
        else:
            self.screen = pygame.display.set_mode((width, height), flags)
            self.W, self.H = self.screen.get_size()

        if self.page == 0:
            self.start_animation(0)
        else:
            self.start_animation(-self.W)

        self.update_font()
        self.update_arrow()

        if callable(self.on_resolution_change):
            try:
                self.on_resolution_change(self.W, self.H)
            except Exception as e:
                print(f"Error en on_resolution_change: {e}")

    def update(self, dt):
        if self.offset_x == self.target_offset_x:
            return

        self.anim_time += dt
        t = min(self.anim_time / self.anim_duration, 1.0)  # Normalizado [0,1]

        # Interpolación lineal entre start_offset_x y target_offset_x
        self.offset_x = (1 - t) * self.start_offset_x + t * self.target_offset_x

        if t >= 1.0:
            self.offset_x = self.target_offset_x

    def draw(self, waves, W, H, t):
        background = pygame.Surface((self.W, self.H), pygame.SRCALPHA)
        make_gradient(background, (50, 0, 80), (20, 0, 40))
        for w in waves:
            w.draw(background, self.W, self.H, t)
        blurred = gaussian_blur(background, self.blur_scale, self.blur_passes)
        self.screen.blit(blurred, (0, 0))

        color = (200, 200, 200)
        margin_y = int(self.H * 0.1)
        pygame.draw.line(self.screen, color, (0, margin_y), (self.W, margin_y), 2)
        pygame.draw.line(self.screen, color, (0, self.H - margin_y), (self.W, self.H - margin_y), 2)

        title_surf = self.font.render("Ajustes de salida de video", True, (255, 255, 255))
        title_rect = title_surf.get_rect(topleft=(int(self.W * 0.05), int(self.H * 0.05)))
        self.screen.blit(title_surf, title_rect)

        x_base_main = self.W // 2 + int(self.offset_x)
        spacing_vertical = int(self.H * 0.005)
        total_height_main = sum(self.font.size(i)[1] for i in self.items_main) + spacing_vertical * (len(self.items_main) - 1)
        start_y = (self.H - total_height_main) // 2
        current_y = start_y
        for idx, item in enumerate(self.items_main):
            color = (255, 255, 0) if (self.page == 0 and idx == self.current_index_main) else (255, 255, 255)
            txt = self.font.render(item, True, color)
            rect = txt.get_rect(center=(x_base_main, current_y + txt.get_height() // 2))
            self.screen.blit(txt, rect)

            if self.page == 0 and idx == self.current_index_main == 1:
                arrow_rect = self.arrow_image.get_rect()
                arrow_rect.centery = rect.centery
                arrow_rect.right = self.W - int(self.W * 0.02)
                arrow_rotated = pygame.transform.rotate(self.arrow_image, 180)
                self.screen.blit(arrow_rotated, arrow_rect)

            current_y += txt.get_height() + spacing_vertical

        x_base_res = int(self.offset_x) + self.W
        spacing = int(self.H * 0.02)

        total_height_left = sum(self.font.size(res)[1] for res in self.res_left) + spacing * (len(self.res_left) - 1)
        start_y_left = (self.H - total_height_left) // 2
        y = start_y_left
        x_left = x_base_res + int(self.W * 0.33)
        for idx, res in enumerate(self.res_left):
            color = (255, 255, 0) if (self.page == 1 and self.current_res_col == 0 and idx == self.current_res_idx) else (255, 255, 255)
            txt = self.font.render(res, True, color)
            rect = txt.get_rect(center=(x_left, y + txt.get_height() // 2))
            self.screen.blit(txt, rect)
            y += txt.get_height() + spacing

        total_height_right = sum(self.font.size(res)[1] for res in self.res_right) + spacing * (len(self.res_right) - 1)
        start_y_right = (self.H - total_height_right) // 2
        y = start_y_right
        x_right = x_base_res + int(self.W * 0.66)
        for idx, res in enumerate(self.res_right):
            color = (255, 255, 0) if (self.page == 1 and self.current_res_col == 1 and idx == self.current_res_idx) else (255, 255, 255)
            txt = self.font.render(res, True, color)
            rect = txt.get_rect(center=(x_right, y + txt.get_height() // 2))
            self.screen.blit(txt, rect)
            y += txt.get_height() + spacing

        if self.page == 1:
            arrow_rect = self.arrow_image.get_rect()
            arrow_rect.centery = self.H // 2
            arrow_rect.left = int(self.W * 0.02)
            arrow_rotated = pygame.transform.rotate(self.arrow_image, 0)
            self.screen.blit(arrow_rotated, arrow_rect)
