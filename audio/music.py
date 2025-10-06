# audio/music.py
import pygame
from storage.profile import is_music_enabled

class MusicManager:
    def __init__(self, music_path=None, volume=0.5):
        self.music_path = music_path
        self.volume = volume
        self.enabled = is_music_enabled()
        self._loaded = False

    def load(self):
        if self.music_path and not self._loaded:
            try:
                pygame.mixer.music.load(self.music_path)
                pygame.mixer.music.set_volume(self.volume)
                self._loaded = True
            except Exception:
                self._loaded = False

    def play_loop(self):
        if not self.enabled: return
        self.load()
        try:
            pygame.mixer.music.play(-1)
        except Exception:
            pass

    def stop(self):
        try:
            pygame.mixer.music.stop()
        except Exception:
            pass

    def set_enabled(self, enabled: bool):
        self.enabled = enabled
        if not enabled:
            self.stop()
        else:
            self.play_loop()
