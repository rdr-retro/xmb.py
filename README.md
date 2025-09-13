# xmb.py

**XMBMenu** es un sistema de menú inspirado en la interfaz XMB de PlayStation, implementado en Python usando **Pygame**. Está diseñado para manejar múltiples categorías, submenús, archivos y reproducción de música con visualización dinámica, con soporte completo de animaciones y layout adaptable a cualquier resolución.

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

- Python 3.12.4+
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

---

