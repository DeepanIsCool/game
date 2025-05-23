import pygame
import os

class AudioManager:
    def __init__(self):
        self.sounds = {}
        self.music = None
        self.volume = 0.5
        self.sound_volume = 0.7
        
    def load_sounds(self):
        """Load all sound effects"""
        sound_dir = os.path.join('assets', 'sounds')
        
        sound_files = {
            'hover': 'hover.wav',
            'click': 'click.wav',
            'start': 'start_game.wav',
            'transition': 'transition.wav'
        }
        
        for sound_name, file_name in sound_files.items():
            try:
                sound_path = os.path.join(sound_dir, file_name)
                if os.path.exists(sound_path):
                    self.sounds[sound_name] = pygame.mixer.Sound(sound_path)
                    self.sounds[sound_name].set_volume(self.sound_volume)
            except pygame.error:
                print(f"Could not load sound: {file_name}")
                
    def load_music(self):
        """Load and start background music"""
        try:
            music_path = os.path.join('assets', 'sounds', 'menu_music.wav')
            if os.path.exists(music_path):
                pygame.mixer.music.load(music_path)
                pygame.mixer.music.set_volume(self.volume)
                pygame.mixer.music.play(-1)  # Loop indefinitely
        except pygame.error:
            print("Could not load background music")
            
    def play_sound(self, sound_name):
        """Play a sound effect if sounds are enabled"""
        if sound_name in self.sounds and self.sound_volume > 0:
            self.sounds[sound_name].play()
            
    def set_volume(self, volume):
        """Set music volume"""
        self.volume = max(0.0, min(1.0, volume))
        pygame.mixer.music.set_volume(self.volume)
        
    def set_sound_volume(self, volume):
        """Set sound effects volume"""
        self.sound_volume = max(0.0, min(1.0, volume))
        for sound in self.sounds.values():
            sound.set_volume(self.sound_volume)
            
    def toggle_music(self):
        """Toggle music on/off"""
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.pause()
        else:
            pygame.mixer.music.unpause()
            
    def toggle_sound(self):
        """Toggle sound effects on/off"""
        new_volume = 0.0 if self.sound_volume > 0 else 0.7
        self.set_sound_volume(new_volume)
