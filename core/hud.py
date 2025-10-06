"""
core/hud.py — RandomPac (v1.2)
HUD: Puntaje, vidas, método, semilla y tiempo transcurrido.
"""

import pygame, time
from settings import *

class HUD:
    def __init__(self, screen, font, method_name, seed):
        self.screen = screen
        self.font = font
        self.method_name = method_name
        self.seed = seed
        self.score = 0
        self.lives = PLAYER_LIVES
        self.message = ""
        self.message_timer = 0
        self.t0 = time.time()

    def update(self, score, lives, message=None):
        self.score = score
        self.lives = lives
        if message:
            self.message = message
            self.message_timer = 120

    def _fmt_time(self):
        t = int(time.time() - self.t0)
        m, s = divmod(t, 60)
        return f"{m:02d}:{s:02d}"

    def draw(self):
        # barra superior
        pygame.draw.rect(self.screen, BLUE, (0, 0, WIDTH, 80))
        title = self.font.render("RANDOMPAC", True, YELLOW)
        self.screen.blit(title, (20, 20))

        score_text = self.font.render(f"Puntaje: {self.score}", True, WHITE)
        self.screen.blit(score_text, (250, 20))

        lives_text = self.font.render(f"Vidas: {self.lives}", True, WHITE)
        self.screen.blit(lives_text, (430, 20))

        time_text = self.font.render(f"Tiempo: {self._fmt_time()}", True, WHITE)
        self.screen.blit(time_text, (600, 20))

        method_text = self.font.render(f"Método: {self.method_name}", True, YELLOW)
        self.screen.blit(method_text, (20, 50))

        seed_text = self.font.render(f"Semilla: {self.seed if self.seed else 'Auto'}", True, GRAY)
        self.screen.blit(seed_text, (430,  Fifty:=50))  # keep alignment
