# audio/sfx.py
import os, pygame

DEFAULT_MAP = {
    "dot":         ["assets/sounds/eat_dot.wav", "assets/sounds/eat_dot.ogg", "assets/sounds/eat_dot.mp3"],
    "power":       ["assets/sounds/power.wav", "assets/sounds/power.ogg"],
    "ghost_eat":   ["assets/sounds/ghost_eat.wav", "assets/sounds/ghost_eat.ogg"],
    "death":       ["assets/sounds/death.mp3", "assets/sounds/death.wav", "assets/sounds/death.ogg"],
    "frightened":  ["assets/sounds/frightened_loop.ogg"],  # opcional (loop)
    "extra_life":  ["assets/sounds/extra_life.wav"],
}

class SFX:
    def __init__(self, mapping=None, volume=0.6):
        self.map = mapping or DEFAULT_MAP
        self.cache = {}
        self.volume = volume

    def _load_first(self, paths):
        for p in paths:
            if os.path.exists(p):
                try:
                    snd = pygame.mixer.Sound(p)
                    snd.set_volume(self.volume)
                    return snd
                except Exception:
                    continue
        return None

    def play(self, name):
        snd = self.cache.get(name)
        if snd is None:
            paths = self.map.get(name, [])
            snd = self._load_first(paths) if paths else None
            self.cache[name] = snd
        if snd:
            try: snd.play()
            except Exception: pass

    def loop(self, name):
        snd = self.cache.get(name)
        if snd is None:
            paths = self.map.get(name, [])
            snd = self._load_first(paths) if paths else None
            self.cache[name] = snd
        if snd:
            try: snd.play(loops=-1)
            except Exception: pass

    def stop(self, name=None):
        if name is None:
            for s in self.cache.values():
                try: s.stop()
                except Exception: pass
        else:
            s = self.cache.get(name)
            if s:
                try: s.stop()
                except Exception: pass
