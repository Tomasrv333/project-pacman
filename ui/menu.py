# ui/menu.py
import pygame
import time
from core.state import AppState
from storage.profile import ensure_player, load_db, is_music_enabled, set_music_enabled, get_stats
from audio.music import MusicManager

BTN_BG = (20, 20, 60)
BTN_BG_H = (40, 40, 100)
TXT = (255,255,255)
HINT = (200, 220, 255)
YELLOW = (255, 220, 0)

def draw_label(screen, font, text, center, color=TXT):
    surf = font.render(text, True, color)
    rect = surf.get_rect(center=center)
    screen.blit(surf, rect)
    return rect

class FloatingButtons:
    """Botones flotantes: música y ayuda. Visible en menús/overlays."""
    def __init__(self, music_mgr: MusicManager, width, height):
        self.music_mgr = music_mgr
        self.width, self.height = width, height
        self.help_hover = False
        self.rect_music = pygame.Rect(width-58, height-58, 48, 48)
        self.rect_help  = pygame.Rect(width-116, height-58, 48, 48)
        self.font = pygame.font.SysFont("arial", 20)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.help_hover = self.rect_help.collidepoint(event.pos)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect_music.collidepoint(event.pos):
                # toggle music flag (caller debe persistir en JSON)
                self.music_mgr.set_enabled(not self.music_mgr.enabled)
        return None, None
        
    def draw(self, screen):
        # help
        pygame.draw.rect(screen, BTN_BG, self.rect_help, border_radius=8)
        draw_label(screen, self.font, "?", self.rect_help.center, YELLOW)
        # tooltip
        if self.help_hover:
            tip = "Cómo jugar: Flechas para moverse, ESC pausa, Enter aceptar."
            tip_surf = self.font.render(tip, True, TXT)
            screen.blit(tip_surf, (self.rect_help.left - tip_surf.get_width() + 48, self.rect_help.top - 28))

        # music
        pygame.draw.rect(screen, BTN_BG, self.rect_music, border_radius=8)
        icon = "♪" if self.music_mgr.enabled else "×"
        draw_label(screen, self.font, icon, self.rect_music.center, TXT)

class StartScreen:
    def __init__(self, screen, width, height, music_mgr: MusicManager, bg_img=None):
        self.screen = screen
        self.W, self.H = width, height
        self.music_mgr = music_mgr
        self.bg = bg_img
        self.font_t = pygame.font.SysFont("arialblack", 56)
        self.font_i = pygame.font.SysFont("arial", 28)
        self.name = ""
        self.floats = FloatingButtons(music_mgr, width, height)

    def handle_event(self, event):
        self.floats.handle_event(event)
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN and self.name.strip():
                ensure_player(self.name.strip())
                return AppState.MENU, {"player": self.name.strip()}
            elif event.key == pygame.K_BACKSPACE:
                self.name = self.name[:-1]
            else:
                ch = event.unicode
                if ch.isalnum() or ch in " _-.":
                    self.name += ch
        return None, None

    def draw(self):
        if self.bg: self.screen.blit(self.bg, (0,0))
        draw_label(self.screen, self.font_t, "RANDOMPAC", (self.W//2, self.H//3), YELLOW)
        draw_label(self.screen, self.font_i, "Escribe tu nombre y presiona Enter", (self.W//2, self.H//3+60), HINT)
        # input visual
        txt = self.name if self.name else "Tu nombre…"
        box = pygame.Rect(self.W//2-220, self.H//2-24, 440, 48)
        pygame.draw.rect(self.screen, BTN_BG, box, border_radius=12)
        pygame.draw.rect(self.screen, (90,90,140), box, 2, border_radius=12)
        font_in = pygame.font.SysFont("consolas", 26)
        t_s = font_in.render(txt, True, TXT)
        self.screen.blit(t_s, (box.x+16, box.y+10))
        self.floats.draw(self.screen)

class MainMenu:
    OPTIONS = ["Jugar", "Enciclopedia", "Estadísticas", "Configuraciones"]
    def __init__(self, screen, width, height, music_mgr: MusicManager, context: dict):
        self.screen = screen; self.W=width; self.H=height
        self.font = pygame.font.SysFont("arial", 34)
        self.sel = 0
        self.player = context.get("player")
        self.floats = FloatingButtons(music_mgr, width, height)

    def handle_event(self, event):
        self.floats.handle_event(event)
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_UP, pygame.K_w):
                self.sel = (self.sel-1) % len(self.OPTIONS)
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self.sel = (self.sel+1) % len(self.OPTIONS)
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                opt = self.OPTIONS[self.sel]
                if opt == "Jugar": return AppState.WIZARD, {}
                if opt == "Enciclopedia": return AppState.ENCYCLOPEDIA, {}
                if opt == "Estadísticas": return AppState.STATS, {}
                if opt == "Configuraciones": return AppState.SETTINGS, {}
        return None, None

    def draw(self):
        title = f"Hola, {self.player}"
        draw_label(self.screen, self.font, title, (self.W//2, 140), YELLOW)
        for i,opt in enumerate(self.OPTIONS):
            rect = pygame.Rect(self.W//2-180, 220+i*70, 360, 52)
            pygame.draw.rect(self.screen, BTN_BG_H if i==self.sel else BTN_BG, rect, border_radius=12)
            draw_label(self.screen, self.font, opt, rect.center, TXT)
        self.floats.draw(self.screen)

class PlayWizard:
    RNGS = ["LCG", "Middle-Square", "Blum-Blum-Shub", "Xorshift"]
    DIFFS = ["Clásico", "Difícil", "Extremo"]
    MAPS = ["Clásico", "Creativo", "Vacío"]
    FIELDS = ["Mapa", "Dificultad", "RNG", "Semilla (opcional)"]
    def __init__(self, screen, width, height, context: dict):
        self.screen=screen; self.W=width; self.H=height
        self.font = pygame.font.SysFont("arial", 28)
        self.sel = 0
        self.map_i=0; self.diff_i=0; self.rng_i=0; self.seed_txt=""
        self.player = context.get("player")

    def _value_for(self, idx):
        if idx==0: return self.MAPS[self.map_i]
        if idx==1: return self.DIFFS[self.diff_i]
        if idx==2: return self.RNGS[self.rng_i]
        if idx==3: return self.seed_txt or "(auto)"
        return ""

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_UP, pygame.K_w):   self.sel = (self.sel-1) % len(self.FIELDS)
            elif event.key in (pygame.K_DOWN, pygame.K_s): self.sel = (self.sel+1) % len(self.FIELDS)
            elif event.key in (pygame.K_LEFT, pygame.K_a):
                if self.sel==0: self.map_i = (self.map_i-1)%len(self.MAPS)
                elif self.sel==1: self.diff_i = (self.diff_i-1)%len(self.DIFFS)
                elif self.sel==2: self.rng_i = (self.rng_i-1)%len(self.RNGS)
            elif event.key in (pygame.K_RIGHT, pygame.K_d):
                if self.sel==0: self.map_i = (self.map_i+1)%len(self.MAPS)
                elif self.sel==1: self.diff_i = (self.diff_i+1)%len(self.DIFFS)
                elif self.sel==2: self.rng_i = (self.rng_i+1)%len(self.RNGS)
            elif self.sel==3:
                if event.key == pygame.K_BACKSPACE: self.seed_txt = self.seed_txt[:-1]
                elif event.key == pygame.K_RETURN:
                    # listo → pasar al overlay de controles
                    cfg = {
                        "player": self.player,
                        "map": self.MAPS[self.map_i],
                        "difficulty": self.DIFFS[self.diff_i],
                        "rng": self.RNGS[self.rng_i],
                        "seed": self.seed_txt.strip() if self.seed_txt.strip() else None,
                    }
                    return AppState.PRE_GAME, {"config": cfg}
                else:
                    ch = event.unicode
                    if ch.isalnum() or ch in "-_.":
                        self.seed_txt += ch
            elif event.key == pygame.K_RETURN:
                cfg = {
                    "player": self.player,
                    "map": self.MAPS[self.map_i],
                    "difficulty": self.DIFFS[self.diff_i],
                    "rng": self.RNGS[self.rng_i],
                    "seed": self.seed_txt.strip() if self.seed_txt.strip() else None,
                }
                return AppState.PRE_GAME, {"config": cfg}
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return AppState.MENU, {}
        return None, None

    def draw(self):
        draw_label(self.screen, self.font, "Configuración de partida (Enter para iniciar)", (self.W//2, 120), YELLOW)
        for i, field in enumerate(self.FIELDS):
            rect = pygame.Rect(self.W//2-260, 180+i*70, 520, 56)
            pygame.draw.rect(self.screen, BTN_BG_H if i==self.sel else BTN_BG, rect, border_radius=12)
            draw_label(self.screen, self.font, f"{field}: {self._value_for(i)}", rect.center, TXT)
        font_hint = pygame.font.SysFont("arial", 22)
        hint = font_hint.render("Presiona ESC para volver", True, (180, 190, 210))
        self.screen.blit(hint, (30, self.H - 40))

class OverlayControls:
    """Overlay previo al juego con los controles."""
    def __init__(self, screen, width, height, config: dict):
        self.screen=screen; self.W=width; self.H=height
        self.font = pygame.font.SysFont("arial", 28)
        self.config = config
        self.timer = 0

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return AppState.WIZARD, {"config": self.config}  # volver al wizard
            return AppState.GAME, {"config": self.config}
        return None, None

    def draw(self):
        overlay = pygame.Surface((self.W, self.H), pygame.SRCALPHA)
        overlay.fill((0,0,0,160))
        self.screen.blit(overlay, (0,0))
        y = 140
        draw_label(self.screen, self.font, "CONTROLES", (self.W//2, y), YELLOW); y+=50
        for line in [
            "Flechas: mover", "ESC: Pausa", "Enter: Aceptar", "M: Música ON/OFF", "? : Ayuda (hover)",
            f"Dificultad: {self.config.get('difficulty')}  RNG: {self.config.get('rng')}",
            f"Mapa: {self.config.get('map')}  Semilla: {self.config.get('seed') or '(auto)'}",
            "Presiona cualquier tecla para comenzar…"
        ]:
            draw_label(self.screen, self.font, line, (self.W//2, y)); y += 36

class PauseMenu:
    OPTIONS = ["Continuar", "Opciones de juego", "Volver al inicio", "Salir"]
    def __init__(self, screen, width, height, music_mgr: MusicManager):
        self.screen=screen; self.W=width; self.H=height
        self.font = pygame.font.SysFont("arial", 34)
        self.sel = 0
        self.floats = FloatingButtons(music_mgr, width, height)

    def handle_event(self, event):
        self.floats.handle_event(event)
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_UP, pygame.K_w): self.sel=(self.sel-1)%len(self.OPTIONS)
            elif event.key in (pygame.K_DOWN, pygame.K_s): self.sel=(self.sel+1)%len(self.OPTIONS)
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                opt = self.OPTIONS[self.sel]
                if opt=="Continuar": return "resume", None
                if opt=="Opciones de juego": return "options", None  # aquí podrías reabrir el wizard con valores actuales
                if opt=="Volver al inicio": return "home", None
                if opt=="Salir": return "quit", None
        return None, None

    def draw(self):
        overlay = pygame.Surface((self.W, self.H), pygame.SRCALPHA)
        overlay.fill((0,0,0,160)); self.screen.blit(overlay, (0,0))
        draw_label(self.screen, self.font, "PAUSA", (self.W//2, 200), YELLOW)
        for i,opt in enumerate(self.OPTIONS):
            rect = pygame.Rect(self.W//2-200, 260+i*64, 400, 52)
            pygame.draw.rect(self.screen, BTN_BG_H if i==self.sel else BTN_BG, rect, border_radius=12)
            draw_label(self.screen, self.font, opt, rect.center, TXT)
        self.floats.draw(self.screen)

class DeathOverlay:
    OPTIONS = ["Volver al inicio", "Reintentar", "Reintentar con otra configuración"]
    def __init__(self, screen, width, height, stats: dict):
        self.screen=screen; self.W=width; self.H=height
        self.font = pygame.font.SysFont("arial", 30)
        self.sel = 0
        self.stats = stats or {}

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_UP, pygame.K_w): self.sel=(self.sel-1)%len(self.OPTIONS)
            elif event.key in (pygame.K_DOWN, pygame.K_s): self.sel=(self.sel+1)%len(self.OPTIONS)
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                return self.OPTIONS[self.sel], None
        return None, None

    def draw(self):
        overlay = pygame.Surface((self.W, self.H), pygame.SRCALPHA)
        overlay.fill((0,0,0,180)); self.screen.blit(overlay, (0,0))
        draw_label(self.screen, self.font, "¡Has muerto!", (self.W//2, 180), YELLOW)
        y=230
        for k,v in self.stats.items():
            draw_label(self.screen, self.font, f"{k}: {v}", (self.W//2, y)); y+=34
        for i,opt in enumerate(self.OPTIONS):
            rect = pygame.Rect(self.W//2-260, y+20+i*64, 520, 52)
            pygame.draw.rect(self.screen, BTN_BG_H if i==self.sel else BTN_BG, rect, border_radius=12)
            draw_label(self.screen, self.font, opt, rect.center, TXT)
        font_hint = pygame.font.SysFont("arial", 22)
        hint = font_hint.render("Presiona ESC para volver", True, (180, 190, 210))
        self.screen.blit(hint, (30, self.H - 40))
            
class StatsScreen:
    """Pantalla de estadísticas globales adaptativa (responde al tamaño de ventana)."""
    def __init__(self, screen, width, height):
        self.screen = screen
        self.W, self.H = width, height
        self.font_t = pygame.font.SysFont("arialblack", 46)
        self.font_h = pygame.font.SysFont("arial", 22, bold=True)
        self.font_b = pygame.font.SysFont("consolas", 21)
        self.players = []
        self._load_data()

    def _load_data(self):
        db = load_db()
        players = db.get("players", {})
        data = []
        for name, p in players.items():
            data.append({
                "name": name,
                "best": p.get("best_score", 0),
                "games": p.get("games", 0),
                "rng": p.get("best_rng", "LCG"),
                "time": p.get("total_time_s", 0),
                "created": p.get("created_at", 0),
            })
        # ordenar por puntaje
        self.players = sorted(data, key=lambda d: d["best"], reverse=True)

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return AppState.MENU, {}  # volver al menú principal
        return None, None

    def draw(self):
        self.screen.fill((10, 15, 40))
        draw_label(self.screen, self.font_t, "ESTADÍSTICAS", (self.W // 2, 70), (255, 220, 0))
        font_hint = pygame.font.SysFont("arial", 22)
        hint = font_hint.render("Presiona ESC para volver", True, (180, 190, 210))
        self.screen.blit(hint, (30, self.H - 40))

        # === CONFIGURACIÓN DE TABLA ===
        headers = ["Jugador", "Método RNG", "Puntaje Máx.", "Partidas", "Tiempo (min)", "Creado"]
        n_cols = len(headers)
        margin_x = 50
        margin_y = 130
        usable_width = self.W - margin_x * 2
        col_spacing = usable_width / n_cols  # no n_cols-1

        # === DIBUJAR ENCABEZADOS ===
        y_head = margin_y
        for i, h in enumerate(headers):
            x = margin_x + i * col_spacing + col_spacing / 2
            draw_label(self.screen, self.font_h, h, (x, y_head), (200, 220, 255))

        pygame.draw.line(
            self.screen, (70, 80, 120, 80),
            (margin_x, y_head + 22), (self.W - margin_x, y_head + 22), 2
        )

        # === FILAS ===
        row_height = 42
        y = y_head + 50
        sep_color = (50, 60, 100, 60)
        visible_players = self.players[:12]  # máximo visible sin scroll

        for idx, p in enumerate(visible_players):
            created = time.strftime("%d/%m/%y", time.localtime(p["created"])) if p["created"] else "-"
            color = (255, 215, 0) if idx == 0 else (255, 255, 255)
            values = [
                p["name"],
                p["rng"],
                str(p["best"]),
                str(p["games"]),
                str(p["time"] // 60),
                created,
            ]
            for i, val in enumerate(values):
                x = margin_x + i * col_spacing + col_spacing / 2
                draw_label(self.screen, self.font_b, val, (x, y), color)

            # línea horizontal separadora
            pygame.draw.line(self.screen, (40, 45, 80, 60),
                            (margin_x, y + 18), (self.W - margin_x, y + 18), 1)
            y += row_height

        # === LÍNEAS VERTICALES ===
        for i in range(n_cols + 1):
            x = margin_x + i * col_spacing
            pygame.draw.line(self.screen, sep_color,
                            (x, y_head + 25), (x, y - 10), 1)
