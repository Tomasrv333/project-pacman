"""
logic/map.py — RandomPac v4.0
==============================
Gestor de mapas del juego.
Ahora soporta:
- Mapa clásico fijo (generate_level)
- Mapas personalizados en /storage/maps/*.json
- Funciones utilitarias (is_wall, is_door, eat_dot)
"""

import os, json

# --- CONFIGURACIÓN GENERAL ---
MAPS_DIR = os.path.join("storage", "maps")

# --- MAPA CLÁSICO BASE ---
def generate_level():
    """Genera el mapa clásico tipo Pac-Man (por defecto)."""
    level = [
        "1111111111111111111111111111",
        "1322222222222112222222222221",
        "1211112111112112111112111121",
        "1211112111112112111112111121",
        "1211112111112112111112111121",
        "1222222222222222222222222221",
        "1211112112111111112112111121",
        "1211112112111111112112111131",
        "1222222112222112222112222221",
        "1111112111112112111112111111",
        "1111112111112112111112111111",
        "1111112112222222222112111111",
        "1111112112111441112112111111",
        "1111112112100000012112111111",
        "2222222222100000012222222222",
        "1111112112100000012112111111",
        "1111112112111111112112111111",
        "1111112112222222222112111111",
        "1111112112111111112112111111",
        "1111112112111111112112111111",
        "1222222222222112222222222221",
        "1211112111112112111112111121",
        "1211112111112112111112111121",
        "1322112222222222222222112221",
        "1112112112111111112112112111",
        "1112112112111111112112112111",
        "1222222112222112222112222221",
        "1211111111112112111111111121",
        "1211111111112112111111111121",
        "1222222222222222222222222231",
        "1111111111111111111111111111",
    ]
    return [[int(ch) for ch in row] for row in level]

# --- MAPAS PERSONALIZADOS ---
def list_custom_maps():
    """Devuelve una lista de nombres de mapas disponibles en storage/maps."""
    if not os.path.exists(MAPS_DIR):
        return []
    return [f[:-5] for f in os.listdir(MAPS_DIR) if f.endswith(".json")]

def load_custom_map(name):
    """Carga un mapa guardado como JSON desde /storage/maps/."""
    path = os.path.join(MAPS_DIR, f"{name}.json")
    if not os.path.exists(path):
        raise FileNotFoundError(f"❌ No se encontró el mapa '{name}' en {MAPS_DIR}")

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # validar formato (debe ser lista de listas de enteros)
    if not isinstance(data, list) or not all(isinstance(row, list) for row in data):
        raise ValueError(f"Formato inválido del mapa '{name}'")

    # aseguramos que todos los valores sean int
    grid = [[int(v) for v in row] for row in data]
    return grid

def load_map(name: str):
    """Carga un mapa desde JSON o retorna el clásico por defecto."""
    if not name or name.lower() == "clásico":
        return generate_level()

    path = os.path.join("storage", "maps", f"{name}.json")
    if not os.path.exists(path):
        print(f"⚠️ Mapa '{name}' no encontrado. Usando clásico.")
        return generate_level()

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            # validar dimensiones básicas
            if isinstance(data, list) and len(data) > 10 and all(isinstance(row, list) for row in data):
                return data
            else:
                print(f"⚠️ Mapa '{name}' inválido. Usando clásico.")
                return generate_level()
    except Exception as e:
        print(f"⚠️ Error al cargar mapa {name}: {e}")
        return generate_level()

# --- FUNCIONES AUXILIARES (sin cambios) ---
def is_wall(grid, c, r):
    return grid[r][c] == 1

def is_door(grid, c, r):
    return grid[r][c] == 4

def eat_dot(grid, c, r):
    """Elimina el punto o power dot cuando Pac-Man lo come."""
    if grid[r][c] in (2, 3):
        grid[r][c] = 0
        return True
    return False
