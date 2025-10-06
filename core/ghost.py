"""
core/ghost.py — RandomPac v3.0
Fantasmas con comportamiento pseudoaleatorio controlado por el generador seleccionado.
"""

import pygame
from settings import *
from core.grid_mover import GridMover

# Direcciones cardinales
DIRS4 = [
    pygame.Vector2(1, 0),
    pygame.Vector2(-1, 0),
    pygame.Vector2(0, 1),
    pygame.Vector2(0, -1)
]

# Estados unificados
STATE_NORMAL = 0
STATE_FRIGHTENED = 1
STATE_EATEN = 2
STATE_IN_HOUSE = 3
STATE_LEAVING = 4
STATE_ROAMING = 5


class Ghost(GridMover):
    def __init__(self, grid, start_tile, color, behavior="random", target=None, speed=3.0, rng=None):
        super().__init__(grid, start_tile, color=color, speed=speed)
        self.behavior = behavior
        self.target = target
        self.state = STATE_ROAMING
        self.current_dir = pygame.Vector2(0, -1)
        self.base_color = color
        self._original_color = color
        self.leave_house = True
        self.rng = rng
        self.last_tile = self.tile
        self.leave_timer = 0

        # --- Imagen inicial ---
        self.image = pygame.Surface((TILE_SIZE - 2, TILE_SIZE - 2), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=self.pos)
        self._draw()  # pinta cuerpo y ojos iniciales

    # ---------- ESTADOS ----------
    def set_frightened(self, now_ms):
        if self.state != STATE_EATEN:
            self.state = STATE_FRIGHTENED
            self.frightened_until = now_ms + FRENZY_TIME_MS

    def was_eaten(self):
        self.state = STATE_EATEN

    def _speed_factor(self):
        if self.state == STATE_FRIGHTENED:
            return FRIGHTENED_SPEED_FACTOR
        if self.state == STATE_EATEN:
            return EATEN_SPEED_FACTOR
        return 1.0

    # ---------- ACTUALIZACIÓN ----------
    def update(self, dt):
        now = pygame.time.get_ticks()

        # 🔸 Si está "muerto" (solo ojos)
        if self.state == STATE_EATEN:
            # esperar si acaba de revivir
            if hasattr(self, "respawn_timer") and now < self.respawn_timer:
                return  # quieto dentro de casa
            elif hasattr(self, "respawn_timer"):
                del self.respawn_timer  # listo para moverse otra vez

            # moverse hacia la casa
            self._return_to_house_step(dt)
            return

        # 🔸 Fin del modo asustado
        if self.state == STATE_FRIGHTENED and now > self.frightened_until:
            self.state = STATE_NORMAL

        # 🔸 Movimiento normal o asustado
        self._normal_ai_step(dt)

        # 🔸 Redibujo (azul / parpadeo al final del modo poder)
        self._draw(now)

    # ---------- IA / MOVIMIENTO ----------
    def _normal_ai_step(self, dt):
        """Decide dirección solo al llegar al centro de una celda."""
        # 1. Verificar si está centrado
        center = self._tile_center(self.tile)
        at_center = self.pos.distance_to(center) < 2

        if at_center:
            valids = [d for d in DIRS4 if self._can_move_from_tile(self.tile, d)]
            if not valids:
                self.next_dir = -self.current_dir
            else:
                if len(valids) > 1 and -self.current_dir in valids:
                    valids.remove(-self.current_dir)

                if self.behavior == "chaser" and self.target:
                    # elige la dirección que acerque más al jugador
                    self.next_dir = min(
                        valids,
                        key=lambda d: abs((self.tile + d).x - self.target.tile.x)
                                    + abs((self.tile + d).y - self.target.tile.y)
                    )
                else:
                    # usa el generador pseudoaleatorio
                    r = self.rng.random() if self.rng else __import__("random").random()
                    idx = int(r * len(valids)) % len(valids)
                    self.next_dir = valids[idx]

            # actualizar dirección actual
            self.current_dir = self.next_dir

        # 2. Mover según la dirección actual
        self.move_step(dt)

    def _leave_house_step(self, dt):
        """Sale de la casa subiendo por la puerta."""
        if self._can_move_from_tile(self.tile, pygame.Vector2(0, -1)):
            self.current_dir = pygame.Vector2(0, -1)
            self.move_step(dt)
            if self.tile.y <= 12:
                self.state = STATE_ROAMING
        else:
            self.state = STATE_ROAMING

    def _return_to_house_step(self, dt):
        """Mover solo los ojos hacia el centro (13,13)."""
        target = pygame.Vector2(13, 13)
        speed_factor = EATEN_SPEED_FACTOR

        # calcular dirección cardinal más corta
        dirs = [pygame.Vector2(1,0), pygame.Vector2(-1,0), pygame.Vector2(0,1), pygame.Vector2(0,-1)]
        valids = [d for d in dirs if self._can_move_from_tile(self.tile, d)]
        if not valids:
            return

        # elegir la que acerque más al centro
        self.next_dir = min(valids, key=lambda d: (self.tile + d).distance_to(target))
        self.current_dir = self.next_dir
        self.move_step(dt * speed_factor)

        # si ya llegó
        if self.tile.distance_to(target) < 0.5:
            self.state = STATE_NORMAL
            self.base_color = self._original_color
            self.leave_house = True
            self.respawn_timer = pygame.time.get_ticks() + 1000

    # ---------- DIBUJO ----------
    def _draw(self, now=None):
        self.image.fill((0, 0, 0, 0))
        w, h = self.image.get_size()

        # --- estado visual ---
        if self.state == STATE_EATEN:
            # solo ojos
            le = (w // 2 - 5, h // 2 - 3)
            re = (w // 2 + 5, h // 2 - 3)
            pygame.draw.circle(self.image, (255,255,255), le, 4)
            pygame.draw.circle(self.image, (255,255,255), re, 4)
            off = self.current_dir * 2
            pygame.draw.circle(self.image, (30,30,200), (int(le[0]+off.x), int(le[1]+off.y)), 2)
            pygame.draw.circle(self.image, (30,30,200), (int(re[0]+off.x), int(re[1]+off.y)), 2)
            return

        # --- cuerpo normal / asustado ---
        if self.state == STATE_FRIGHTENED:
            body = (40, 100, 255)
            # parpadeo al final
            if now and now > self.frightened_until - 1500:
                if (now // 200) % 2 == 0:
                    body = (255, 255, 255)
        else:
            body = self.base_color

        pygame.draw.rect(self.image, body, (2, h // 3, w - 4, h // 2))
        pygame.draw.circle(self.image, body, (w // 2, h // 3), w // 2 - 2)

        # ojos
        le = (w // 2 - 5, h // 3 - 3)
        re = (w // 2 + 5, h // 3 - 3)
        pygame.draw.circle(self.image, (255, 255, 255), le, 4)
        pygame.draw.circle(self.image, (255, 255, 255), re, 4)
        off = self.current_dir * 2
        pygame.draw.circle(self.image, (30, 30, 200), (int(le[0]+off.x), int(le[1]+off.y)), 2)
        pygame.draw.circle(self.image, (30, 30, 200), (int(re[0]+off.x), int(re[1]+off.y)), 2)
