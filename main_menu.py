import pygame
import sys
import math
import random
from games.gravity_flip import GravityFlipRunner
from games.color_match import ColorMatchShooter
from games.echo_maze import EchoMaze
from games.time_loop import TimeLoopDefender
from utils.audio_manager import AudioManager
from utils.settings_menu import SettingsMenu

class Star:
    def __init__(self, width, height):
        self.x = random.randint(0, width)
        self.y = random.randint(0, height)
        self.speed = random.uniform(0.5, 2.0)
        self.brightness = random.randint(100, 255)
        self.size = random.randint(1, 3)

class ArcadeGameLauncher:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        
        # Window setup
        self.WINDOW_SIZE = (800, 600)
        self.screen = pygame.display.set_mode(self.WINDOW_SIZE)
        pygame.display.set_caption("Retro Arcade Game Launcher")
        
        # Initialize audio manager
        self.audio_manager = AudioManager()
        self.audio_manager.load_sounds()
        self.audio_manager.load_music()
        
        # Initialize settings menu
        self.settings_menu = SettingsMenu(self.WINDOW_SIZE, self.audio_manager)
        self.show_settings = False
        
        # Colors
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.NEON_BLUE = (0, 255, 255)
        self.NEON_PINK = (255, 0, 255)
        
        # Fonts
        self.title_font = pygame.font.Font(None, 72)
        self.button_font = pygame.font.Font(None, 36)
        
        # Button dimensions
        self.button_width = 300
        self.button_height = 60
        self.button_margin = 20
        
        # Create game instances
        self.gravity_flip = GravityFlipRunner()
        self.color_match = ColorMatchShooter()
        self.echo_maze = EchoMaze()
        self.time_loop = TimeLoopDefender()
        
        # Game buttons with their unique properties
        self.buttons = [
            {
                "text": "Gravity Flip Runner",
                "game": self.gravity_flip,
                "color": (0, 255, 255),
                "hover_offset": 0,
                "scale": 1.0,
                "hover": False
            },
            {
                "text": "Color Match Shooter",
                "game": self.color_match,
                "color": (255, 100, 100),
                "hover_offset": 0,
                "scale": 1.0,
                "hover": False
            },
            {
                "text": "Echo Maze",
                "game": self.echo_maze,
                "color": (100, 255, 100),
                "hover_offset": 0,
                "scale": 1.0,
                "hover": False
            },
            {
                "text": "Time Loop Defender",
                "game": self.time_loop,
                "color": (255, 200, 0),
                "hover_offset": 0,
                "scale": 1.0,
                "hover": False
            }
        ]
        
        # Background stars
        self.stars = [Star(self.WINDOW_SIZE[0], self.WINDOW_SIZE[1]) 
                     for _ in range(100)]
        
        # Animation variables
        self.title_glow = 0
        self.title_glow_direction = 1
        self.frame_alpha = 255
        self.time = 0
        
    def update_stars(self):
        for star in self.stars:
            star.y += star.speed
            if star.y > self.WINDOW_SIZE[1]:
                star.y = 0
                star.x = random.randint(0, self.WINDOW_SIZE[0])
                
    def draw_stars(self):
        for star in self.stars:
            color = (star.brightness, star.brightness, star.brightness)
            pygame.draw.circle(self.screen, color, 
                             (int(star.x), int(star.y)), star.size)
                
    def draw_neon_frame(self):
        thickness = 2
        glow_color = (
            int(self.NEON_BLUE[0] * (0.5 + 0.5 * math.sin(self.time * 0.05))),
            int(self.NEON_BLUE[1] * (0.5 + 0.5 * math.sin(self.time * 0.05))),
            int(self.NEON_BLUE[2] * (0.5 + 0.5 * math.sin(self.time * 0.05)))
        )
        
        # Draw outer glow
        for i in range(3):
            pygame.draw.rect(self.screen, glow_color,
                           (i, i, 
                            self.WINDOW_SIZE[0] - i * 2,
                            self.WINDOW_SIZE[1] - i * 2),
                           thickness)
                           
    def draw_button(self, button, rect):
        # Update hover state
        old_hover = button["hover"]
        button["hover"] = rect.collidepoint(pygame.mouse.get_pos())
        
        # Play hover sound if just started hovering
        if button["hover"] and not old_hover:
            self.audio_manager.play_sound("hover")
        
        # Base button color with gradient
        gradient_surface = pygame.Surface((rect.width, rect.height))
        for i in range(rect.height):
            progress = i / rect.height
            color = [int(c * (0.8 + 0.2 * progress)) 
                    for c in button["color"]]
            pygame.draw.line(gradient_surface, color, 
                           (0, i), (rect.width, i))
            
        # Apply hover effects
        if button["hover"]:
            # Scale up
            button["scale"] = min(1.1, button["scale"] + 0.05)
            
            # Add glow effect
            glow_surface = pygame.Surface((rect.width + 20, rect.height + 20))
            glow_surface.fill(self.BLACK)
            pygame.draw.rect(glow_surface, button["color"], 
                           (0, 0, rect.width + 20, rect.height + 20), 
                           border_radius=15)
            glow_surface.set_alpha(100)
            self.screen.blit(glow_surface, 
                           (rect.x - 10, rect.y - 10))
        else:
            button["scale"] = max(1.0, button["scale"] - 0.05)
        
        # Scale button surface
        scaled_surface = pygame.transform.scale(
            gradient_surface,
            (int(rect.width * button["scale"]), 
             int(rect.height * button["scale"]))
        )
        
        # Draw button
        self.screen.blit(scaled_surface, 
                        (rect.x + rect.width * (1 - button["scale"]) / 2,
                         rect.y + rect.height * (1 - button["scale"]) / 2))
        
        # Draw text
        text_surface = self.button_font.render(button["text"], True, self.WHITE)
        text_rect = text_surface.get_rect(center=rect.center)
        self.screen.blit(text_surface, text_rect)
        
    def draw_settings_button(self):
        # Draw settings icon
        settings_rect = pygame.Rect(
            self.WINDOW_SIZE[0] - 50, 
            self.WINDOW_SIZE[1] - 50,
            40, 40
        )
        
        # Check hover
        hover = settings_rect.collidepoint(pygame.mouse.get_pos())
        color = self.NEON_BLUE if hover else self.WHITE
        
        pygame.draw.circle(self.screen, color, settings_rect.center, 20, 2)
        # Draw gear icon
        for i in range(8):
            angle = i * math.pi / 4 + self.time * 0.02
            x = settings_rect.centerx + math.cos(angle) * 15
            y = settings_rect.centery + math.sin(angle) * 15
            pygame.draw.circle(self.screen, color, (int(x), int(y)), 3)
        
        return settings_rect
        
    def draw_exit_button(self):
        exit_rect = pygame.Rect(10, self.WINDOW_SIZE[1] - 50, 40, 40)
        hover = exit_rect.collidepoint(pygame.mouse.get_pos())
        color = (255, 100, 100) if hover else (255, 0, 0)
        
        pygame.draw.rect(self.screen, color, exit_rect, 2)
        exit_text = self.button_font.render("X", True, color)
        exit_text_rect = exit_text.get_rect(center=exit_rect.center)
        self.screen.blit(exit_text, exit_text_rect)
        
        return exit_rect
        
    def transition_to_game(self, game):
        self.audio_manager.play_sound("start")
        
        # Fade out effect
        fade_surface = pygame.Surface(self.WINDOW_SIZE)
        fade_surface.fill(self.BLACK)
        
        for alpha in range(0, 255, 5):
            self.screen.blit(fade_surface, (0, 0))
            fade_surface.set_alpha(alpha)
            pygame.display.flip()
            pygame.time.delay(5)
            
        # Run the game
        game.run(self.screen)
        
        # Fade back in
        for alpha in range(255, 0, -5):
            self.screen.blit(fade_surface, (0, 0))
            fade_surface.set_alpha(alpha)
            pygame.display.flip()
            pygame.time.delay(5)
            
    def run(self):
        clock = pygame.time.Clock()
        running = True
        
        while running:
            self.time += 1
            mouse_pos = pygame.mouse.get_pos()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.show_settings:
                        self.show_settings = self.settings_menu.handle_event(event)
                        if not self.show_settings:
                            self.audio_manager.play_sound("click")
                    else:
                        # Check button clicks
                        for i, button in enumerate(self.buttons):
                            button_rect = pygame.Rect(
                                (self.WINDOW_SIZE[0] - self.button_width) // 2,
                                150 + i * (self.button_height + self.button_margin),
                                self.button_width,
                                self.button_height
                            )
                            if button_rect.collidepoint(mouse_pos):
                                self.audio_manager.play_sound("click")
                                self.transition_to_game(button["game"])
                                
                        # Check settings and exit buttons
                        settings_rect = self.draw_settings_button()
                        exit_rect = self.draw_exit_button()
                        
                        if settings_rect.collidepoint(mouse_pos):
                            self.audio_manager.play_sound("click")
                            self.show_settings = True
                        elif exit_rect.collidepoint(mouse_pos):
                            self.audio_manager.play_sound("click")
                            running = False
                            
                elif self.show_settings:
                    self.settings_menu.handle_event(event)
            
            # Update background
            self.screen.fill(self.BLACK)
            self.update_stars()
            self.draw_stars()
            
            # Draw neon frame
            self.draw_neon_frame()
            
            if not self.show_settings:
                # Update and draw title
                self.title_glow += 0.05 * self.title_glow_direction
                if self.title_glow >= 1.0 or self.title_glow <= 0.0:
                    self.title_glow_direction *= -1
                    
                title_color = (
                    int(255 * (0.7 + 0.3 * self.title_glow)),
                    int(255 * (0.7 + 0.3 * self.title_glow)),
                    int(255 * (0.7 + 0.3 * self.title_glow))
                )
                
                title_surface = self.title_font.render("CHOOSE A GAME", 
                                                     True, title_color)
                title_rect = title_surface.get_rect(
                    center=(self.WINDOW_SIZE[0] // 2, 80)
                )
                self.screen.blit(title_surface, title_rect)
                
                # Draw buttons
                for i, button in enumerate(self.buttons):
                    button_rect = pygame.Rect(
                        (self.WINDOW_SIZE[0] - self.button_width) // 2,
                        150 + i * (self.button_height + self.button_margin),
                        self.button_width,
                        self.button_height
                    )
                    self.draw_button(button, button_rect)
                
                # Draw settings and exit buttons
                self.draw_settings_button()
                self.draw_exit_button()
            else:
                # Draw settings menu
                self.settings_menu.draw(self.screen)
            
            pygame.display.flip()
            clock.tick(60)
            
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    launcher = ArcadeGameLauncher()
    launcher.run()
