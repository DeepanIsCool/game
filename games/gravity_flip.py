import pygame
import random
import math
from typing import List, Dict
import os

class ParticleSystem:
    def __init__(self):
        self.particles: List[Dict] = []
        
    def create_burst(self, x: int, y: int, direction: int, color: tuple):
        for _ in range(20):
            angle = random.uniform(-math.pi/4, math.pi/4)
            if direction < 0:  # Flipping upward
                angle += math.pi
            speed = random.uniform(2, 5)
            self.particles.append({
                'x': x,
                'y': y,
                'vx': math.cos(angle) * speed,
                'vy': math.sin(angle) * speed,
                'life': 1.0,
                'color': color
            })
            
    def update(self):
        for particle in self.particles[:]:
            particle['x'] += particle['vx']
            particle['y'] += particle['vy']
            particle['life'] -= 0.02
            if particle['life'] <= 0:
                self.particles.remove(particle)
                
    def draw(self, screen):
        for particle in self.particles:
            alpha = int(255 * particle['life'])
            color = (*particle['color'][:3], alpha)
            pos = (int(particle['x']), int(particle['y']))
            size = int(5 * particle['life'])
            
            particle_surface = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            pygame.draw.circle(particle_surface, color, (size, size), size)
            screen.blit(particle_surface, 
                       (pos[0] - size, pos[1] - size))

class Background:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.layers = [
            {
                'image': self.create_star_layer(0.2),
                'scroll': 0,
                'speed': 0.5
            },
            {
                'image': self.create_star_layer(0.3),
                'scroll': 0,
                'speed': 1.0
            },
            {
                'image': self.create_grid_layer(),
                'scroll': 0,
                'speed': 2.0
            }
        ]
        
    def create_star_layer(self, density: float) -> pygame.Surface:
        surface = pygame.Surface((self.width * 2, self.height), pygame.SRCALPHA)
        num_stars = int(self.width * self.height * density)
        for _ in range(num_stars):
            x = random.randint(0, surface.get_width())
            y = random.randint(0, surface.get_height())
            brightness = random.randint(100, 255)
            size = random.randint(1, 3)
            pygame.draw.circle(surface, (brightness, brightness, brightness), 
                             (x, y), size)
        return surface
        
    def create_grid_layer(self) -> pygame.Surface:
        surface = pygame.Surface((self.width * 2, self.height), pygame.SRCALPHA)
        grid_size = 40
        for x in range(0, surface.get_width(), grid_size):
            pygame.draw.line(surface, (0, 255, 255, 30), 
                           (x, 0), (x, self.height))
        for y in range(0, surface.get_height(), grid_size):
            pygame.draw.line(surface, (0, 255, 255, 30), 
                           (0, y), (surface.get_width(), y))
        return surface
        
    def update(self, speed: float):
        for layer in self.layers:
            layer['scroll'] = (layer['scroll'] + speed * layer['speed']) % self.width
            
    def draw(self, screen):
        for layer in self.layers:
            screen.blit(layer['image'], (-layer['scroll'], 0))
            screen.blit(layer['image'], 
                       (self.width - layer['scroll'], 0))

class GravityFlipRunner:
    def __init__(self):
        self.WINDOW_SIZE = (800, 600)
        self.FPS = 60
        
        # Colors
        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)
        self.NEON_YELLOW = (255, 255, 0)
        self.NEON_BLUE = (0, 255, 255)
        self.NEON_GREEN = (0, 255, 0)
        
        # Game objects
        self.player_size = 30
        self.obstacle_width = 50
        self.obstacle_gap = 200
        self.gravity = 0.8
        self.jump_speed = -15
        
        # Initialize systems
        self.particle_system = ParticleSystem()
        self.background = None  # Will be initialized in reset_game
        
        # Trail effect
        self.trail: List[Dict] = []
        self.trail_length = 10
        
        # Game states
        self.STATE_MENU = 'menu'
        self.STATE_PLAYING = 'playing'
        self.STATE_PAUSED = 'paused'
        self.STATE_GAME_OVER = 'game_over'
        
        # Load fonts
        self.title_font = pygame.font.Font(None, 74)
        self.menu_font = pygame.font.Font(None, 36)
        self.score_font = pygame.font.Font(None, 48)
        
        # Load high score
        self.high_score = self.load_high_score()
        
    def load_high_score(self) -> int:
        try:
            with open('high_score.txt', 'r') as f:
                return int(f.read())
        except:
            return 0
            
    def save_high_score(self):
        with open('high_score.txt', 'w') as f:
            f.write(str(self.high_score))
            
    def reset_game(self):
        self.player_pos = pygame.Vector2(100, self.WINDOW_SIZE[1] // 2)
        self.player_velocity = 0
        self.gravity_flip = False
        self.score = 0
        self.game_speed = 5
        self.obstacles = []
        self.spawn_initial_obstacles()
        self.game_state = self.STATE_MENU
        self.background = Background(self.WINDOW_SIZE[0], self.WINDOW_SIZE[1])
        self.show_controls = True
        self.controls_timer = 5 * self.FPS  # 5 seconds
        self.screen_shake = 0
        
    def spawn_initial_obstacles(self):
        for i in range(3):
            x = self.WINDOW_SIZE[0] + i * 300
            self.spawn_obstacle(x)
            
    def spawn_obstacle(self, x: float):
        height = random.randint(100, 300)
        self.obstacles.append({
            'x': x,
            'height': height,
            'passed': False,
            'glow': 0,
            'offset': random.uniform(-2, 2)  # For wiggle effect
        })
        
    def update_trail(self):
        self.trail.insert(0, {
            'pos': self.player_pos.copy(),
            'alpha': 255
        })
        if len(self.trail) > self.trail_length:
            self.trail.pop()
            
        for trail in self.trail:
            trail['alpha'] = max(0, trail['alpha'] - 10)
            
    def draw_trail(self, screen):
        for i, trail in enumerate(self.trail):
            alpha = trail['alpha']
            size = self.player_size * (1 - i/self.trail_length)
            trail_surface = pygame.Surface((size, size), pygame.SRCALPHA)
            pygame.draw.circle(trail_surface, 
                             (*self.NEON_YELLOW[:3], alpha),
                             (size/2, size/2), size/2)
            screen.blit(trail_surface, 
                       (trail['pos'].x - size/2, trail['pos'].y - size/2))
            
    def draw_menu(self, screen):
        # Draw title
        title = self.title_font.render("GRAVITY FLIP RUNNER", True, self.NEON_BLUE)
        title_rect = title.get_rect(center=(self.WINDOW_SIZE[0]//2, 150))
        screen.blit(title, title_rect)
        
        # Draw blinking "Press SPACE to Start"
        if (pygame.time.get_ticks() // 500) % 2:
            start_text = self.menu_font.render("Press SPACE to Start", 
                                             True, self.WHITE)
            start_rect = start_text.get_rect(
                center=(self.WINDOW_SIZE[0]//2, 300))
            screen.blit(start_text, start_rect)
            
        # Draw controls
        controls_text = self.menu_font.render("Controls: SPACE to Flip Gravity", 
                                            True, self.WHITE)
        controls_rect = controls_text.get_rect(
            center=(self.WINDOW_SIZE[0]//2, 400))
        screen.blit(controls_text, controls_rect)
        
        # Draw goal
        goal_text = self.menu_font.render("Goal: Survive as long as you can!", 
                                        True, self.WHITE)
        goal_rect = goal_text.get_rect(center=(self.WINDOW_SIZE[0]//2, 450))
        screen.blit(goal_text, goal_rect)
        
        # Draw high score
        high_score_text = self.menu_font.render(
            f"High Score: {self.high_score}", True, self.NEON_GREEN)
        high_score_rect = high_score_text.get_rect(
            center=(self.WINDOW_SIZE[0]//2, 500))
        screen.blit(high_score_text, high_score_rect)
        
    def draw_game_over(self, screen):
        # Draw "Game Over"
        game_over = self.title_font.render("GAME OVER", True, self.NEON_BLUE)
        game_over_rect = game_over.get_rect(
            center=(self.WINDOW_SIZE[0]//2, 200))
        screen.blit(game_over, game_over_rect)
        
        # Draw score
        score_text = self.score_font.render(f"Score: {self.score}", 
                                          True, self.WHITE)
        score_rect = score_text.get_rect(center=(self.WINDOW_SIZE[0]//2, 300))
        screen.blit(score_text, score_rect)
        
        # Draw high score
        high_score_text = self.score_font.render(
            f"High Score: {self.high_score}", True, self.NEON_GREEN)
        high_score_rect = high_score_text.get_rect(
            center=(self.WINDOW_SIZE[0]//2, 350))
        screen.blit(high_score_text, high_score_rect)
        
        # Draw restart instructions
        if (pygame.time.get_ticks() // 500) % 2:
            restart_text = self.menu_font.render(
                "Press R to Retry or ESC to Exit", True, self.WHITE)
            restart_rect = restart_text.get_rect(
                center=(self.WINDOW_SIZE[0]//2, 450))
            screen.blit(restart_text, restart_rect)
            
    def draw_pause_screen(self, screen):
        # Draw semi-transparent overlay
        overlay = pygame.Surface(self.WINDOW_SIZE, pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        screen.blit(overlay, (0, 0))
        
        # Draw "PAUSED"
        pause_text = self.title_font.render("PAUSED", True, self.WHITE)
        pause_rect = pause_text.get_rect(center=(self.WINDOW_SIZE[0]//2, 
                                               self.WINDOW_SIZE[1]//2))
        screen.blit(pause_text, pause_rect)
        
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
                    elif event.key == pygame.K_SPACE:
                        if self.game_state == self.STATE_MENU:
                            self.game_state = self.STATE_PLAYING
                        elif self.game_state == self.STATE_PLAYING:
                            self.gravity_flip = not self.gravity_flip
                            self.screen_shake = 10
                            self.particle_system.create_burst(
                                self.player_pos.x, self.player_pos.y,
                                -1 if self.gravity_flip else 1,
                                self.NEON_YELLOW
                            )
                    elif event.key == pygame.K_p:
                        if self.game_state == self.STATE_PLAYING:
                            self.game_state = self.STATE_PAUSED
                        elif self.game_state == self.STATE_PAUSED:
                            self.game_state = self.STATE_PLAYING
                    elif event.key == pygame.K_r and \
                         self.game_state == self.STATE_GAME_OVER:
                        self.reset_game()
                        self.game_state = self.STATE_PLAYING
            
            if self.game_state == self.STATE_PLAYING:
                # Update game logic
                gravity_direction = -1 if self.gravity_flip else 1
                self.player_velocity += self.gravity * gravity_direction
                self.player_pos.y += self.player_velocity
                
                # Update background
                self.background.update(self.game_speed)
                
                # Update particle system
                self.particle_system.update()
                
                # Update trail
                self.update_trail()
                
                # Keep player in bounds
                if self.player_pos.y < 0:
                    self.player_pos.y = 0
                    self.player_velocity = 0
                elif self.player_pos.y > self.WINDOW_SIZE[1] - self.player_size:
                    self.player_pos.y = self.WINDOW_SIZE[1] - self.player_size
                    self.player_velocity = 0
                    
                # Update obstacles
                for obstacle in self.obstacles[:]:
                    obstacle['x'] -= self.game_speed
                    # Update obstacle glow
                    obstacle['glow'] = (obstacle['glow'] + 0.05) % (2 * math.pi)
                    # Update obstacle wiggle
                    obstacle['offset'] = math.sin(pygame.time.get_ticks() * 0.01) * 2
                    
                    if not obstacle['passed'] and \
                       obstacle['x'] < self.player_pos.x:
                        obstacle['passed'] = True
                        self.score += 1
                        # Increase game speed every 15 seconds
                        if self.score % 15 == 0:
                            self.game_speed += 0.5
                            
                    if obstacle['x'] < -self.obstacle_width:
                        self.obstacles.remove(obstacle)
                        self.spawn_obstacle(self.WINDOW_SIZE[0])
                        
                # Check collisions
                player_rect = pygame.Rect(self.player_pos.x, self.player_pos.y,
                                        self.player_size, self.player_size)
                for obstacle in self.obstacles:
                    top_obstacle = pygame.Rect(
                        obstacle['x'], 0,
                        self.obstacle_width, obstacle['height']
                    )
                    bottom_obstacle = pygame.Rect(
                        obstacle['x'],
                        obstacle['height'] + self.obstacle_gap,
                        self.obstacle_width,
                        self.WINDOW_SIZE[1]
                    )
                    
                    if player_rect.colliderect(top_obstacle) or \
                       player_rect.colliderect(bottom_obstacle):
                        if self.score > self.high_score:
                            self.high_score = self.score
                            self.save_high_score()
                        self.game_state = self.STATE_GAME_OVER
                        
                # Update controls timer
                if self.show_controls:
                    self.controls_timer -= 1
                    if self.controls_timer <= 0:
                        self.show_controls = False
                        
                # Update screen shake
                if self.screen_shake > 0:
                    self.screen_shake -= 1
            
            # Draw everything
            screen.fill(self.BLACK)
            
            # Draw background
            self.background.draw(screen)
            
            if self.game_state == self.STATE_MENU:
                self.draw_menu(screen)
            else:
                # Draw obstacles with glow effect
                for obstacle in self.obstacles:
                    glow_intensity = (math.sin(obstacle['glow']) + 1) / 2
                    glow_color = (0, 
                                int(255 * (0.7 + 0.3 * glow_intensity)), 
                                int(255 * (0.7 + 0.3 * glow_intensity)))
                    
                    # Draw top obstacle
                    pygame.draw.rect(screen, glow_color,
                                   (obstacle['x'], 
                                    0 + obstacle['offset'],
                                    self.obstacle_width, 
                                    obstacle['height']))
                    
                    # Draw bottom obstacle
                    pygame.draw.rect(screen, glow_color,
                                   (obstacle['x'],
                                    obstacle['height'] + self.obstacle_gap + obstacle['offset'],
                                    self.obstacle_width,
                                    self.WINDOW_SIZE[1]))
                    
                    # Draw glow effect
                    for i in range(3):
                        glow_alpha = int(128 * (1 - i/3) * glow_intensity)
                        glow_surface = pygame.Surface(
                            (self.obstacle_width + i*4, self.WINDOW_SIZE[1]), 
                            pygame.SRCALPHA
                        )
                        pygame.draw.rect(glow_surface, 
                                       (*glow_color, glow_alpha),
                                       (0, 0, 
                                        self.obstacle_width + i*4, 
                                        obstacle['height']))
                        pygame.draw.rect(glow_surface, 
                                       (*glow_color, glow_alpha),
                                       (0, 
                                        obstacle['height'] + self.obstacle_gap,
                                        self.obstacle_width + i*4,
                                        self.WINDOW_SIZE[1]))
                        screen.blit(glow_surface, 
                                  (obstacle['x'] - i*2, 0))
                
                # Apply screen shake
                shake_offset = random.randint(-self.screen_shake, 
                                           self.screen_shake)
                
                # Draw player trail
                self.draw_trail(screen)
                
                # Draw player with glow effect
                player_surface = pygame.Surface(
                    (self.player_size * 2, self.player_size * 2), 
                    pygame.SRCALPHA
                )
                pygame.draw.circle(player_surface, 
                                 (*self.NEON_YELLOW, 128),
                                 (self.player_size, self.player_size),
                                 self.player_size)
                pygame.draw.circle(player_surface, 
                                 self.NEON_YELLOW,
                                 (self.player_size, self.player_size),
                                 self.player_size - 2)
                screen.blit(player_surface,
                          (self.player_pos.x - self.player_size/2 + shake_offset,
                           self.player_pos.y - self.player_size/2))
                
                # Draw particles
                self.particle_system.draw(screen)
                
                # Draw score
                score_text = self.score_font.render(f"Score: {self.score}", 
                                                  True, self.NEON_GREEN)
                screen.blit(score_text, (10, 10))
                
                # Draw controls hint (fades out after 5 seconds)
                if self.show_controls:
                    alpha = int(255 * (self.controls_timer / (5 * self.FPS)))
                    controls_surface = pygame.Surface(
                        (300, 40), pygame.SRCALPHA)
                    controls_text = self.menu_font.render(
                        "Press SPACE to Flip", True, 
                        (*self.WHITE[:3], alpha))
                    controls_rect = controls_text.get_rect(
                        center=(150, 20))
                    controls_surface.blit(controls_text, controls_rect)
                    screen.blit(controls_surface,
                              (self.WINDOW_SIZE[0]//2 - 150,
                               self.WINDOW_SIZE[1] - 60))
                
                # Draw pause screen if paused
                if self.game_state == self.STATE_PAUSED:
                    self.draw_pause_screen(screen)
                elif self.game_state == self.STATE_GAME_OVER:
                    self.draw_game_over(screen)
            
            pygame.display.flip()
            clock.tick(self.FPS)
            
        return True  # Return to main menu
