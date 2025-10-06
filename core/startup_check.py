"""
core/startup_check.py — RandomPac (v1.0)
=======================================
Verifica que todos los módulos esenciales estén disponibles antes de lanzar el juego.
"""

import importlib, sys, pygame

REQUIRED_MODULES = [
    "pygame",
    "settings",
    "core.menu",
    "core.game_loop",
    "core.player",
    "core.ghost",
    "core.hud",
    "core.effects",
    "logic.random_generators",
    "logic.map",
]

def run_diagnostics():
    try:
        # Verificar versión de pygame
        version = pygame.version.ver
        if int(version.split('.')[0]) < 2:
            return f"Versión de pygame incompatible ({version}). Se requiere >= 2.0"

        # Verificar importación de módulos
        for module in REQUIRED_MODULES:
            try:
                importlib.import_module(module)
            except Exception as e:
                return f"Error al cargar módulo '{module}': {e}"

        # Verificar fuentes y configuración
        from settings import WIDTH, HEIGHT, TILE_SIZE
        if WIDTH < 640 or HEIGHT < 480:
            return "Resolución no válida en settings.py."

        # Todo correcto
        return True

    except Exception as e:
        return f"Error en diagnóstico: {str(e)}"
