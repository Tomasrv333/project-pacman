
from settings import GRID_COLS, GRID_ROWS

# 0: vacío, 1: pared, 2: punto, 3: power-dot (grande)
# Layout sencillo 25x25 (borde de paredes + puntos en pasillos).
LEVEL = []
for r in range(GRID_ROWS):
    row = []
    for c in range(GRID_COLS):
        if r in (0, GRID_ROWS-1) or c in (0, GRID_COLS-1):
            row.append(1)  # borde
        else:
            row.append(2)  # punto por defecto
    LEVEL.append(row)

# Carve simple corridors (rectángulos internos)
def carve_rect(x0, y0, x1, y1):
    for r in range(y0, y1+1):
        for c in range(x0, x1+1):
            LEVEL[r][c] = 0

# Pasillos internos (muy simple — editable por el equipo)
carve_rect(2,2,22,2)
carve_rect(2,22,22,22)
carve_rect(2,2,2,22)
carve_rect(22,2,22,22)

carve_rect(4,4,20,4)
carve_rect(4,20,20,20)
carve_rect(4,4,4,20)
carve_rect(20,4,20,20)

carve_rect(6,6,18,6)
carve_rect(6,18,18,18)
carve_rect(6,6,6,18)
carve_rect(18,6,18,18)

# Power dots en esquinas internas
LEVEL[4][4] = 3
LEVEL[4][20] = 3
LEVEL[20][4] = 3
LEVEL[20][20] = 3

def is_wall(grid, c, r):
    return grid[r][c] == 1

def has_dot(grid, c, r):
    return grid[r][c] == 2

def eat_dot(grid, c, r):
    if grid[r][c] in (2,3):
        grid[r][c] = 0
        return True
    return False
