# images.py
"""
Mapa centralizado de imágenes: código hex -> ruta de archivo.
Usa get_image("EFA295") desde otros módulos (ej. xmb.py).
"""

import os
import pygame

# Diccionario: código hex → ruta relativa del archivo de imagen
IMAGE_CODES = {
    "EFA295": "images/vertical/folder.png",       # Archivos / folder
    "C1B3F0": "images/vertical/star.png",         # Favoritos
    "A92F11": "images/horizontal/clock.png",      # Reloj
    "BB00FF": "images/horizontal/juegos.png",     # Juegos
    "11AAFF": "images/horizontal/fotos.png",      # Fotos
    "22BB66": "images/horizontal/musica.png",     # Música
    "FFAA33": "images/horizontal/videos.png",     # Videos
    "DD44CC": "images/horizontal/ajustes.png",    # Ajustes
    "1A3F7C": "images/vertical/screenset.png",    # Ajustes de pantalla
    "B45E2F": "images/vertical/update.png",    # update
    "08D9A3": "images/vertical/theme.png",    # Ajustes de tema
    "4F7A2B": "images/vertical/egg.png",    # egg
"1A3F7C": "images/vertical/screenset.png",    # Ajustes de pantalla


    "F1F1F1": "images/vertical/flecha.png",       # Flecha
    "99CC00": "images/horizontal/usuarios.png",   # Usuarios
    "FF0000": "images/vertical/ap.png",            # Botón de apagado
    "33AA77": "images/vertical/newus.png",          # Nuevo usuario
    "7799CC": "images/vertical/user.png",          # Usuario ya creado
    "33AAFF": "images/vertical/accd.png",          # Usuario ya creado
# Multimedia
    "4F7A1C": "images/sys/play.png",         # play
    "D13E8B": "images/sys/pause.png",        # pause
    "7AC2F1": "images/sys/mp3.png",          # mp3
    "80BC7A": "images/sys/wav.png",          # wav
    "8F0830": "images/sys/aac.png",          # aac
    "71205B": "images/sys/wma.png",          # wma
    "B544D5": "images/sys/noimage.png",      # noimage


}

# Caché de imágenes cargadas para evitar recargas
_loaded_images = {}

def get_image(code, scale=None):
    """
    Devuelve una Surface de pygame para el código dado.
    - code: str, código hex (no sensible a mayúsculas).
    - scale: (w, h) opcional para escalar la imagen antes de devolverla.
    Retorna None y emite un warning si falta el código o el archivo.
    """
    if not code:
        return None
    code = code.upper()
    path = IMAGE_CODES.get(code)
    if not path:
        print(f"⚠️ Código de imagen no encontrado: {code}")
        return None

    if code not in _loaded_images:
        if not os.path.isfile(path):
            print(f"⚠️ Archivo no encontrado para el código {code}: {path}")
            return None
        try:
            img = pygame.image.load(path).convert_alpha()
            _loaded_images[code] = img
        except Exception as e:
            print(f"⚠️ Error cargando imagen {path}: {e}")
            return None

    img = _loaded_images[code]
    if scale:
        try:
            return pygame.transform.smoothscale(img, scale)
        except Exception as e:
            print(f"⚠️ Error escalando imagen {code}: {e}")
            return img
    return img

def register_image(code, path, preload=False):
    """
    Registra dinámicamente un nuevo código -> ruta.
    Si preload=True intenta cargarla inmediatamente en caché.
    """
    if not code or not path:
        return
    code = code.upper()
    IMAGE_CODES[code] = path
    if preload and os.path.isfile(path):
        try:
            _loaded_images[code] = pygame.image.load(path).convert_alpha()
        except Exception as e:
            print(f"⚠️ Error preload register_image {path}: {e}")

def preload_all():
    """Intenta precargar todas las imágenes existentes en IMAGE_CODES."""
    for code, path in IMAGE_CODES.items():
        if code in _loaded_images:
            continue
        if os.path.isfile(path):
            try:
                _loaded_images[code] = pygame.image.load(path).convert_alpha()
            except Exception as e:
                print(f"⚠️ Error preloading {path}: {e}")

def list_codes():
    """Devuelve la lista de códigos registrados."""
    return list(IMAGE_CODES.keys())
