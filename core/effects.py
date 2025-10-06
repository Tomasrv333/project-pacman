"""
core/effects.py — RandomPac (v1.2)
Transiciones simples (fade in/out). Se eliminaron efectos CRT por mareo visual.
"""

import pygame
from settings import *

class Transition:
    def __init__(self, screen):
        self.screen = screen

    def fade_in(self, color=DARK_BLUE, speed=8):
        surf = pygame.Surface((WIDTH, HEIGHT))
        surf.fill(color)
        for alpha in range(255, -1, -speed):
            surf.set_alpha(alpha)
            self.screen.blit(surf, (0, 0))
            pygame.display.flip()
            pygame.time.delay(8)

    def fade_out(self, color=DARK_BLUE, speed=8):
        surf = pygame.Surface((WIDTH, HEIGHT))
        surf.fill(color)
        for alpha in range(0, 255, speed):
            surf.set_alpha(alpha)
            self.screen.blit(surf, (0, 0))
            pygame.display.flip()
            pygame.time.delay(8)
