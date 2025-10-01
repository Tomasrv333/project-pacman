
import pygame
from settings import TILE_SIZE, GHOST_SPEED, RED
import random

DIRS = [pygame.Vector2(1,0), pygame.Vector2(-1,0), pygame.Vector2(0,1), pygame.Vector2(0,-1)]

class Ghost(pygame.sprite.Sprite):
    def __init__(self, x, y, rng):
        super().__init__()
        self.image = pygame.Surface((TILE_SIZE-4, TILE_SIZE-4), pygame.SRCALPHA)
        pygame.draw.rect(self.image, RED, (2,2,TILE_SIZE-8,TILE_SIZE-8), border_radius=6)
        self.rect = self.image.get_rect(center=(x, y))
        self.rng = rng
        self.dir = random.choice(DIRS)
        self.timer = 0

    def update(self, dt, walls):
        self.timer += dt
        # cada cierto tiempo, decide nueva dirección con el RNG inyectado
        if self.timer > 300:  # ms
            r = self.rng.random()  # [0,1)
            idx = int(r * len(DIRS)) % len(DIRS)
            self.dir = DIRS[idx]
            self.timer = 0

        old = self.rect.copy()
        self.rect.x += int(self.dir.x * GHOST_SPEED)
        self.rect.y += int(self.dir.y * GHOST_SPEED)
        # choque pared: retrocede y elige otra dirección
        for w in walls:
            if self.rect.colliderect(w):
                self.rect = old
                # elige otra
                idx = (idx + 1) % len(DIRS) if 'idx' in locals() else 0
                self.dir = DIRS[idx]
                break
