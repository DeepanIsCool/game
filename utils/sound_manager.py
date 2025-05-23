import pygame
import os

class SoundManager:
    def __init__(self):
        pygame.mixer.init()
        self.sounds = {}
        self.music = None
        self.sound_enabled = True
        self.music_enabled = True
        
    def load_sound(self, name, file_path):
        """Load a sound effect."""
        if os.path.exists(file_path):
            self.sounds[name] = pygame.mixer.Sound(file_path)
            
    def play_sound(self, name):
        """Play a sound effect."""
        if self.sound_enabled and name in self.sounds:
            self.sounds[name].play()
            
    def load_music(self, file_path):
        """Load background music."""
        if os.path.exists(file_path):
            self.music = file_path
            
    def play_music(self, loops=-1):
        """Play background music."""
        if self.music_enabled and self.music:
            pygame.mixer.music.load(self.music)
            pygame.mixer.music.play(loops)
            
    def stop_music(self):
        """Stop background music."""
        pygame.mixer.music.stop()
        
    def toggle_sound(self):
        """Toggle sound effects on/off."""
        self.sound_enabled = not self.sound_enabled
        
    def toggle_music(self):
        """Toggle background music on/off."""
        self.music_enabled = not self.music_enabled
        if not self.music_enabled:
            self.stop_music()
        elif self.music:
            self.play_music()
            
    def set_sound_volume(self, volume):
        """Set volume for sound effects (0.0 to 1.0)."""
        for sound in self.sounds.values():
            sound.set_volume(volume)
            
    def set_music_volume(self, volume):
        """Set volume for background music (0.0 to 1.0)."""
        pygame.mixer.music.set_volume(volume)
