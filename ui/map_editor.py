# ui/map_editor.py
import pygame, os, json
from core.state import AppState

CELL_SIZE = 24
GRID_W, GRID_H = 28, 31
MAPS_PATH = os.path.join("storage", "maps")

# Leyenda igual a logic/map.py
TILES = {
    0: ("Vacío", (15, 15, 30)),
    1: ("Muro", (0, 0, 180)),
    2: ("Punto", (220, 220, 100)),
    3: ("Power Dot", (255, 80, 80)),
    4: ("Puerta", (180, 90, 0))
}

class MapEditor:
    def __init__(self, screen, width, height):
        self.screen = screen
        self.W, self.H = width, height
        self.grid = [[0]*GRID_W for _ in range(GRID_H)]
        self.selected_tile = 1
        self.font = pygame.font.SysFont("arial", 20)
        os.makedirs(MAPS_PATH, exist_ok=True)

        # posición del cursor
        self.cursor_x = 0
        self.cursor_y = 0

        # modo de guardado
        self.saving = False
        self.save_name = ""

    def handle_event(self, event):
        if self.saving:
            # estamos en modo de escritura del nombre
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    self.finish_save()
                elif event.key == pygame.K_BACKSPACE:
                    self.save_name = self.save_name[:-1]
                elif event.key == pygame.K_ESCAPE:
                    self.saving = False
                    self.save_name = ""
                else:
                    ch = event.unicode
                    if ch.isalnum() or ch in "-_":
                        self.save_name += ch
            return None, None

        # === Modo normal ===
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return AppState.MENU, {}

            elif event.key == pygame.K_UP:
                self.cursor_y = (self.cursor_y - 1) % GRID_H
            elif event.key == pygame.K_DOWN:
                self.cursor_y = (self.cursor_y + 1) % GRID_H
            elif event.key == pygame.K_LEFT:
                self.cursor_x = (self.cursor_x - 1) % GRID_W
            elif event.key == pygame.K_RIGHT:
                self.cursor_x = (self.cursor_x + 1) % GRID_W
            elif event.key in (pygame.K_SPACE, pygame.K_RETURN):
                self.grid[self.cursor_y][self.cursor_x] = self.selected_tile
            elif event.key in (pygame.K_BACKSPACE, pygame.K_0):
                self.grid[self.cursor_y][self.cursor_x] = 0
            elif event.unicode in ("1", "2", "3", "4"):
                self.selected_tile = int(event.unicode)
            elif event.key == pygame.K_s:
                # activar modo de guardado visual
                self.saving = True
                self.save_name = ""
            elif event.key == pygame.K_l:
                self.load_map()

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            x, y = event.pos
            c, r = x // CELL_SIZE, y // CELL_SIZE
            if 0 <= c < GRID_W and 0 <= r < GRID_H:
                self.grid[r][c] = self.selected_tile
                self.cursor_x, self.cursor_y = c, r

        return None, None

    def draw(self):
        self.screen.fill((10, 15, 40))

        # --- Dibujar celdas ---
        for r in range(GRID_H):
            for c in range(GRID_W):
                color = TILES[self.grid[r][c]][1]
                pygame.draw.rect(self.screen, color, (c*CELL_SIZE, r*CELL_SIZE, CELL_SIZE-1, CELL_SIZE-1))

        # --- Rejilla ---
        for r in range(GRID_H+1):
            pygame.draw.line(self.screen, (30,30,60), (0, r*CELL_SIZE), (GRID_W*CELL_SIZE, r*CELL_SIZE))
        for c in range(GRID_W+1):
            pygame.draw.line(self.screen, (30,30,60), (c*CELL_SIZE, 0), (c*CELL_SIZE, GRID_H*CELL_SIZE))

        # --- Cursor ---
        rect = pygame.Rect(self.cursor_x*CELL_SIZE, self.cursor_y*CELL_SIZE, CELL_SIZE, CELL_SIZE)
        pygame.draw.rect(self.screen, (255, 255, 0), rect, 2)

        # --- HUD ---
        y_hud = self.H - 60
        msg = "[Flechas] Mover | [1–4] Cambiar | [ESP/ENTER] Colocar | [S] Guardar | [L] Cargar | [ESC] Volver"
        txt = self.font.render(msg, True, (255,255,255))
        self.screen.blit(txt, (20, y_hud))
        cur_tile = TILES[self.selected_tile][0]
        sel = self.font.render(f"Bloque actual: {cur_tile}", True, (255,220,0))
        self.screen.blit(sel, (20, y_hud-28))

        # --- Si estamos guardando, mostrar input visual ---
        if self.saving:
            overlay = pygame.Surface((self.W, self.H), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            self.screen.blit(overlay, (0, 0))

            box = pygame.Rect(self.W//2 - 180, self.H//2 - 40, 360, 80)
            pygame.draw.rect(self.screen, (50, 50, 90), box, border_radius=10)
            pygame.draw.rect(self.screen, (200, 200, 255), box, 2, border_radius=10)

            prompt = self.font.render("Nombre del mapa:", True, (255, 255, 255))
            self.screen.blit(prompt, (box.x + 20, box.y + 10))

            name = self.font.render(self.save_name or "Escribe aquí...", True, (255, 255, 0))
            self.screen.blit(name, (box.x + 20, box.y + 40))

    def finish_save(self):
        if not self.save_name.strip():
            self.saving = False
            return
        path = os.path.join(MAPS_PATH, f"{self.save_name.strip()}.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.grid, f)
        print(f"✅ Mapa guardado como {path}")
        self.saving = False
        self.save_name = ""

    def load_map(self):
        files = [f for f in os.listdir(MAPS_PATH) if f.endswith(".json")]
        if not files:
            print("⚠️ No hay mapas guardados.")
            return
        path = os.path.join(MAPS_PATH, files[-1])
        with open(path, "r", encoding="utf-8") as f:
            self.grid = json.load(f)
        print(f"📂 Mapa cargado: {files[-1]}")
