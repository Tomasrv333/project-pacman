
# Pacman Simulación — Skeleton (Pygame)

Proyecto base para el reto de **Simulación Discreta**. Incluye:
- Bucle de juego con Pygame
- Mapa en grilla (tiles), puntos y paredes
- Jugador controlado con teclado
- Fantasma con movimiento **aleatorio** inyectado desde `random_generators.py`
- Tres generadores PRNG: **LCG**, **MiddleSquare**, **XorShift32**
- Pantalla de título, HUD (score/vidas) y estructura modular

## Requisitos
```bash
python -m venv .venv
# Activar entorno e instalar:
pip install -r requirements.txt
```

## Ejecutar
```bash
python main.py
```

## Archivos clave
- `settings.py` — constantes y configuración.
- `map.py` — layout del nivel (matriz) y utilidades del mapa.
- `random_generators.py` — generadores de números pseudoaleatorios.
- `player.py` — clase Player (movimiento y colisión).
- `ghost.py` — clase Ghost, usa un PRNG inyectado para decidir direcciones.
- `main.py` — orquestación del juego.
