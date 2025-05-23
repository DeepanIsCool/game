import pygame
import os

class SettingsMenu:
    def __init__(self, screen_size, audio_manager):
        self.screen_size = screen_size
        self.audio_manager = audio_manager
        
        # Colors
        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)
        self.GRAY = (128, 128, 128)
        self.NEON_BLUE = (0, 255, 255)
        
        # Fonts
        self.title_font = pygame.font.Font(None, 48)
        self.option_font = pygame.font.Font(None, 36)
        
        # Menu dimensions
        self.width = 400
        self.height = 300
        self.x = (screen_size[0] - self.width) // 2
        self.y = (screen_size[1] - self.height) // 2
        
        # Settings options
        self.options = [
            {"text": "Music Volume", "type": "slider", "value": 0.5},
            {"text": "Sound Effects", "type": "slider", "value": 0.7},
            {"text": "Fullscreen", "type": "toggle", "value": False},
            {"text": "Back", "type": "button"}
        ]
        
        self.selected_option = None
        self.dragging = False
        
    def draw(self, screen):
        # Draw semi-transparent background
        overlay = pygame.Surface(self.screen_size, pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        screen.blit(overlay, (0, 0))
        
        # Draw settings panel
        pygame.draw.rect(screen, self.BLACK, 
                        (self.x, self.y, self.width, self.height))
        pygame.draw.rect(screen, self.NEON_BLUE, 
                        (self.x, self.y, self.width, self.height), 2)
        
        # Draw title
        title = self.title_font.render("Settings", True, self.WHITE)
        title_rect = title.get_rect(centerx=self.x + self.width//2, 
                                  y=self.y + 20)
        screen.blit(title, title_rect)
        
        # Draw options
        y_offset = 80
        for i, option in enumerate(self.options):
            option_rect = pygame.Rect(self.x + 20, 
                                    self.y + y_offset, 
                                    self.width - 40, 
                                    40)
            
            # Draw option text
            text = self.option_font.render(option["text"], True, self.WHITE)
            screen.blit(text, (option_rect.x, option_rect.y + 10))
            
            # Draw control based on type
            if option["type"] == "slider":
                # Draw slider background
                slider_rect = pygame.Rect(option_rect.x + 200, 
                                        option_rect.y + 15, 
                                        150, 
                                        10)
                pygame.draw.rect(screen, self.GRAY, slider_rect)
                
                # Draw slider handle
                handle_x = slider_rect.x + (slider_rect.width * option["value"])
                pygame.draw.circle(screen, self.NEON_BLUE, 
                                 (int(handle_x), slider_rect.centery), 8)
                
            elif option["type"] == "toggle":
                toggle_rect = pygame.Rect(option_rect.x + 200, 
                                        option_rect.y + 10, 
                                        40, 
                                        20)
                pygame.draw.rect(screen, 
                               self.NEON_BLUE if option["value"] else self.GRAY, 
                               toggle_rect)
                
                # Draw toggle handle
                handle_x = toggle_rect.right - 15 if option["value"] else toggle_rect.x + 5
                pygame.draw.circle(screen, self.WHITE, 
                                 (handle_x, toggle_rect.centery), 8)
                
            elif option["type"] == "button":
                pygame.draw.rect(screen, self.NEON_BLUE, option_rect, 2)
            
            y_offset += 60
            
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            y_offset = 80
            
            for i, option in enumerate(self.options):
                option_rect = pygame.Rect(self.x + 20, 
                                        self.y + y_offset, 
                                        self.width - 40, 
                                        40)
                
                if option["type"] == "slider":
                    slider_rect = pygame.Rect(option_rect.x + 200, 
                                            option_rect.y + 15, 
                                            150, 
                                            10)
                    if slider_rect.collidepoint(mouse_pos):
                        self.selected_option = i
                        self.dragging = True
                        self.update_slider_value(mouse_pos[0], i)
                        
                elif option["type"] == "toggle":
                    toggle_rect = pygame.Rect(option_rect.x + 200, 
                                            option_rect.y + 10, 
                                            40, 
                                            20)
                    if toggle_rect.collidepoint(mouse_pos):
                        option["value"] = not option["value"]
                        self.apply_setting(i)
                        
                elif option["type"] == "button" and option_rect.collidepoint(mouse_pos):
                    return False  # Close settings
                    
                y_offset += 60
                
        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False
            self.selected_option = None
            
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            if self.selected_option is not None:
                self.update_slider_value(event.pos[0], self.selected_option)
                
        return True
        
    def update_slider_value(self, x, option_index):
        option = self.options[option_index]
        if option["type"] == "slider":
            slider_rect = pygame.Rect(self.x + 220, 
                                    self.y + 80 + (option_index * 60) + 15, 
                                    150, 
                                    10)
            option["value"] = max(0, min(1, 
                                       (x - slider_rect.x) / slider_rect.width))
            self.apply_setting(option_index)
            
    def apply_setting(self, option_index):
        option = self.options[option_index]
        if option["text"] == "Music Volume":
            self.audio_manager.set_volume(option["value"])
        elif option["text"] == "Sound Effects":
            self.audio_manager.set_sound_volume(option["value"])
        elif option["text"] == "Fullscreen":
            pygame.display.toggle_fullscreen()
