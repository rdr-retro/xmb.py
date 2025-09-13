import json
import os


class UserManager:
    def __init__(self, save_file="users.json"):
        """
        Clase para gestionar usuarios del sistema.
        - Carga usuarios desde JSON al iniciar.
        - Proporciona funciones para crear, guardar y obtenerlos como menú.
        """
        self.save_file = save_file
        self.users = ["Usuario1"]  # Usuario por defecto si no hay archivo
        self.load_users()

    def load_users(self):
        """
        Carga usuarios desde un archivo JSON si existe.
        Si hay algún error o no existe, deja el usuario por defecto.
        """
        if os.path.isfile(self.save_file):
            try:
                with open(self.save_file, "r", encoding="utf-8") as f:
                    loaded = json.load(f)
                    if isinstance(loaded, list):
                        self.users = loaded
                    else:
                        print("⚠️ El archivo de usuarios no tiene formato de lista. Usando valor por defecto.")
                        self.users = ["Usuario1"]
            except Exception as e:
                print(f"⚠️ Error cargando usuarios: {e}")
                self.users = ["Usuario1"]

    def save_users(self):
        """
        Guarda los usuarios en un archivo JSON.
        """
        try:
            with open(self.save_file, "w", encoding="utf-8") as f:
                json.dump(self.users, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"⚠️ Error guardando usuarios: {e}")

    def get_menu_items(self):
        """
        Devuelve la lista de opciones del submenú "Usuarios".
        Siempre contiene:
          - 'Apagar sistema'
          - 'Crear nuevo usuario'
          - Todos los usuarios registrados
        """
        return ["Apagar sistema", "Crear nuevo usuario"] + self.users

    def create_user(self, base_name="Usuario"):
        """
        Crea un nuevo usuario con nombre único basado en 'UsuarioN'.
        Se guarda automáticamente en users.json.
        Devuelve el nombre creado.
        """
        # Generar un nombre que no esté en uso
        n = len(self.users) + 1
        new_name = f"{base_name}{n}"
        while new_name in self.users:
            n += 1
            new_name = f"{base_name}{n}"

        self.users.append(new_name)
        self.save_users()
        return new_name

    def add_user(self, name):
        """
        Añade un usuario con un nombre en específico (ej: introducido en pantalla).
        Ignora si está vacío o si ya existe.
        Se guarda en json y se devuelve el nombre agregado, o None si no se agregó.
        """
        clean_name = name.strip()
        if clean_name and clean_name not in self.users:
            self.users.append(clean_name)
            self.save_users()
            return clean_name
        return None

    def remove_user(self, name):
        """
        Elimina un usuario de la lista (menos el primero por defecto).
        Devuelve True si se eliminó, False si no existía.
        """
        if name in self.users and name != "Usuario1":  # proteger el usuario base
            self.users.remove(name)
            self.save_users()
            return True
        return False
