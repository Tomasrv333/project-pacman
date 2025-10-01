
import pygame
from settings import TILE_SIZE, PLAYER_SPEED, YELLOW
from math import copysign

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, grid):
        super().__init__()
        self.grid = grid
        self.image = pygame.Surface((TILE_SIZE-4, TILE_SIZE-4), pygame.SRCALPHA)
        pygame.draw.circle(self.image, YELLOW, (TILE_SIZE//2 -2, TILE_SIZE//2 -2), (TILE_SIZE//2 -4))
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.vel = pygame.Vector2(0, 0)
        self.lives = 3
        self.score = 0

    def update(self, dt, walls):
        keys = pygame.key.get_pressed()
        self.vel.x = (keys[pygame.K_RIGHT] - keys[pygame.K_LEFT]) * PLAYER_SPEED
        self.vel.y = (keys[pygame.K_DOWN]  - keys[pygame.K_UP])    * PLAYER_SPEED

        # movimiento eje X
        self.rect.x += int(self.vel.x)
        for w in walls:
            if self.rect.colliderect(w):
                self.rect.x -= int(self.vel.x)
                break

        # eje Y
        self.rect.y += int(self.vel.y)
        for w in walls:
            if self.rect.colliderect(w):
                self.rect.y -= int(self.vel.y)
                break
