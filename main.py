
import pygame, sys, copy
from settings import *
from map import LEVEL, is_wall, has_dot, eat_dot
from player import Player
from ghost import Ghost
from random_generators import LCG, MiddleSquare, XorShift32

def build_walls(level):
    walls = []
    for r,row in enumerate(level):
        for c,val in enumerate(row):
            if val == 1:  # pared
                rect = pygame.Rect(c*TILE_SIZE, r*TILE_SIZE, TILE_SIZE, TILE_SIZE)
                walls.append(rect)
    return walls

def draw_grid(screen, level, font):
    for r,row in enumerate(level):
        for c,val in enumerate(row):
            x = c*TILE_SIZE
            y = r*TILE_SIZE
            if val == 1:  # pared
                pygame.draw.rect(screen, BLUE, (x, y, TILE_SIZE, TILE_SIZE), border_radius=4)
            elif val == 2:  # dot
                pygame.draw.circle(screen, WHITE, (x+TILE_SIZE//2, y+TILE_SIZE//2), 2)
            elif val == 3:  # power
                pygame.draw.circle(screen, WHITE, (x+TILE_SIZE//2, y+TILE_SIZE//2), 5, width=1)

def tile_at(px, py):
    c = int(px // TILE_SIZE)
    r = int(py // TILE_SIZE)
    c = max(0, min(GRID_COLS-1, c))
    r = max(0, min(GRID_ROWS-1, r))
    return c, r

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption(TITLE)
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("arial", 18)

    # estado del juego
    level = copy.deepcopy(LEVEL)
    walls = build_walls(level)

    # entidades
    player = Player(TILE_SIZE*12 + TILE_SIZE//2, TILE_SIZE*19, level)

    rngs = [LCG(seed=12345), MiddleSquare(seed=8421), XorShift32(seed=123456)]
    rng_names = ["LCG", "MiddleSquare", "XorShift32"]
    rng_idx = 0
    ghost = Ghost(TILE_SIZE*12 + TILE_SIZE//2, TILE_SIZE*9, rngs[rng_idx])

    # pantalla de título simple
    title = True
    while title:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN:
                title = False
        screen.fill(BLACK)
        t1 = font.render("PACMAN — Simulación Discreta", True, YELLOW)
        t2 = font.render("Presiona cualquier tecla para iniciar", True, WHITE)
        t3 = font.render("Cambia PRNG con teclas 1/2/3 durante el juego", True, GRAY)
        screen.blit(t1, (WIDTH//2 - t1.get_width()//2, HEIGHT//2 - 60))
        screen.blit(t2, (WIDTH//2 - t2.get_width()//2, HEIGHT//2 - 20))
        screen.blit(t3, (WIDTH//2 - t3.get_width()//2, HEIGHT//2 + 20))
        pygame.display.flip()
        clock.tick(30)

    score = 0
    lives = PLAYER_LIVES
    running = True
    while running:
        dt = clock.tick(FPS)
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_1: rng_idx = 0; ghost.rng = rngs[rng_idx]
                if e.key == pygame.K_2: rng_idx = 1; ghost.rng = rngs[rng_idx]
                if e.key == pygame.K_3: rng_idx = 2; ghost.rng = rngs[rng_idx]

        # update
        player.update(dt, walls)
        ghost.update(dt, walls)

        # comer puntos
        pc, pr = tile_at(player.rect.centerx, player.rect.centery)
        if eat_dot(level, pc, pr):
            score += DOT_SCORE

        # colisión con fantasma
        if player.rect.colliderect(ghost.rect):
            lives -= 1
            # respawn simple
            player.rect.center = (TILE_SIZE*12 + TILE_SIZE//2, TILE_SIZE*19)
            ghost.rect.center  = (TILE_SIZE*12 + TILE_SIZE//2, TILE_SIZE*9)
            if lives <= 0:
                running = False

        # draw
        screen.fill(BLACK)
        draw_grid(screen, level, font)
        screen.blit(player.image, player.rect)
        screen.blit(ghost.image, ghost.rect)

        # HUD
        hud = font.render(f"Score: {score}   Vidas: {lives}   RNG: {rng_names[rng_idx]}", True, WHITE)
        screen.blit(hud, (10, HEIGHT-32))

        pygame.display.flip()

    # pantalla fin
    end = True
    while end:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                end = False
        screen.fill(BLACK)
        t1 = font.render(f"Juego terminado — Score: {score}", True, WHITE)
        t2 = font.render("Cierra la ventana para salir.", True, GRAY)
        screen.blit(t1, (WIDTH//2 - t1.get_width()//2, HEIGHT//2 - 20))
        screen.blit(t2, (WIDTH//2 - t2.get_width()//2, HEIGHT//2 + 20))
        pygame.display.flip()
        clock.tick(30)

if __name__ == '__main__':
    main()
