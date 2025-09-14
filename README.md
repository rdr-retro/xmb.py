# xmb.py En desarrollo.

**XMBMenu** es un sistema de menú inspirado en la interfaz XMB de PlayStation, implementado en Python usando **Pygame**. Está diseñado para manejar múltiples categorías, submenús, archivos y reproducción de música con visualización dinámica, con soporte completo de animaciones y layout adaptable a cualquier resolución.
<img width="800" height="500" alt="Captura de pantalla 2025-09-13 a las 20 51 33" src="https://github.com/user-attachments/assets/84c9d921-0861-4798-bbcf-5f6d2d2bc04e" />

---

## Características Principales

- **Navegación Horizontal y Vertical**: Explora categorías horizontalmente y submenús verticalmente.
- **Submenús Anidados**:
  - Ajustes de pantalla y salida de video.
  - Ajustes de tema.
  - Gestión de usuarios.
- **Reproductor de Música**: Soporte para `.mp3`, `.wav`, `.aac`, `.wma` con visualización dinámica.
- **Gestor de Archivos**: Navega directorios, reproduce archivos de audio y maneja carpetas.
- **Animaciones Suaves**:
  - Lerp para desplazamiento de menú y submenús.
  - Fade-in/out de iconos.
  - Animación de salto al cambiar selección.
- **Modo Oscuro** con sonido al activarlo.
- **Reloj Integrado** (`reloj.draw_reloj`).
- **Iconos Personalizables** por categoría o submenú.
- **Easter-egg** incluido en Ajustes → Huevo.
- **Soporte Multiusuario**: Crear, seleccionar y mostrar usuario activo.
- **Responsive Layout**: Adapta automáticamente tamaños y posiciones a la resolución de pantalla.

---

## Requisitos

- Python 3.12.4
- Pygame 2.0+
- Módulos auxiliares incluidos:
  - `utils` (función `lerp`)
  - `reloj`
  - `screen` (`ScreenSettings`)
  - `user_input_screen` (`UserInputScreen`)
  - `users` (`UserManager`)
  - `images` (`get_image`)
  - `music` (`MusicVisualizer`)
  - `theme` (`open_theme_settings`)


<img width="1277" height="718" alt="Captura de pantalla 2025-09-13 a las 20 51 33" src="https://github.com/user-attachments/assets/d2ac1fcc-4b41-454b-9f7f-d76920966ba2" />

<img width="1277" height="717" alt="Captura de pantalla 2025-09-13 a las 20 54 38" src="https://github.com/user-attachments/assets/c166a340-6b1b-4ca8-b032-3bc84e37eb25" />
<img width="1277" height="717" alt="Captura de pantalla 2025-09-13 a las 20 54 48" src="https://github.com/user-attachments/assets/4fd852a9-16bb-47c9-a1d4-6a17760a1524" />

# Install
- descargar python 3.12.4 Añadir al Path actualizar pip e instalar las siguientes librerias:
# pygame
# numpy
# pillow
# pydub
# mutagen
- opccional visual studio code

- Descargar ffmpeg: Ve a la página oficial: https://ffmpeg.org/download.html
- Descarga una versión compilada (por ejemplo, desde gyan.dev o BtbN).
- Descomprime el archivo .zip en alguna carpeta (ejemplo: C:\ffmpeg).
- Añade la ruta C:\ffmpeg\bin a las variables de entorno (PATH): Abre Panel de Control → Sistema → Configuración avanzada del sistema. En Variables de entorno, edita Path y agrega la ruta.
- renicia windows despuws de instalar ffmpeg
  
