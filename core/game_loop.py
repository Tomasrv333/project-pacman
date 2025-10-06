"""
core/game_loop.py — RandomPac v1.6
Bucle principal: integra dificultad (velocidad), sonido y RNG.
"""

import pygame, sys, os, time
from settings import *
from core.player import Player
from core.ghost import Ghost, STATE_FRIGHTENED, STATE_EATEN, STATE_NORMAL
from core.hud import HUD
from core.effects import Transition
from logic.map import generate_level, eat_dot
from audio.sfx import SFX
from storage.profile import update_stats

class GameLoop:
    def __init__(self, screen, generator_class, method_name, seed, config=None):
        self.screen = screen
        self.level = generate_level()
        self.generator = generator_class(seed)
        self.method_name = method_name
        self.seed = seed
        self.power_mode_until = 0  # tiempo en ms hasta cuando dura el modo poder
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(FONT_MAIN, 24)
        self.running = True
        self.paused = False

        # === CONFIGURACIÓN GENERAL ===
        self.config = config or {}
        difficulty = self.config.get("difficulty", "Clásico")

        # === VELOCIDADES POR DIFICULTAD ===
        if difficulty == "Clásico":
            self.speed_player = 3.2
            self.speed_ghost = 3.0
        elif difficulty == "Difícil":
            self.speed_player = 3.8
            self.speed_ghost = 3.6
        elif difficulty == "Extremo":
            self.speed_player = 4.4
            self.speed_ghost = 4.2
        else:
            self.speed_player = 3.2
            self.speed_ghost = 3.0

        # === ENTIDADES ===
        # === ENTIDADES ===
        self.player = Player(self.level, start_tile=(13, 23), color=YELLOW, speed=self.speed_player)
        self.player.game_ref = self  # <--- referencia al juego

        self.ghosts = pygame.sprite.Group(
            Ghost(self.level, (13, 13), RED, "chaser", self.player, self.speed_ghost, self.generator),
            Ghost(self.level, (14, 13), PINK, "random", self.player, self.speed_ghost, self.generator),
            Ghost(self.level, (12, 13), CYAN, "random", self.player, self.speed_ghost, self.generator),
            Ghost(self.level, (15, 13), ORANGE, "random", self.player, self.speed_ghost, self.generator),
        )

        self.hud = HUD(self.screen, self.font, self.method_name, self.seed)

        # sonidos
        self.sfx = SFX()
        self.chain_eat = 0          # cadena de comer fantasmas
        self.start_time = time.time()

    # ---------- BUCLE ----------
    def run(self):
        Transition(self.screen).fade_out()
        while self.running:
            dt = self.clock.tick(FPS)
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
            self.update(dt)
            self.draw()
        pygame.time.delay(600)

        # guardar estadísticas al salir de la partida
        duration = int(time.time() - self.start_time)
        update_stats(
            self.config.get("player","anon"),
            self.player.score,
            duration,
            self.config
        )

    # ---------- LÓGICA ----------
    def reset_positions(self):
        self.player.teleport((13,23))
        for i,g in enumerate(self.ghosts.sprites()):
            g.teleport((13+(i%2)*1 + (-1 if i==2 else 0), 14))
            g.current_dir = pygame.Vector2(0, -1)
            g.state = STATE_NORMAL
            g._draw()


    def update(self, dt):
        # mover entidades
        self.player.update(dt)
        for g in self.ghosts:
            g.update(dt)

        # comer dots / power
        # comer dots / power
        c, r = int(self.player.tile.x), int(self.player.tile.y)
        pre = self.level[r][c]
        if pre in (2, 3):  # 2 = dot, 3 = power
            if pre == 2:
                self.player.add_score(DOT_SCORE)
                self.sfx.play("dot")
            else:
                # power pellet
                self.player.add_score(POWER_DOT_SCORE)
                self.chain_eat = 0
                now = pygame.time.get_ticks()
                for g in self.ghosts:
                    g.set_frightened(now)
                # activar modo poder global
                self.power_mode_until = now + FRENZY_TIME_MS
                self.sfx.play("power")
                self.sfx.stop("frightened")
                self.sfx.loop("frightened")
            eat_dot(self.level, c, r)
            self.hud.update(self.player.score, self.player.lives)

        # -------- COLISIONES CIRCULARES --------
        for g in self.ghosts:
            dx = self.player.pos.x - g.pos.x
            dy = self.player.pos.y - g.pos.y
            dist = (dx * dx + dy * dy) ** 0.5

            if dist < TILE_SIZE * 0.6:  # colisión justa
                if g.state == STATE_FRIGHTENED:
                    self.chain_eat += 1
                    gain = GHOST_SCORE_BASE * (2 ** (self.chain_eat - 1))
                    self.player.add_score(gain)
                    g.was_eaten()
                    self.sfx.play("ghost_eat")
                    self.hud.update(self.player.score, self.player.lives, f"+{gain}")
                elif g.state != STATE_EATEN:
                    # perder vida
                    self.player.lives -= 1
                    self.sfx.stop("frightened")
                    self.sfx.play("death")
                    self.chain_eat = 0
                    if self.player.lives <= 0:
                        self.running = False
                        return
                    self.reset_positions()
                    self.hud.update(self.player.score, self.player.lives, "¡Ay!")

        # detener sonido cuando termina el modo poder
        # detener sonido cuando termina el modo poder
        if pygame.time.get_ticks() > self.power_mode_until:
            self.sfx.stop("frightened")

        # victoria
        if all(all(v not in (2, 3) for v in row) for row in self.level):
            self.running = False

    # ---------- DIBUJO ----------
    def draw_grid(self):
        for r, row in enumerate(self.level):
            for c, val in enumerate(row):
                x = c * TILE_SIZE
                y = HUD_HEIGHT + r * TILE_SIZE
                if val == 1:
                    pygame.draw.rect(self.screen, WALL_COLOR, (x, y, TILE_SIZE, TILE_SIZE))
                elif val == 4:
                    pygame.draw.rect(self.screen, (150,150,255), (x+8, y+TILE_SIZE//2-2, TILE_SIZE-16, 4))
                elif val == 2:
                    pygame.draw.circle(self.screen, (255,255,255), (x+TILE_SIZE//2, y+TILE_SIZE//2), 3)
                elif val == 3:
                    t = (pygame.time.get_ticks()//250)%2==0
                    if t: pygame.draw.circle(self.screen, (255,255,102), (x+TILE_SIZE//2, y+TILE_SIZE//2), 6)

    def draw(self):
        self.screen.fill(DARK_BLUE)
        self.draw_grid()
        self.screen.blit(self.player.image, self.player.rect)
        self.ghosts.draw(self.screen)
        self.hud.draw()
        pygame.display.flip()