# main.py
import pygame, sys
from os.path import join
from settings import WIDTH, HEIGHT, BG_COLOR
from core.state import AppState
from ui.menu import StartScreen, MainMenu, PlayWizard, OverlayControls, PauseMenu, DeathOverlay, StatsScreen
from audio.music import MusicManager
from storage.profile import set_music_enabled, is_music_enabled, update_stats
from logic.random_generators import LCG, MiddleSquare, PAM
from ui.map_editor import MapEditor

# importa tu GameLoop real
from core.game_loop import GameLoop
# importa tu RNG registry si lo tienes (aquí finge)
RNG_MAP = {
    "LCG": LCG,
    "Middle-Square": MiddleSquare,
    "PAM": PAM
}

def main():
    pygame.init()
    pygame.mixer.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()

    # música
    music = MusicManager(music_path=join("assets", "sounds", "start_theme.mp3"), volume=0.4)    
    #if is_music_enabled(): music.play_loop()

    state = AppState.START
    ctx = {}
    start = StartScreen(screen, WIDTH, HEIGHT, music_mgr=music, bg_img=None)
    main_menu = None
    wizard = None
    overlay = None
    pause_menu = None
    death = None
    game = None
    stats_screen = None
    map_editor = None

    while True:
        screen.fill(BG_COLOR)
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            # toggle música con M (en menús también)
            if e.type == pygame.KEYDOWN and e.key == pygame.K_m:
                music.set_enabled(not music.enabled)
                set_music_enabled(music.enabled)

            # estados
            if state == AppState.START:
                ns, data = start.handle_event(e)
                if ns: state = ns; ctx.update(data or {})
            elif state == AppState.MENU and main_menu:
                ns, data = main_menu.handle_event(e)
                if ns: state = ns; ctx.update(data or {})
            elif state == AppState.WIZARD and wizard:
                ns, data = wizard.handle_event(e)
                if ns: state = ns; ctx.update(data or {})
            elif state == AppState.PRE_GAME and overlay:
                ns, data = overlay.handle_event(e)
                if ns:
                    # unir config nueva y avanzar
                    ctx.update(data or {})
                    config = ctx.get("config", {})
                    rng_name = config.get("rng", "LCG")
                    seed = config.get("seed") or 12345
                    rng_cls = RNG_MAP.get(rng_name, list(RNG_MAP.values())[0])  # fallback seguro
                    game = GameLoop(screen, rng_cls, rng_name, seed, config=config)
                    if is_music_enabled():
                        music.play_loop()
                    state = ns
            elif state == AppState.GAME and game:
                if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                    pygame.mixer.music.pause()
                    state = AppState.PAUSE
                    pause_menu = PauseMenu(screen, WIDTH, HEIGHT, music_mgr=music)
            elif state == AppState.PAUSE and pause_menu:
                act, _ = pause_menu.handle_event(e)
                if act == "resume":
                    pygame.mixer.music.unpause()
                    state = AppState.GAME
                elif act == "options":
                    state = AppState.WIZARD
                    wizard = PlayWizard(screen, WIDTH, HEIGHT, {"player": ctx.get("player")})
                elif act == "home":
                    pygame.mixer.music.stop()
                    state = AppState.MENU
                elif act == "quit":
                    pygame.quit(); sys.exit()
            elif state == AppState.DEATH and death:
                opt, _ = death.handle_event(e)
                if opt == "Volver al inicio":
                    state = AppState.MENU
                elif opt == "Reintentar":
                    state = AppState.PRE_GAME
                    overlay = OverlayControls(screen, WIDTH, HEIGHT, ctx.get("config", {}))
                elif opt == "Reintentar con otra configuración":
                    state = AppState.WIZARD
                    wizard = PlayWizard(screen, WIDTH, HEIGHT, {"player": ctx.get("player")})
            elif state == AppState.STATS:
                # Si no existe, crear la pantalla de estadísticas
                if stats_screen is None:
                    stats_screen = StatsScreen(screen, WIDTH, HEIGHT)

                # Manejar eventos (para scroll o volver atrás)
                ns, data = stats_screen.handle_event(e)
                if ns:  # si se presionó ESC o Enter, volver al menú
                    state = ns
                    stats_screen = None  # resetear para recargar la próxima vez
            elif state == AppState.MAP_EDITOR and map_editor:
                ns, data = map_editor.handle_event(e)
                if ns:
                    state = ns
                    map_editor = None
                    
        # draw/update por estado
        if state == AppState.START:
            start.draw()
        elif state == AppState.MENU:
            if not main_menu:
                main_menu = MainMenu(screen, WIDTH, HEIGHT, music_mgr=music, context=ctx)
            main_menu.draw()
        elif state == AppState.WIZARD:
            if not wizard:
                wizard = PlayWizard(screen, WIDTH, HEIGHT, context=ctx)
            wizard.draw()
        elif state == AppState.PRE_GAME:
            if not overlay:
                overlay = OverlayControls(screen, WIDTH, HEIGHT, config=ctx.get("config", {}))
            overlay.draw()
        elif state == AppState.GAME and game:
            # corre el game loop de un paso (tu GameLoop ya tiene run(); aquí mostramos tick integrado)
            dt = clock.tick(60)
            game.update(dt)
            game.draw()
            # ejemplo: detectar muerte o fin para pasar a DEATH
            if not game.running:
                # guarda stats demo
                update_stats(ctx.get("player","Anon"), score=getattr(game.player, "score", 0),
                    time_s=60, config=ctx.get("config", {}))
                state = AppState.DEATH
                stats = {
                    "Puntaje": getattr(game.player, "score", 0),
                    "Tiempo (s)": 60,
                    "result": getattr(game, "result", "lose")
                }
                death = DeathOverlay(screen, WIDTH, HEIGHT, stats)

        elif state == AppState.PAUSE and pause_menu:
            pause_menu.draw()
        elif state == AppState.DEATH and death:
            death.draw()
        elif state == AppState.STATS:
            if stats_screen:
                stats_screen.draw()
        elif state == AppState.MAP_EDITOR:
            if not map_editor:
                map_editor = MapEditor(screen, WIDTH, HEIGHT)
            map_editor.draw()
            
        pygame.display.flip()
        clock.tick(60)
        
if __name__ == "__main__":
    main()
