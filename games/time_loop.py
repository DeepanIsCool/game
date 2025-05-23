import pygame
import random
import math
from typing import List, Dict, Tuple
import os

class Notification:
    def __init__(self, text: str, color: Tuple[int, int, int], duration: int = 120):
        self.text = text
        self.color = color
        self.duration = duration
        self.alpha = 0
        self.fade_in = True
        
    def update(self) -> bool:
        if self.fade_in:
            self.alpha = min(255, self.alpha + 10)
            if self.alpha == 255:
                self.fade_in = False
        else:
            self.duration -= 1
            if self.duration < 60:
                self.alpha = max(0, self.alpha - 5)
                
        return self.alpha > 0

class LoopEffect:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.progress = 0
        self.active = False
        self.surface = pygame.Surface((width, height))
        self.noise_surface = pygame.Surface((width, height))
        
    def start(self):
        self.active = True
        self.progress = 0
        
    def update(self) -> bool:
        if not self.active:
            return False
            
        self.progress += 0.02
        if self.progress >= 1:
            self.active = False
            return False
            
        # Create glitch effect
        self.noise_surface.fill((0, 0, 0))
        for _ in range(100):
            x = random.randint(0, self.width - 1)
            y = random.randint(0, self.height - 1)
            width = random.randint(10, 100)
            height = random.randint(2, 10)
            alpha = random.randint(50, 150)
            color = (random.randint(0, 255),
                    random.randint(0, 255),
                    random.randint(0, 255),
                    alpha)
            pygame.draw.rect(self.noise_surface, color,
                           (x, y, width, height))
            
        return True
        
    def draw(self, screen):
        if not self.active:
            return
            
        alpha = int(255 * (0.5 - abs(0.5 - self.progress)))
        self.noise_surface.set_alpha(alpha)
        screen.blit(self.noise_surface, (0, 0))

class TimeLoopDefender:
    def __init__(self):
        self.WINDOW_SIZE = (800, 600)
        self.FPS = 60
        
        # Colors
        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)
        self.RED = (255, 50, 50)
        self.BLUE = (50, 50, 255)
        self.CYAN = (0, 255, 255)
        
        # Game states
        self.STATE_MENU = 'menu'
        self.STATE_PLAYING = 'playing'
        self.STATE_PAUSED = 'paused'
        self.STATE_GAME_OVER = 'game_over'
        
        # Load fonts
        self.title_font = pygame.font.Font(None, 74)
        self.hud_font = pygame.font.Font(None, 36)
        self.alert_font = pygame.font.Font(None, 48)
        
        # Initialize effects
        self.loop_effect = LoopEffect(self.WINDOW_SIZE[0], self.WINDOW_SIZE[1])
        
        # Initialize game
        self.reset_game()
        
    def reset_game(self):
        self.game_state = self.STATE_MENU
        self.base_pos = (self.WINDOW_SIZE[0] // 2, self.WINDOW_SIZE[1] // 2)
        self.base_health = 100
        self.score = 0
        self.current_round = 0
        self.max_rounds = 3
        self.round_timer = 30 * self.FPS  # 30 seconds per round
        self.enemies = []
        self.bullets = []
        self.past_actions = []  # Actions from previous rounds
        self.current_actions = []  # Actions in current round
        self.notifications = []
        self.stats = {
            'damage_dealt': 0,
            'enemies_defeated': 0,
            'shots_fired': 0
        }
        
    def add_notification(self, text: str, color: Tuple[int, int, int]):
        self.notifications.append(Notification(text, color))
        
    def update_notifications(self):
        self.notifications = [n for n in self.notifications if n.update()]
        
    def draw_notifications(self, screen):
        for i, notification in enumerate(self.notifications):
            text_surface = self.alert_font.render(notification.text, True,
                                                notification.color)
            text_surface.set_alpha(notification.alpha)
            text_rect = text_surface.get_rect(
                center=(self.WINDOW_SIZE[0]//2,
                       self.WINDOW_SIZE[1]//2 - 100 + i*60))
            screen.blit(text_surface, text_rect)
            
    def draw_health_bar(self, screen):
        # Draw health bar background
        bar_width = 200
        bar_height = 20
        x = 10
        y = 10
        pygame.draw.rect(screen, (50, 50, 50),
                        (x, y, bar_width, bar_height))
        
        # Draw health bar
        health_width = int(bar_width * (self.base_health / 100))
        if health_width > 0:
            health_color = (
                min(255, 510 * (1 - self.base_health/100)),  # Red
                min(255, 510 * (self.base_health/100)),      # Green
                0                                            # Blue
            )
            pygame.draw.rect(screen, health_color,
                           (x, y, health_width, bar_height))
            
        # Draw glow effect
        glow_surface = pygame.Surface((bar_width + 20, bar_height + 20),
                                    pygame.SRCALPHA)
        glow_alpha = int(127 + 127 * math.sin(pygame.time.get_ticks() * 0.005))
        pygame.draw.rect(glow_surface,
                        (*health_color, glow_alpha),
                        (0, 0, bar_width + 20, bar_height + 20),
                        5)
        screen.blit(glow_surface, (x - 10, y - 10))
        
        # Draw health text
        health_text = self.hud_font.render(f"HEALTH: {self.base_health}",
                                         True, self.WHITE)
        screen.blit(health_text, (x + bar_width + 20, y))
        
    def draw_score_panel(self, screen):
        # Draw score background with gradient
        panel_width = 200
        panel_height = 30
        x = 10
        y = 40
        
        gradient_surface = pygame.Surface((panel_width, panel_height))
        for i in range(panel_height):
            progress = i / panel_height
            color = [int(c * (0.5 + 0.5 * progress)) for c in self.BLUE]
            pygame.draw.line(gradient_surface, color,
                           (0, i), (panel_width, i))
            
        screen.blit(gradient_surface, (x, y))
        
        # Draw score text
        score_text = self.hud_font.render(f"SCORE: {self.score}",
                                        True, self.WHITE)
        screen.blit(score_text, (x + 10, y + 5))
        
    def draw_timer(self, screen):
        time_left = self.round_timer // self.FPS
        color = self.RED if time_left <= 10 else self.WHITE
        
        # Draw digital countdown
        timer_text = self.hud_font.render(
            f"ROUND: {self.current_round + 1}/{self.max_rounds} | "
            f"TIME: {time_left}s",
            True, color)
        screen.blit(timer_text, (10, 80))
        
        # Draw circular timer
        center = (self.WINDOW_SIZE[0] - 50, 50)
        radius = 30
        progress = self.round_timer / (30 * self.FPS)
        
        # Draw background circle
        pygame.draw.circle(screen, (50, 50, 50), center, radius)
        
        # Draw progress arc
        if progress > 0:
            points = [(center[0], center[1])]
            for i in range(0, int(360 * progress) + 1):
                angle = math.radians(i - 90)
                x = center[0] + radius * math.cos(angle)
                y = center[1] + radius * math.sin(angle)
                points.append((x, y))
            points.append(center)
            
            if len(points) > 2:
                pygame.draw.polygon(screen, color, points)
                
    def draw_round_summary(self, screen):
        # Draw semi-transparent overlay
        overlay = pygame.Surface(self.WINDOW_SIZE, pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        screen.blit(overlay, (0, 0))
        
        # Draw terminal-style box
        box_width = 500
        box_height = 300
        x = (self.WINDOW_SIZE[0] - box_width) // 2
        y = (self.WINDOW_SIZE[1] - box_height) // 2
        
        pygame.draw.rect(screen, (0, 50, 0), 
                        (x, y, box_width, box_height))
        pygame.draw.rect(screen, self.CYAN,
                        (x, y, box_width, box_height), 2)
        
        # Draw stats with typing effect
        stats_text = [
            f">>> LOOP {self.current_round} COMPLETE <<<",
            f"",
            f"Damage Dealt: {self.stats['damage_dealt']}",
            f"Enemies Defeated: {self.stats['enemies_defeated']}",
            f"Shots Fired: {self.stats['shots_fired']}",
            f"Loop Efficiency: {self.calculate_efficiency()}%",
            f"",
            f"Press SPACE to continue..."
        ]
        
        for i, text in enumerate(stats_text):
            text_surface = self.hud_font.render(text, True, self.CYAN)
            screen.blit(text_surface, 
                       (x + 20, y + 20 + i * 30))
            
    def calculate_efficiency(self) -> int:
        if self.stats['shots_fired'] == 0:
            return 0
        return int(100 * self.stats['enemies_defeated'] / 
                  max(1, self.stats['shots_fired']))
        
    def draw_pause_menu(self, screen):
        # Draw semi-transparent overlay
        overlay = pygame.Surface(self.WINDOW_SIZE, pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        screen.blit(overlay, (0, 0))
        
        # Draw pause menu
        title = self.title_font.render("PAUSED", True, self.WHITE)
        title_rect = title.get_rect(
            center=(self.WINDOW_SIZE[0]//2, 200))
        screen.blit(title, title_rect)
        
        options = [
            "Resume (P)",
            "Restart Loop (R)",
            "Exit (ESC)"
        ]
        
        for i, option in enumerate(options):
            option_text = self.hud_font.render(option, True, self.WHITE)
            option_rect = option_text.get_rect(
                center=(self.WINDOW_SIZE[0]//2, 300 + i*40))
            screen.blit(option_text, option_rect)
            
    def run(self, screen):
        clock = pygame.time.Clock()
        self.reset_game()
        running = True
        
        while running:
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        if self.game_state == self.STATE_PLAYING:
                            self.game_state = self.STATE_PAUSED
                        else:
                            running = False
                    elif event.key == pygame.K_p:
                        if self.game_state == self.STATE_PLAYING:
                            self.game_state = self.STATE_PAUSED
                        elif self.game_state == self.STATE_PAUSED:
                            self.game_state = self.STATE_PLAYING
                    elif event.key == pygame.K_r:
                        if self.game_state == self.STATE_PAUSED:
                            self.reset_game()
                            self.game_state = self.STATE_PLAYING
                    elif event.key == pygame.K_SPACE:
                        if self.game_state == self.STATE_MENU:
                            self.game_state = self.STATE_PLAYING
                            self.add_notification("Time Loop Initiated",
                                               self.CYAN)
                            
            if self.game_state == self.STATE_PLAYING:
                # Update game logic here
                self.round_timer -= 1
                
                if self.round_timer <= 0:
                    self.current_round += 1
                    if self.current_round >= self.max_rounds:
                        self.game_state = self.STATE_GAME_OVER
                    else:
                        self.round_timer = 30 * self.FPS
                        self.loop_effect.start()
                        self.add_notification("Time Loop Reset",
                                           self.CYAN)
                        
                # Update effects
                self.update_notifications()
                self.loop_effect.update()
                
            # Draw everything
            screen.fill(self.BLACK)
            
            if self.game_state == self.STATE_MENU:
                # Draw menu
                title = self.title_font.render("TIME LOOP DEFENDER",
                                             True, self.WHITE)
                subtitle = self.hud_font.render(
                    "Trapped in a Collapsing Timeline",
                    True, self.CYAN)
                
                title_rect = title.get_rect(
                    center=(self.WINDOW_SIZE[0]//2, 200))
                subtitle_rect = subtitle.get_rect(
                    center=(self.WINDOW_SIZE[0]//2, 270))
                
                screen.blit(title, title_rect)
                screen.blit(subtitle, subtitle_rect)
                
                if (pygame.time.get_ticks() // 500) % 2:
                    start_text = self.hud_font.render(
                        "Press SPACE to Start",
                        True, self.WHITE)
                    start_rect = start_text.get_rect(
                        center=(self.WINDOW_SIZE[0]//2, 400))
                    screen.blit(start_text, start_rect)
                    
            elif self.game_state == self.STATE_PLAYING:
                # Draw game elements here
                
                # Draw HUD
                self.draw_health_bar(screen)
                self.draw_score_panel(screen)
                self.draw_timer(screen)
                
                # Draw notifications
                self.draw_notifications(screen)
                
                # Draw loop effect
                self.loop_effect.draw(screen)
                
            elif self.game_state == self.STATE_PAUSED:
                self.draw_pause_menu(screen)
                
            elif self.game_state == self.STATE_GAME_OVER:
                # Draw game over screen
                game_over = self.title_font.render("GAME OVER",
                                                 True, self.RED)
                game_over_rect = game_over.get_rect(
                    center=(self.WINDOW_SIZE[0]//2, 200))
                screen.blit(game_over, game_over_rect)
                
                score_text = self.hud_font.render(
                    f"Final Score: {self.score}",
                    True, self.WHITE)
                score_rect = score_text.get_rect(
                    center=(self.WINDOW_SIZE[0]//2, 300))
                screen.blit(score_text, score_rect)
                
            pygame.display.flip()
            clock.tick(self.FPS)
            
        return True  # Return to main menu
