import pygame
import sys
import os
import numpy as np
from pydub import AudioSegment
from mutagen.id3 import ID3, TPE1, TIT2, TALB
import io
from PIL import Image

# Dictionary of images
IMAGE_CODES = {
    "22BB66": "images/horizontal/musica.png",  # Music icon
    "4F7A1C": "images/sys/play.png",          # Play button
    "D13E8B": "images/sys/pause.png",         # Pause button
    "7AC2F1": "images/sys/mp3.png",           # mp3
    "80BC7A": "images/sys/wav.png",           # wav
    "8F0830": "images/sys/aac.png",           # aac
    "71205B": "images/sys/wma.png",           # wma
    "B544D5": "images/sys/noimage.png",       # noimage
}

_loaded_images = {}

def get_image(code, max_size=None):
    if not code:
        return None
    code = code.upper()
    path = IMAGE_CODES.get(code)
    if not path:
        print(f"⚠️ Image code not found: {code}")
        return None
    if code not in _loaded_images:
        if not os.path.isfile(path):
            print(f"⚠️ File not found for code {code}: {path}")
            return None
        try:
            img = pygame.image.load(path).convert_alpha()
            _loaded_images[code] = img
        except Exception as e:
            print(f"⚠️ Error loading image {path}: {e}")
            return None
    img = _loaded_images[code]
    if max_size:
        try:
            width, height = img.get_size()
            aspect_ratio = width / height
            if width > height:
                new_width = max_size
                new_height = int(max_size / aspect_ratio)
            else:
                new_height = max_size
                new_width = int(max_size * aspect_ratio)
            return pygame.transform.smoothscale(img, (new_width, new_height))
        except Exception as e:
            print(f"⚠️ Error scaling image {code}: {e}")
            return img
    return img

class MusicVisualizer:
    def __init__(self, screen, song_path):
        self.screen = screen
        self.song_path = song_path
        self.font = pygame.font.SysFont("arial", 24)
        self.bar_font = pygame.font.SysFont("arial", 36, bold=True)
        self.time_font = pygame.font.SysFont("arial", 40, bold=True)
        self.paused = False
        self.running = False
        self.album_art = None
        self.author = "Unknown"
        self.song_title = "Unknown"
        self.album_name = "Unknown"
        self.bar_height = 80
        self.visualization_mode = "wave"  # Default to wave (PSP style)

        self.track_index, self.total_tracks = self.get_track_info(song_path)

        try:
            song = AudioSegment.from_file(song_path)
        except Exception as e:
            print(f"Could not load song: {e}")
            self.running = False
            return

        samples = np.array(song.get_array_of_samples())
        if song.channels == 2:
            samples = samples.reshape((-1, 2)).mean(axis=1)  # Mix stereo to mono: (L+R)/2
        self.sample_rate = song.frame_rate
        self.samples = samples.astype(np.float32)
        self.samples /= np.max(np.abs(self.samples))  # Normalize to [-1.0, 1.0]

        if not pygame.mixer.get_init():
            pygame.mixer.init(frequency=self.sample_rate)
        pygame.mixer.music.load(song_path)
        pygame.mixer.music.play()
        self.running = True

        # Wave visualization settings (PSP style)
        self.wave_points = 512  # Number of points for the wave
        self.wave_amplitude = 100  # Vertical amplitude for wave
        self.wave_y_center = self.screen.get_height() // 2  # Vertical center
        self.wave_width = self.screen.get_width() - 100  # Wave area width
        self.wave_x_start = 50  # Starting x position
        self.window_size = 512  # Samples per frame for all modes

        # Dots visualization settings
        self.cols = 12
        self.rows = 8
        self.dot_size = 20
        self.border_radius = 10
        self.dot_width = self.dot_size * 1.5
        self.dot_height = self.dot_size
        self.spacing_x = (self.screen.get_width() - self.cols * self.dot_width) // (self.cols + 1)
        self.spacing_y = (self.screen.get_height() - self.rows * self.dot_height) // (self.rows * 2)
        grid_height = self.rows * self.dot_height + (self.rows - 1) * self.spacing_y
        self.start_y = (self.screen.get_height() - grid_height) // 2 + 50
        self.start_x = self.spacing_x

        # Bars visualization settings
        self.bars_num = 32  # Number of bars
        self.bars_width = (self.screen.get_width() - 100) // self.bars_num
        self.bars_x_start = 50
        self.bars_base_y = self.screen.get_height() // 2
        self.bars_max_height = 200  # Maximum height of bars

        # Futiger Aero visualization settings
        self.aero_points = 16  # Number of circles
        self.aero_x_start = 50
        self.aero_width = self.screen.get_width() - 100
        self.aero_base_y = self.screen.get_height() // 2
        self.aero_max_radius = 50
        self.aero_min_radius = 10

        self.position = 0

        self.load_album_art()
        self.load_metadata()
        self.music_icon = get_image("22BB66", max_size=64)
        self.play_icon = get_image("4F7A1C", max_size=100)
        self.pause_icon = get_image("D13E8B", max_size=100)

    def get_track_info(self, song_path):
        folder = os.path.dirname(os.path.abspath(song_path))
        audio_extensions = ('.mp3', '.wav', '.flac', '.ogg', '.m4a', '.aac', '.wma')
        files = sorted([f for f in os.listdir(folder) if f.lower().endswith(audio_extensions)], key=str.lower)
        total = len(files)
        base_name = os.path.basename(song_path).lower()
        track_index = 1
        for i, f in enumerate(files):
            if f.lower() == base_name:
                track_index = i + 1
                break
        return track_index, total

    def load_album_art(self):
        try:
            tags = ID3(self.song_path)
            for tag in tags.values():
                if tag.FrameID == "APIC":
                    image_data = tag.data
                    image = Image.open(io.BytesIO(image_data))
                    image = image.resize((120, 120))
                    mode = image.mode
                    size = image.size
                    data = image.tobytes()
                    self.album_art = pygame.image.fromstring(data, size, mode)
                    return
        except:
            pass
        if os.path.isfile("cover.jpg"):
            self.album_art = pygame.image.load("cover.jpg")
            self.album_art = pygame.transform.scale(self.album_art, (120, 120))
            return
        self.album_art = get_image("B544D5", max_size=120)

    def load_metadata(self):
        try:
            tags = ID3(self.song_path)
            if "TPE1" in tags:
                self.author = tags["TPE1"].text[0]
            if "TIT2" in tags:
                self.song_title = tags["TIT2"].text[0]
            if "TALB" in tags:
                self.album_name = tags["TALB"].text[0]
        except:
            self.author = "Unknown"
            self.song_title = "Unknown"
            self.album_name = "Unknown"

    def handle_event(self, event):
        if event.type == pygame.QUIT:
            self.running = False
            pygame.mixer.music.stop()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                if self.paused:
                    pygame.mixer.music.unpause()
                    self.paused = False
                else:
                    pygame.mixer.music.pause()
                    self.paused = True
            elif event.key == pygame.K_ESCAPE:
                self.running = False
                pygame.mixer.music.stop()
            elif event.key == pygame.K_TAB:
                # Cycle through modes: wave -> dots -> bars -> futiger_aero -> wave
                modes = ["wave", "dots", "bars", "futiger_aero"]
                current_idx = modes.index(self.visualization_mode)
                self.visualization_mode = modes[(current_idx + 1) % len(modes)]
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            x_pos = 10
            icon = self.pause_icon if self.paused else self.play_icon
            if icon:
                y_pos = self.screen.get_height() - icon.get_height() - 20
                button_rect = pygame.Rect(x_pos, y_pos, icon.get_width(), icon.get_height())
                if button_rect.collidepoint(event.pos):
                    if self.paused:
                        pygame.mixer.music.unpause()
                        self.paused = False
                    else:
                        pygame.mixer.music.pause()
                        self.paused = True

    def update(self, dt):
        if not self.paused:
            self.position += int(self.sample_rate * dt)
            if self.position >= len(self.samples):
                self.position = len(self.samples)

    def get_wave_samples(self):
        """Extract PCM samples for the wave visualization."""
        start = self.position
        end = start + self.window_size
        if end >= len(self.samples):
            return np.zeros(self.wave_points)
        samples = self.samples[start:end]
        if len(samples) > 0:
            x = np.linspace(0, len(samples) - 1, self.wave_points)
            samples = np.interp(x, np.arange(len(samples)), samples)
        else:
            samples = np.zeros(self.wave_points)
        return samples

    def get_levels(self):
        """Calculate frequency levels for dots, bars, and futiger_aero visualizations."""
        start = self.position
        end = start + self.window_size
        if end >= len(self.samples):
            return [0] * max(self.cols, self.bars_num, self.aero_points)
        window = self.samples[start:end] * np.hanning(self.window_size)
        spectrum = np.abs(np.fft.rfft(window))
        freqs = np.fft.rfftfreq(self.window_size, 1/self.sample_rate)

        # Determine number of bands based on mode
        num_bands = {
            "dots": self.cols,
            "bars": self.bars_num,
            "futiger_aero": self.aero_points
        }.get(self.visualization_mode, self.cols)
        low_freq_limit = 200
        num_low_bands = num_bands // 3
        num_high_bands = num_bands - num_low_bands
        low_bands = np.linspace(20, low_freq_limit, num_low_bands + 1)
        high_bands = np.logspace(np.log10(low_freq_limit), np.log10(self.sample_rate / 2), num_high_bands + 1)
        band_limits = np.concatenate([low_bands[:-1], high_bands])

        levels = []
        bass_boost = 2.0
        min_threshold = 0.01

        for i in range(num_bands):
            mask = (freqs >= band_limits[i]) & (freqs < band_limits[i + 1])
            power = np.mean(spectrum[mask]) if np.any(mask) else 0
            if i < num_low_bands:
                power *= bass_boost
            power = max(power, min_threshold)
            levels.append(power)

        max_power = max(levels) if max(levels) > 0 else 1
        if self.visualization_mode == "dots":
            levels = [min((lvl / max_power) ** 0.7 * self.rows, self.rows) for lvl in levels]
            levels = [int(lvl) for lvl in levels]
        elif self.visualization_mode == "bars":
            levels = [min((lvl / max_power) ** 0.7 * self.bars_max_height, self.bars_max_height) for lvl in levels]
        else:  # futiger_aero
            levels = [min((lvl / max_power) ** 0.7 * (self.aero_max_radius - self.aero_min_radius) + self.aero_min_radius, self.aero_max_radius) for lvl in levels]
        return levels

    def format_time(self, seconds):
        minutes = int(seconds // 60)
        seconds = int(seconds % 60)
        return f"{minutes:02d}:{seconds:02d}"

    def draw_wave(self):
        """Draws a single, straight oscilloscope-style line with fixed endpoints."""
        samples = self.get_wave_samples()
        screen_height = self.screen.get_height()
        center_y = self.wave_y_center
        margin = 80
        x_start = self.wave_x_start
        x_end = x_start + self.wave_width

        # Generate points for the wave
        points = []
        x_positions = np.linspace(x_start, x_end, self.wave_points)
        points.append((x_start, center_y))  # Fixed start point
        for i in range(1, self.wave_points - 1):
            x = x_positions[i]
            y = center_y - samples[i] * self.wave_amplitude
            y = max(margin, min(screen_height - margin, y))
            points.append((x, y))
        points.append((x_end, center_y))  # Fixed end point

        # Smooth the points
        smoothed_points = [points[0]]
        for i in range(1, len(points) - 1):
            prev_x, prev_y = points[i - 1]
            curr_x, curr_y = points[i]
            next_x, next_y = points[i + 1]
            smoothed_y = (prev_y + curr_y * 2 + next_y) / 4
            smoothed_points.append((curr_x, smoothed_y))
        smoothed_points.append(points[-1])

        # Draw the wave with gradient color
        for i in range(len(smoothed_points) - 1):
            t = i / (len(smoothed_points) - 1)
            color = (
                int(0 + t * 255),    # Red: 0 to 255
                int(255 - t * 255),  # Green: 255 to 0
                255                  # Blue: constant
            )
            pygame.draw.line(self.screen, color, smoothed_points[i], smoothed_points[i + 1], 3)

    def draw_dots(self):
        """Draws the grid of rectangles for frequency visualization."""
        levels = self.get_levels()
        for col, active_rows in enumerate(levels):
            for row in range(self.rows):
                x = self.start_x + col * (self.dot_width + self.spacing_x)
                y = self.start_y + (self.rows - 1 - row) * (self.dot_height + self.spacing_y)
                if row < active_rows:
                    if row < 4:
                        color = (0, 255, 255)  # Cyan for low rows
                    elif 4 <= row <= 6:
                        color = (255, 165, 0)  # Orange for mid rows
                    else:
                        color = (255, 0, 0)    # Red for high rows
                else:
                    color = (30, 30, 30)      # Dark gray for inactive
                pygame.draw.rect(self.screen, color, (x, y, self.dot_width, self.dot_height), border_radius=self.border_radius)

    def draw_bars(self):
        """Draws green bars extending upward based on frequency bands."""
        levels = self.get_levels()
        for i, height in enumerate(levels):
            x = self.bars_x_start + i * self.bars_width
            y = self.bars_base_y - height
            pygame.draw.rect(self.screen, (0, 255, 0), (x, y, self.bars_width - 2, height), border_radius=5)

    def draw_futiger_aero(self):
        """Draws pulsating colorful circles in Frutiger Aero style."""
        levels = self.get_levels()
        x_positions = np.linspace(self.aero_x_start, self.aero_x_start + self.aero_width, self.aero_points)
        for i, radius in enumerate(levels):
            x = x_positions[i]
            y = self.aero_base_y
            # Color based on frequency band
            t = i / (self.aero_points - 1)
            color = (
                int(0 + t * 255),    # Red: 0 to 255
                int(255 - t * 100),  # Green: 255 to 155
                int(100 + t * 155)   # Blue: 100 to 255
            )
            # Add slight transparency for Aero effect
            surface = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(surface, (*color, 128), (radius, radius), radius)
            self.screen.blit(surface, (x - radius, y - radius))

    def draw(self):
        self.screen.fill((0, 0, 0))
        pygame.draw.rect(self.screen, (10, 10, 80), (0, 0, self.screen.get_width(), self.bar_height))

        if self.music_icon:
            self.screen.blit(self.music_icon, (10, (self.bar_height - 64) // 2))

        text_surface = self.bar_font.render(self.author, True, (255, 255, 255))
        self.screen.blit(text_surface, (84, (self.bar_height - text_surface.get_height()) // 2))

        counter_text = f"({self.track_index}/{self.total_tracks})"
        counter_surface = self.bar_font.render(counter_text, True, (255, 255, 255))
        self.screen.blit(counter_surface, (self.screen.get_width() - 10 - counter_surface.get_width(),
                                         (self.bar_height - counter_surface.get_height()) // 2))

        if self.album_art:
            album_x = 20
            album_y = self.bar_height + 10
            self.screen.blit(self.album_art, (album_x, album_y))
            line_y = album_y + 60
            pygame.draw.line(self.screen, (255, 255, 255), (album_x + 120, line_y), (self.screen.get_width() - 20, line_y), 2)
            title_surface = self.bar_font.render(self.song_title, True, (255, 255, 255))
            self.screen.blit(title_surface, (album_x + 130, line_y - title_surface.get_height() - 5))
            album_surface = self.font.render(self.album_name, True, (255, 255, 255))
            self.screen.blit(album_surface, (album_x + 130, line_y + 5))

            file_extension = os.path.splitext(self.song_path)[1].lower()
            format_code = {
                '.mp3': '7AC2F1',
                '.wav': '80BC7A',
                '.aac': '8F0830',
                '.wma': '71205B',
                '.m4a': '8F0830',
            }.get(file_extension, '7AC2F1')
            format_icon = get_image(format_code, max_size=140)
            if format_icon:
                format_x = self.screen.get_width() - format_icon.get_width() - 20
                format_y = line_y + 5
                self.screen.blit(format_icon, (format_x, format_y))

        # Draw visualization based on mode
        if self.visualization_mode == "wave":
            self.draw_wave()
        elif self.visualization_mode == "dots":
            self.draw_dots()
        elif self.visualization_mode == "bars":
            self.draw_bars()
        else:  # futiger_aero
            self.draw_futiger_aero()

        icon = self.pause_icon if self.paused else self.play_icon
        if icon:
            x_pos = 10
            y_pos = self.screen.get_height() - icon.get_height() - 20
            self.screen.blit(icon, (x_pos, y_pos))

        line_start_x = self.screen.get_width() - 650
        line_end_x = self.screen.get_width() - 50
        line_y = self.screen.get_height() - 50
        pygame.draw.line(self.screen, (255, 255, 255), (line_start_x, line_y), (line_end_x, line_y), 10)

        if len(self.samples) > 0:
            progress = self.position / len(self.samples)
            progress_end_x = line_start_x + (line_end_x - line_start_x) * progress
            pygame.draw.line(self.screen, (0, 0, 255), (line_start_x, line_y), (progress_end_x, line_y), 10)

            total_seconds = len(self.samples) / self.sample_rate
            current_seconds = min(self.position / self.sample_rate, total_seconds)
            current_time = self.format_time(current_seconds)
            total_time = self.format_time(total_seconds)
            current_time_surface = self.time_font.render(current_time, True, (0, 0, 255))
            total_time_surface = self.time_font.render(f"/{total_time}", True, (255, 255, 255))
            total_text_width = current_time_surface.get_width() + total_time_surface.get_width()

            text_x = line_end_x - total_text_width - 10
            text_y = line_y - current_time_surface.get_height() - 10
            self.screen.blit(current_time_surface, (text_x, text_y))
            self.screen.blit(total_time_surface, (text_x + current_time_surface.get_width(), text_y))

    def is_running(self):
        return self.running

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python music.py <audio_file>")
        sys.exit(1)
    song_path = sys.argv[1]
    if not os.path.isfile(song_path):
        print(f"File not found: {song_path}")
        sys.exit(1)

    pygame.init()
    screen = pygame.display.set_mode((1280, 720))
    pygame.display.set_caption("Music Visualizer with Wave, Dots, Bars, and Futiger Aero")
    player = MusicVisualizer(screen, song_path)
    clock = pygame.time.Clock()

    while player.is_running():
        for event in pygame.event.get():
            player.handle_event(event)
        player.update(1/30)
        player.draw()
        pygame.display.flip()
        clock.tick(30)

    pygame.quit()
    sys.exit()