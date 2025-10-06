"""
settings.py — RandomPac v1.5
============================
Configuración global del juego.
Incluye dimensiones, colores, FPS, fuentes y constantes de juego.
"""

import os
import pygame

# ----------------------------------------------------------------------
# 🖥️ DIMENSIONES Y ESCALA
# ----------------------------------------------------------------------
# Tamaño de la cuadrícula (Pac-Man original)
GRID_COLS = 28
GRID_ROWS = 31

# Tamaño de cada celda (ajustable)
TILE_SIZE = 24  # ideal para resoluciones normales (672x744)

# HUD (barra superior azul)
HUD_HEIGHT = 80

# Dimensiones finales de ventana
WIDTH = GRID_COLS * TILE_SIZE
HEIGHT = GRID_ROWS * TILE_SIZE + HUD_HEIGHT

# ----------------------------------------------------------------------
# ⚙️ AJUSTES GENERALES
# ----------------------------------------------------------------------
FPS = 60
TITLE = "RANDOMPAC — Simulación Discreta y Aleatoriedad"

# ----------------------------------------------------------------------
# 🎨 COLORES
# ----------------------------------------------------------------------
DARK_BLUE = (10, 10, 40)
BLUE = (0, 128, 255)
YELLOW = (255, 220, 0)
RED = (255, 0, 0)
PINK = (255, 105, 180)
CYAN = (0, 255, 255)
ORANGE = (255, 165, 0)
WHITE = (255, 255, 255)
GRAY = (180, 180, 180)
WALL_COLOR = (10, 20, 60)
BG_COLOR = (25, 80, 200)
HUD_BG = (0, 70, 180)
HUD_TEXT = (255, 255, 255)


# ----------------------------------------------------------------------
# 🕹️ VARIABLES DE JUEGO
# ----------------------------------------------------------------------

# --- PUNTAJES ---
DOT_SCORE = 10
POWER_DOT_SCORE = 50
GHOST_SCORE_BASE = 200          # 200, 400, 800, 1600… en cadena

# --- VIDAS ---
PLAYER_LIVES = 3
EXTRA_LIFE_AT = 3000            # gana una vida adicional al superar este score
MAX_LIVES = 5

# --- POWER MODE / FRENESÍ ---
FRENZY_TIME_MS = 6000           # duración en milisegundos
FRIGHTENED_SPEED_FACTOR = 0.6   # fantasmas más lentos estando asustados
EATEN_SPEED_FACTOR = 1.2        # ojos regresando, un poco más rápido


# ----------------------------------------------------------------------
# 🔤 FUENTES
# ----------------------------------------------------------------------
pygame.font.init()
FONT_MAIN = pygame.font.match_font("arial")

# ----------------------------------------------------------------------
# 🔊 RUTAS Y RECURSOS (opcional)
# ----------------------------------------------------------------------
BASE_DIR = os.path.dirname(__file__)
ASSETS_DIR = os.path.join(BASE_DIR, "assets")

# Asegura que exista la carpeta de recursos
os.makedirs(ASSETS_DIR, exist_ok=True)
