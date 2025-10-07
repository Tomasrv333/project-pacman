# core/state.py
from enum import Enum, auto

class AppState(Enum):
    START = auto()         # input de nombre
    MENU = auto()          # menú principal
    WIZARD = auto()        # configuración de partida
    PRE_GAME = auto()      # overlay controles
    GAME = auto()          # en partida
    PAUSE = auto()         # menú de pausa
    DEATH = auto()         # fin de vida / stats
    ENCYCLOPEDIA = auto()
    STATS = auto()
    SETTINGS = auto()
    MAP_EDITOR = auto()    # generador de mapa
