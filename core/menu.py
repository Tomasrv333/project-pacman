"""
core/menu.py — RandomPac (v1.0)
===============================
Menú retro animado para selección de método pseudoaleatorio y semilla.
"""

import pygame, sys
from settings import *
from logic.random_generators import LCG, MiddleSquare, PAM

class Menu:
    def __init__(self, screen):
        self.screen = screen
        self.font_title = pygame.font.Font(FONT_MAIN, 64)
        self.font_option = pygame.font.Font(FONT_MAIN, 32)
        self.clock = pygame.time.Clock()

        # Métodos disponibles
        self.methods = [
            (LCG, "Congruencial Lineal", "Generador clásico, reproducible y estable."),
            (MiddleSquare, "Cuadrado Medio", "Histórico, basado en el cuadrado de la semilla."),
            (PAM, "Promedio Aritmético Múltiple", "Método propio del grupo con promedios ponderados.")
        ]

        self.selected = 0
        self.seed_input = ""
        self.entering_seed = False
        self.glow = 0
        self.fade_dir = 1

    def draw_text_center(self, text, font, color, y):
        surf = font.render(text, True, color)
        rect = surf.get_rect(center=(WIDTH//2, y))
        self.screen.blit(surf, rect)

    def run(self):
        while True:
            self.screen.fill(DARK_BLUE)

            # Animación parpadeante retro
            self.glow += self.fade_dir * 3
            if self.glow >= 100 or self.glow <= 0:
                self.fade_dir *= -1

            glow_color = (YELLOW[0], YELLOW[1] - min(80, self.glow), 0)

            # Título
            self.draw_text_center("RANDOMPAC", self.font_title, glow_color, 160)
            self.draw_text_center("Simulación Discreta y Aleatoriedad", self.font_option, WHITE, 220)

            # Instrucciones
            self.draw_text_center("Selecciona el método aleatorio ↓↑ y presiona ENTER", self.font_option, GRAY, 300)

            # Listado de métodos
            start_y = 360
            for i, (_, name, desc) in enumerate(self.methods):
                color = YELLOW if i == self.selected else WHITE
                self.draw_text_center(f"{i+1}. {name}", self.font_option, color, start_y + i * 60)
                if i == self.selected:
                    self.draw_text_center(desc, pygame.font.Font(FONT_MAIN, 24), GRAY, start_y + 100)

            # Entrada de semilla
            if self.entering_seed:
                self.draw_text_center(f"Ingresa semilla numérica: {self.seed_input}", self.font_option, WHITE, 700)
            else:
                self.draw_text_center("Presiona S para establecer una semilla personalizada", pygame.font.Font(FONT_MAIN, 24), GRAY, 700)

            # Eventos
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif e.type == pygame.KEYDOWN:
                    if self.entering_seed:
                        if e.key == pygame.K_RETURN:
                            self.entering_seed = False
                        elif e.key == pygame.K_BACKSPACE:
                            self.seed_input = self.seed_input[:-1]
                        elif e.unicode.isdigit():
                            self.seed_input += e.unicode
                    else:
                        if e.key == pygame.K_DOWN:
                            self.selected = (self.selected + 1) % len(self.methods)
                        elif e.key == pygame.K_UP:
                            self.selected = (self.selected - 1) % len(self.methods)
                        elif e.key == pygame.K_RETURN:
                            generator_class, name, _ = self.methods[self.selected]
                            seed = int(self.seed_input) if self.seed_input else None
                            return generator_class, name, seed
                        elif e.key == pygame.K_s:
                            self.entering_seed = True

            pygame.display.flip()
            self.clock.tick(FPS)
