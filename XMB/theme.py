import pygame

# Assuming change_color is defined in wave.py
try:
    from wave import change_color
except ImportError:
    print("[Error] Could not import change_color from wave.py")
    # Mock function for testing purposes
    def change_color(index):
        print(f"[Mock] Changing color to index {index}")

class ThemeSettings:
    def __init__(self, screen, font):
        self.screen = screen
        self.font = font
        self.width, self.height = screen.get_size()

        # Define theme colors (RGB tuples) corresponding to each theme
        self.theme_colors = [
            (255, 105, 180),  # Pink
            (0, 0, 255),      # Blue
            (0, 255, 0),      # Green
            (255, 0, 0),      # Red
            (0, 255, 255),    # Cyan
            (255, 255, 0),    # Yellow
            (128, 0, 128),    # Purple
            (255, 165, 0),    # Orange
            (0, 128, 128),    # Teal
            (255, 0, 255)     # Magenta
        ]

        # Options list (10 color themes)
        self.options = [
            "Pink Theme",
            "Blue Theme",
            "Green Theme",
            "Red Theme",
            "Cyan Theme",
            "Yellow Theme",
            "Purple Theme",
            "Orange Theme",
            "Teal Theme",
            "Magenta Theme"
        ]
        self.current_index = 0  # Selected option index

        # Animation settings for the sweep effect
        self.panel_offset_x = self.width  # Start off-screen to the right
        self.target_offset_x = self.width * 0.6  # Panel covers 40% of screen from right
        self.anim_duration = 0.5  # Animation duration in seconds
        self.anim_time = 0.0  # Accumulated animation time
        self.is_animating = False  # Animation state

        # Panel properties
        self.panel_width = int(self.width * 0.4)  # 40% of screen width
        self.panel_alpha = 128  # Semi-transparent (0-255)
        self.color_square_size = 30  # Size of the color square
        self.color_square_margin = 10  # Margin between square and text

        # Pre-render text surfaces for performance
        self.text_surfaces = []
        for option in self.options:
            text = self.font.render(option, True, (255, 255, 255))  # White text
            self.text_surfaces.append(text)

    def start_animation(self):
        """Start the panel sweep-in animation."""
        self.anim_time = 0.0
        self.panel_offset_x = self.width  # Start off-screen
        self.is_animating = True

    def update(self, dt):
        """Update the animation state based on elapsed time (dt in seconds)."""
        if self.is_animating and self.anim_time < self.anim_duration:
            self.anim_time += dt
            t = min(self.anim_time / self.anim_duration, 1.0)  # Normalize [0,1]
            # Quadratic ease-in-out for smooth animation
            t = t * t * (3 - 2 * t)
            self.panel_offset_x = self.width - (self.width - self.target_offset_x) * t
            if t >= 1.0:
                self.is_animating = False
                self.panel_offset_x = self.target_offset_x

    def handle_event(self, event):
        """Handle user input events."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                print(f"[ThemeSettings] Escape pressed, closing menu")
                return "exit"  # Signal to close menu and return to XMB
            elif event.key == pygame.K_RETURN:
                # Apply the selected theme
                try:
                    change_color(self.current_index)
                    print(f"[ThemeSettings] Selected: {self.options[self.current_index]} (Color: {self.theme_colors[self.current_index]})")
                except Exception as e:
                    print(f"[Error] Failed to change color: {e}")
                # Keep menu open after selection
            elif event.key == pygame.K_UP:
                self.current_index = max(0, self.current_index - 1)
                print(f"[ThemeSettings] Selected index: {self.current_index}")
            elif event.key == pygame.K_DOWN:
                self.current_index = min(len(self.options) - 1, self.current_index + 1)
                print(f"[ThemeSettings] Selected index: {self.current_index}")
        return None

    def draw(self, width, height, current_time):
        """Draw the theme settings panel with color squares."""
        # Create a surface for the panel with transparency
        panel_surface = pygame.Surface((self.panel_width, height), pygame.SRCALPHA)
        panel_surface.fill((0, 0, 0, self.panel_alpha))  # Semi-transparent black

        # Calculate option height
        option_height = height // len(self.options)

        # Draw each option with its color square
        for i, (option, text_surface, color) in enumerate(zip(self.options, self.text_surfaces, self.theme_colors)):
            # Calculate y-position for this option
            y_center = (i + 0.5) * option_height

            # Draw color square
            square_rect = pygame.Rect(
                self.color_square_margin,
                int(y_center - self.color_square_size / 2),
                self.color_square_size,
                self.color_square_size
            )
            pygame.draw.rect(panel_surface, color, square_rect)

            # Draw text next to the color square
            text_rect = text_surface.get_rect(
                midleft=(self.color_square_margin + self.color_square_size + self.color_square_margin, y_center)
            )
            panel_surface.blit(text_surface, text_rect)

            # Highlight selected option with a yellow outline
            if i == self.current_index:
                highlight_rect = pygame.Rect(
                    0, i * option_height, self.panel_width, option_height
                )
                pygame.draw.rect(panel_surface, (255, 255, 0, 128), highlight_rect, 2)

        # Blit the panel with the sweep animation
        panel_x = int(self.panel_offset_x)
        self.screen.blit(panel_surface, (panel_x, 0))

        # Background remains visible (no screen clearing)

def open_theme_settings(screen, font):
    """Create and initialize the ThemeSettings menu."""
    try:
        settings = ThemeSettings(screen, font)
        settings.start_animation()
        return settings
    except Exception as e:
        print(f"[Error] Failed to initialize ThemeSettings: {e}")
        return None

# Example usage (for testing purposes)
if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    font = pygame.font.Font(None, 36)
    clock = pygame.time.Clock()

    settings = open_theme_settings(screen, font)
    running = True

    while running:
        dt = clock.tick(60) / 1000.0  # Delta time in seconds
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            result = settings.handle_event(event)
            if result == "exit":
                running = False

        # Update and draw
        settings.update(dt)
        screen.fill((50, 50, 50))  # Dark gray background for testing
        settings.draw(screen.get_width(), screen.get_height(), pygame.time.get_ticks() / 1000.0)
        pygame.display.flip()

    pygame.quit()