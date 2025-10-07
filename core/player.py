"""
core/player.py — RandomPac v1.6
===============================
Jugador (RandomPac) con movimiento clásico tipo Pac-Man:
- Movimiento continuo por celdas (usa GridMover)
- Giro 180° inmediato permitido
- Animación de boca fluida senoidal
"""

import pygame, math
from settings import *
from core.grid_mover import GridMover
from logic.map import eat_dot

class Player(GridMover):
    def __init__(self, grid, start_tile, color=(255, 220, 0), speed=3.2):
        super().__init__(grid, start_tile, color=color, speed=speed)
        self.score = 0
        self.lives = PLAYER_LIVES
        self.extra_life_claimed = False
        self.mouth_phase = 0.0      # 0..1
        self.dir_vec = pygame.Vector2(1,0)

    def add_score(self, v):
        self.score += int(v)
        # vida extra
        if (not self.extra_life_claimed) and self.score >= EXTRA_LIFE_AT and self.lives < MAX_LIVES:
            self.lives += 1
            self.extra_life_claimed = True
            # sfx desde game loop

    def update(self, dt):
        # --- leer input ---
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP]:
            self.next_dir = pygame.Vector2(0, -1)
        elif keys[pygame.K_DOWN]:
            self.next_dir = pygame.Vector2(0, 1)
        elif keys[pygame.K_LEFT]:
            self.next_dir = pygame.Vector2(-1, 0)
        elif keys[pygame.K_RIGHT]:
            self.next_dir = pygame.Vector2(1, 0)

        # --- movimiento ---
        prev_dir = self.current_dir.copy()
        super().update(dt)
        
        # --- detectar modo poder global ---
        is_power = pygame.time.get_ticks() < self.game_ref.power_mode_until
        if is_power:
            self.speed = 4.2
            # parpadeo visual suave
            self.power_flash = (pygame.time.get_ticks() // 150) % 2 == 0
        else:
            self.speed = 3.2
            self.power_flash = False
            
        # --- actualizar orientación solo si realmente giró ---
        if self.current_dir != prev_dir:
            self.dir_vec = self.current_dir

        # --- animación de la boca ---
        anim_speed = 3.5 if is_power else 2.2
        self.mouth_phase += (dt / 1000.0) * (self.speed * anim_speed)
        if self.mouth_phase > 1.0:
            self.mouth_phase -= 1.0

        self._draw_pacman()

    def _draw_pacman(self):
        self.image.fill((0,0,0,0))
        w, h = self.image.get_size()
        r = min(w,h)//2 - 1
        cx, cy = w//2, h//2

        # ángulo de la boca (0 = cerrado)
        # abre de 18° a 40° y regresa
        t = self.mouth_phase
        amp = 60
        base = 0
        mouth_deg = base + int(abs(0.5 - t) * 2 * (amp - base))  # triangulación

        # orientación
        if   self.dir_vec.x > 0: start = -mouth_deg; end = mouth_deg
        elif self.dir_vec.x < 0: start = 180 - mouth_deg; end = 180 + mouth_deg
        elif self.dir_vec.y < 0: start = -90 - mouth_deg; end = -90 + mouth_deg  # arriba
        elif self.dir_vec.y > 0: start = 90 - mouth_deg;  end = 90 + mouth_deg   # abajo
        else:                    start = -90 - mouth_deg; end = -90 + mouth_deg

        # círculo + “corte” de la boca
        color = (255, 255, 150) if self.power_flash else (255, 220, 0)
        pygame.draw.circle(self.image, color, (cx, cy), r)

        # BONUS ✨ halo visual durante el poder
        if self.power_flash:
            halo_color = (255, 255, 200, 60)  # color claro semi-transparente
            halo_surface = pygame.Surface((w, h), pygame.SRCALPHA)
            pygame.draw.circle(halo_surface, halo_color, (cx, cy), r + 3)
            pygame.draw.circle(halo_surface, (0, 0, 0, 0), (cx, cy), r - 2)
            self.image.blit(halo_surface, (0, 0), special_flags=pygame.BLEND_ADD)

        # cortar boca con un polígono del color de fondo HUD (transparente en sprite)
        theta1 = pygame.math.Vector2(1,0).rotate(start)
        theta2 = pygame.math.Vector2(1,0).rotate(end)
        p1 = (cx, cy)
        p2 = (cx + int(theta1.x*r*2), cy + int(theta1.y*r*2))
        p3 = (cx + int(theta2.x*r*2), cy + int(theta2.y*r*2))
        pygame.draw.polygon(self.image, (0,0,0,0), (p1,p2,p3))
