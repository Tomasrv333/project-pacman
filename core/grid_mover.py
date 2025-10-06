"""
core/grid_mover.py — RandomPac v2.3
Movimiento fiel a Pac-Man:
- Solo gira si la celda vecina (tile + dir) es libre
- Detiene justo antes del muro (sin vibrar)
- Reversa inmediata solo si hay espacio detrás
"""

import pygame, random
from settings import TILE_SIZE, HUD_HEIGHT


class GridMover(pygame.sprite.Sprite):
    def __init__(self, grid, start_tile, color=(255, 255, 255), speed=3.0):
        super().__init__()
        self.grid = grid
        self.tile = pygame.Vector2(start_tile)          # posición en CELDAS
        self.pos = self._tile_center(self.tile)         # posición en PÍXELES
        self.current_dir = pygame.Vector2(1, 0)
        self.next_dir = pygame.Vector2(1, 0)
        self.speed = speed
        self.color = color

        self.image = pygame.Surface((TILE_SIZE - 2, TILE_SIZE - 2), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=self.pos)

    # ---------- conversiones ----------
    def _tile_center(self, tile):
        return pygame.Vector2(
            tile.x * TILE_SIZE + TILE_SIZE / 2,
            HUD_HEIGHT + tile.y * TILE_SIZE + TILE_SIZE / 2
        )

    def _pos_to_tile(self, pos):
        c = int(pos.x // TILE_SIZE)
        r = int((pos.y - HUD_HEIGHT) // TILE_SIZE)
        return c, r

    # ---------- mapa / colisiones por CELDA ----------
    def _is_blocked_tile(self, c, r):
        if r < 0 or c < 0 or r >= len(self.grid) or c >= len(self.grid[0]):
            return True
        v = self.grid[r][c]
        if v == 1:       # muro
            return True
        # 🔸 Ajuste: la puerta (4) bloquea solo al jugador, no a los fantasmas
        if v == 4 and self.__class__.__name__ == "Player":
            return True
        return False

    def _can_move_from_tile(self, tile, direction):
        nxt = tile + direction
        return not self._is_blocked_tile(int(nxt.x), int(nxt.y))

    # ---------- movimiento ----------
    def move_step(self, dt):
        center = self._tile_center(self.tile)
        at_center = self.pos.distance_to(center) < 2

        # 1) En el centro: decidir giro SOLO si la CELDA vecina es libre
        if at_center:
            if self._can_move_from_tile(self.tile, self.next_dir):
                self.current_dir = self.next_dir
            # si el frente está bloqueado, no avances (quédate centrado)
            if not self._can_move_from_tile(self.tile, self.current_dir):
                self.pos = center
                self.rect.center = (int(self.pos.x), int(self.pos.y))
                return

        # 2) Avanzar hacia el centro de la siguiente celda (sin pasarse)
        target_tile = self.tile + self.current_dir
        # si el target está bloqueado y aún no salimos del centro, alíneate y no avances
        if at_center and not self._can_move_from_tile(self.tile, self.current_dir):
            self.pos = center
            self.rect.center = (int(self.pos.x), int(self.pos.y))
            return

        target_center = self._tile_center(target_tile)
        step = self.current_dir * (self.speed * dt / 16)

        # mover y clamp al target_center
        self.pos += step
        if self.current_dir.x > 0 and self.pos.x >= target_center.x:
            self.pos.x = target_center.x
        elif self.current_dir.x < 0 and self.pos.x <= target_center.x:
            self.pos.x = target_center.x
        if self.current_dir.y > 0 and self.pos.y >= target_center.y:
            self.pos.y = target_center.y
        elif self.current_dir.y < 0 and self.pos.y <= target_center.y:
            self.pos.y = target_center.y

        # ¿llegamos a la siguiente celda?
        if self.pos == target_center:
            self.tile = target_tile  # avanzamos una celda

        self.rect.center = (int(self.pos.x), int(self.pos.y))

    # ---------- utilidades ----------
    def reverse_direction(self):
        self.current_dir = -self.current_dir
        self.next_dir = self.current_dir

    def try_reverse(self, desired_dir):
        """Permite reversa solo si hay espacio en la celda posterior."""
        if desired_dir == -self.current_dir and self._can_move_from_tile(self.tile, desired_dir):
            self.reverse_direction()

    def _find_alternative_dir(self):
        """Para IA: busca una dirección válida distinta a la contraria si hay opciones."""
        dirs = [pygame.Vector2(1,0), pygame.Vector2(-1,0), pygame.Vector2(0,1), pygame.Vector2(0,-1)]
        valids = [d for d in dirs if self._can_move_from_tile(self.tile, d)]
        if valids:
            if -self.current_dir in valids and len(valids) > 1:
                valids.remove(-self.current_dir)
            return random.choice(valids)
        return -self.current_dir
    
    def update(self, dt):
        """Actualiza el movimiento continuo, dependiente del tiempo."""
        self.move_step(dt)

    def teleport(self, new_tile):
        """Mueve instantáneamente al centro de la celda indicada."""
        self.tile = pygame.Vector2(new_tile)
        self.pos = self._tile_center(self.tile)
        self.rect.center = (int(self.pos.x), int(self.pos.y))

