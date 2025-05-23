import pygame
import random
import math
from typing import List, Dict, Tuple
import os

class Target:
    def __init__(self, x: float, y: float, color: Tuple[int, int, int], 
                 size: int = 40, level: int = 1):
        self.x = x
        self.y = y
        self.color = color
        self.size = size
        self.original_size = size
        self.hit = False
        self.hit_animation = 0
        self.rotation = 0
        self.pulse = 0
        self.level = level
        
        # Movement patterns based on level
        if level >= 2:
            self.vx = random.choice([-2, 2])
            self.vy = random.uniform(1.5, 3)  # Ensure downward movement
        else:
            self.vx = 0
            self.vy = random.uniform(1, 2.5)  # Consistent downward movement
            
        # Color changing behavior (level 3+)
        self.color_change_timer = 300 if level >= 3 else 0
        self.original_color = color
        
    def update(self, width: int, height: int):
        # Update position
        self.x += self.vx
        self.y += self.vy
        
        # Bounce off walls (only horizontally)
        if self.x < 0:
            self.x = 0
            self.vx = abs(self.vx)  # Move right
        elif self.x > width:
            self.x = width
            self.vx = -abs(self.vx)  # Move left
            
        # Update rotation and pulse
        self.rotation += 2
        self.pulse = (math.sin(pygame.time.get_ticks() * 0.005) + 1) * 0.1
        
        # Update hit animation
        if self.hit:
            self.hit_animation += 0.2
            self.size = self.original_size * (1 + math.sin(self.hit_animation))
            if self.hit_animation >= math.pi:
                return True
                
        # Update color changing (level 3+)
        if self.color_change_timer > 0:
            self.color_change_timer -= 1
            if self.color_change_timer == 0:
                available_colors = [
                    (255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0)
                ]
                available_colors.remove(self.original_color)
                self.color = random.choice(available_colors)
                
        return False
        
    def draw(self, screen):
        # Create surface for the target
        target_surface = pygame.Surface((self.size * 2, self.size * 2), 
                                      pygame.SRCALPHA)
        
        # Draw glowing effect
        glow_size = int(self.size * (1 + self.pulse))
        for i in range(3):
            alpha = 100 - i * 30
            pygame.draw.rect(target_surface,
                           (*self.color, alpha),
                           (self.size - glow_size//2 + i*2,
                            self.size - glow_size//2 + i*2,
                            glow_size - i*4,
                            glow_size - i*4))
            
        # Draw main square
        pygame.draw.rect(target_surface,
                        self.color,
                        (self.size - self.size//2,
                         self.size - self.size//2,
                         self.size,
                         self.size))
        
        # Rotate and draw
        rotated_surface = pygame.transform.rotate(target_surface, self.rotation)
        screen.blit(rotated_surface,
                   (self.x - rotated_surface.get_width()//2,
                    self.y - rotated_surface.get_height()//2))

class ParticleSystem:
    def __init__(self):
        self.particles: List[Dict] = []
        
    def create_hit_burst(self, x: int, y: int, color: Tuple[int, int, int]):
        for _ in range(20):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(2, 5)
            self.particles.append({
                'x': x,
                'y': y,
                'vx': math.cos(angle) * speed,
                'vy': math.sin(angle) * speed,
                'life': 1.0,
                'color': color,
                'size': random.uniform(2, 4)
            })
            
    def create_background_particle(self, width: int, height: int):
        color = random.choice([
            (255, 0, 0), (0, 255, 0), (0, 0, 255),
            (255, 255, 0), (0, 255, 255), (255, 0, 255)
        ])
        self.particles.append({
            'x': random.randint(0, width),
            'y': height + 10,
            'vx': random.uniform(-0.5, 0.5),
            'vy': random.uniform(-1, -0.5),
            'life': 1.0,
            'color': color,
            'size': random.uniform(3, 6)
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
            size = int(particle['size'] * particle['life'])
            
            particle_surface = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            pygame.draw.circle(particle_surface, color, 
                             (size, size), size)
            screen.blit(particle_surface, 
                       (pos[0] - size, pos[1] - size))

class Projectile:
    def __init__(self, x: float, y: float, color: Tuple[int, int, int]):
        self.x = x
        self.y = y
        self.color = color
        self.speed = -10
        self.trail: List[Dict] = []
        
    def update(self):
        self.y += self.speed
        
        # Update trail
        self.trail.insert(0, {'x': self.x, 'y': self.y, 'alpha': 255})
        if len(self.trail) > 10:
            self.trail.pop()
            
        for trail in self.trail:
            trail['alpha'] = max(0, trail['alpha'] - 25)
            
    def draw(self, screen):
        # Draw trail
        for trail in self.trail:
            alpha = trail['alpha']
            trail_surface = pygame.Surface((6, 6), pygame.SRCALPHA)
            pygame.draw.circle(trail_surface,
                             (*self.color, alpha),
                             (3, 3), 3)
            screen.blit(trail_surface,
                       (trail['x'] - 3, trail['y'] - 3))
        
        # Draw projectile
        projectile_surface = pygame.Surface((8, 8), pygame.SRCALPHA)
        pygame.draw.circle(projectile_surface,
                          self.color,
                          (4, 4), 4)
        screen.blit(projectile_surface,
                   (self.x - 4, self.y - 4))

class ColorMatchShooter:
    def __init__(self):
        self.WINDOW_SIZE = (800, 600)
        self.FPS = 60
        
        # Colors
        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)
        self.COLORS = [
            (255, 0, 0),    # Red
            (0, 255, 0),    # Green
            (0, 0, 255),    # Blue
            (255, 255, 0)   # Yellow
        ]
        
        # Game objects
        self.player_width = 60
        self.player_height = 40
        self.player_x = self.WINDOW_SIZE[0] // 2
        self.current_color_index = 0
        
        # Initialize systems
        self.particle_system = ParticleSystem()
        
        # Game states
        self.STATE_MENU = 'menu'
        self.STATE_PLAYING = 'playing'
        self.STATE_GAME_OVER = 'game_over'
        
        # Load fonts
        self.title_font = pygame.font.Font(None, 74)
        self.menu_font = pygame.font.Font(None, 36)
        self.hud_font = pygame.font.Font(None, 24)
        
        # Game variables
        self.reset_game()
        
    def reset_game(self):
        self.game_state = self.STATE_MENU
        self.score = 0
        self.combo = 0
        self.high_score = self.load_high_score()
        self.targets: List[Target] = []
        self.projectiles: List[Projectile] = []
        self.spawn_timer = 0
        self.level = 1
        self.shots_fired = 0
        self.shots_hit = 0
        self.combo_text = None
        self.combo_timer = 0
        self.power_ups: List[Dict] = []
        self.rainbow_shot = False
        self.rainbow_timer = 0
        self.slow_motion = False
        self.slow_timer = 0
        
    def load_high_score(self) -> int:
        try:
            with open('color_match_high_score.txt', 'r') as f:
                return int(f.read())
        except:
            return 0
            
    def save_high_score(self):
        with open('color_match_high_score.txt', 'w') as f:
            f.write(str(self.high_score))
            
    def spawn_target(self):
        x = random.randint(50, self.WINDOW_SIZE[0] - 50)
        color = random.choice(self.COLORS)
        self.targets.append(Target(x, -20, color, level=self.level))
        
    def spawn_power_up(self):
        if random.random() < 0.05:  # 5% chance
            x = random.randint(50, self.WINDOW_SIZE[0] - 50)
            power_up_type = random.choice(['rainbow', 'slow', 'multiplier'])
            self.power_ups.append({
                'x': x,
                'y': -20,
                'type': power_up_type,
                'vy': 2
            })
            
    def update_power_ups(self):
        for power_up in self.power_ups[:]:
            power_up['y'] += power_up['vy']
            
            # Check collision with player
            if (abs(power_up['x'] - self.player_x) < 30 and
                abs(power_up['y'] - (self.WINDOW_SIZE[1] - 50)) < 30):
                if power_up['type'] == 'rainbow':
                    self.rainbow_shot = True
                    self.rainbow_timer = 300  # 5 seconds
                elif power_up['type'] == 'slow':
                    self.slow_motion = True
                    self.slow_timer = 300
                elif power_up['type'] == 'multiplier':
                    self.score *= 2
                self.power_ups.remove(power_up)
            elif power_up['y'] > self.WINDOW_SIZE[1]:
                self.power_ups.remove(power_up)
                
    def draw_power_ups(self, screen):
        for power_up in self.power_ups:
            color = (255, 255, 255)
            if power_up['type'] == 'rainbow':
                color = (random.randint(0, 255),
                        random.randint(0, 255),
                        random.randint(0, 255))
            elif power_up['type'] == 'slow':
                color = (0, 255, 255)
            elif power_up['type'] == 'multiplier':
                color = (255, 255, 0)
                
            pygame.draw.circle(screen, color,
                             (int(power_up['x']), int(power_up['y'])), 15)
            
    def draw_menu(self, screen):
        # Draw title
        title = self.title_font.render("COLOR MATCH SHOOTER", True, self.WHITE)
        title_rect = title.get_rect(center=(self.WINDOW_SIZE[0]//2, 150))
        screen.blit(title, title_rect)
        
        # Draw controls
        controls = [
            "Controls:",
            "← / → : Move",
            "Space : Shoot",
            "1-4  : Change Color"
        ]
        
        for i, text in enumerate(controls):
            control_text = self.menu_font.render(text, True, self.WHITE)
            control_rect = control_text.get_rect(
                center=(self.WINDOW_SIZE[0]//2, 250 + i*40))
            screen.blit(control_text, control_rect)
            
        # Draw "Press Space to Start"
        if (pygame.time.get_ticks() // 500) % 2:
            start_text = self.menu_font.render("Press SPACE to Start",
                                             True, self.WHITE)
            start_rect = start_text.get_rect(
                center=(self.WINDOW_SIZE[0]//2, 450))
            screen.blit(start_text, start_rect)
            
        # Draw high score
        high_score_text = self.menu_font.render(
            f"High Score: {self.high_score}", True, self.WHITE)
        high_score_rect = high_score_text.get_rect(
            center=(self.WINDOW_SIZE[0]//2, 500))
        screen.blit(high_score_text, high_score_rect)
        
    def draw_game_over(self, screen):
        # Draw "Game Over"
        game_over = self.title_font.render("GAME OVER", True, self.WHITE)
        game_over_rect = game_over.get_rect(
            center=(self.WINDOW_SIZE[0]//2, 150))
        screen.blit(game_over, game_over_rect)
        
        # Draw score
        score_text = self.menu_font.render(f"Score: {self.score}",
                                         True, self.WHITE)
        score_rect = score_text.get_rect(
            center=(self.WINDOW_SIZE[0]//2, 250))
        screen.blit(score_text, score_rect)
        
        # Draw high score
        high_score_text = self.menu_font.render(
            f"High Score: {self.high_score}", True, self.WHITE)
        high_score_rect = high_score_text.get_rect(
            center=(self.WINDOW_SIZE[0]//2, 300))
        screen.blit(high_score_text, high_score_rect)
        
        # Draw accuracy
        accuracy = (self.shots_hit / max(1, self.shots_fired)) * 100
        accuracy_text = self.menu_font.render(
            f"Accuracy: {accuracy:.1f}%", True, self.WHITE)
        accuracy_rect = accuracy_text.get_rect(
            center=(self.WINDOW_SIZE[0]//2, 350))
        screen.blit(accuracy_text, accuracy_rect)
        
        # Draw restart instructions
        if (pygame.time.get_ticks() // 500) % 2:
            restart_text = self.menu_font.render(
                "Press R to Retry or ESC to Exit", True, self.WHITE)
            restart_rect = restart_text.get_rect(
                center=(self.WINDOW_SIZE[0]//2, 450))
            screen.blit(restart_text, restart_rect)
            
    def draw_hud(self, screen):
        # Draw score
        score_text = self.hud_font.render(f"Score: {self.score}",
                                        True, self.WHITE)
        screen.blit(score_text, (10, 10))
        
        # Draw combo
        if self.combo > 1:
            combo_text = self.hud_font.render(f"Combo x{self.combo}",
                                            True, self.WHITE)
            screen.blit(combo_text, (10, 40))
            
        # Draw current color indicator
        pygame.draw.rect(screen, self.COLORS[self.current_color_index],
                        (self.WINDOW_SIZE[0] - 50, 10, 40, 40))
        
        # Draw color bar
        bar_width = 50
        for i, color in enumerate(self.COLORS):
            pygame.draw.rect(screen, color,
                           (10 + i * (bar_width + 5),
                            self.WINDOW_SIZE[1] - 30,
                            bar_width, 20))
            if i == self.current_color_index:
                pygame.draw.rect(screen, self.WHITE,
                               (10 + i * (bar_width + 5),
                                self.WINDOW_SIZE[1] - 30,
                                bar_width, 20), 2)
                
        # Draw power-up status
        if self.rainbow_shot:
            rainbow_text = self.hud_font.render(
                f"Rainbow Shot: {self.rainbow_timer//60}s",
                True, (random.randint(0, 255),
                      random.randint(0, 255),
                      random.randint(0, 255)))
            screen.blit(rainbow_text,
                       (self.WINDOW_SIZE[0] - 200, 60))
            
        if self.slow_motion:
            slow_text = self.hud_font.render(
                f"Slow Motion: {self.slow_timer//60}s",
                True, (0, 255, 255))
            screen.blit(slow_text,
                       (self.WINDOW_SIZE[0] - 200, 90))
            
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
                        running = False
                    elif event.key == pygame.K_SPACE:
                        if self.game_state == self.STATE_MENU:
                            self.game_state = self.STATE_PLAYING
                        elif self.game_state == self.STATE_PLAYING:
                            # Shoot projectile
                            self.projectiles.append(
                                Projectile(self.player_x,
                                         self.WINDOW_SIZE[1] - 60,
                                         self.COLORS[self.current_color_index])
                            )
                            self.shots_fired += 1
                    elif event.key == pygame.K_r and \
                         self.game_state == self.STATE_GAME_OVER:
                        self.reset_game()
                        self.game_state = self.STATE_PLAYING
                    elif self.game_state == self.STATE_PLAYING:
                        # Color selection
                        if event.key in [pygame.K_1, pygame.K_2,
                                       pygame.K_3, pygame.K_4]:
                            self.current_color_index = int(event.unicode) - 1
                            if self.current_color_index >= len(self.COLORS):
                                self.current_color_index = 0
            
            if self.game_state == self.STATE_PLAYING:
                # Move player
                keys = pygame.key.get_pressed()
                if keys[pygame.K_LEFT]:
                    self.player_x = max(self.player_width//2,
                                      self.player_x - 5)
                if keys[pygame.K_RIGHT]:
                    self.player_x = min(self.WINDOW_SIZE[0] - self.player_width//2,
                                      self.player_x + 5)
                    
                # Spawn targets
                self.spawn_timer += 1
                if self.spawn_timer >= 60:
                    self.spawn_target()
                    self.spawn_power_up()
                    self.spawn_timer = 0
                    
                # Update projectiles
                for projectile in self.projectiles[:]:
                    projectile.update()
                    if projectile.y < -10:
                        self.projectiles.remove(projectile)
                        self.combo = 0
                        
                # Update targets
                for target in self.targets[:]:
                    if target.update(self.WINDOW_SIZE[0], self.WINDOW_SIZE[1]):
                        self.targets.remove(target)
                    elif target.y > self.WINDOW_SIZE[1]:
                        self.targets.remove(target)
                        self.combo = 0
                        if self.score > 0:
                            self.score -= 10
                            
                # Update power-ups
                self.update_power_ups()
                
                # Update power-up timers
                if self.rainbow_timer > 0:
                    self.rainbow_timer -= 1
                    if self.rainbow_timer == 0:
                        self.rainbow_shot = False
                        
                if self.slow_timer > 0:
                    self.slow_timer -= 1
                    if self.slow_timer == 0:
                        self.slow_motion = False
                        
                # Check collisions
                for projectile in self.projectiles[:]:
                    for target in self.targets[:]:
                        dx = target.x - projectile.x
                        dy = target.y - projectile.y
                        if math.sqrt(dx*dx + dy*dy) < target.size:
                            if (self.rainbow_shot or
                                projectile.color == target.color):
                                # Hit with correct color
                                target.hit = True
                                self.projectiles.remove(projectile)
                                self.score += 10 * (self.combo + 1)
                                self.combo += 1
                                self.shots_hit += 1
                                self.particle_system.create_hit_burst(
                                    target.x, target.y, target.color)
                                
                                # Show combo text
                                if self.combo > 1:
                                    self.combo_text = f"Combo x{self.combo}!"
                                    self.combo_timer = 60
                            else:
                                # Hit with wrong color
                                self.combo = 0
                                self.projectiles.remove(projectile)
                            break
                            
                # Update particles
                self.particle_system.update()
                
                # Create background particles
                if random.random() < 0.1:
                    self.particle_system.create_background_particle(
                        self.WINDOW_SIZE[0], self.WINDOW_SIZE[1])
                    
                # Update level
                self.level = min(3, 1 + self.score // 200)
                
            # Draw everything
            screen.fill(self.BLACK)
            
            # Draw background particles
            self.particle_system.draw(screen)
            
            if self.game_state == self.STATE_MENU:
                self.draw_menu(screen)
            elif self.game_state == self.STATE_PLAYING:
                # Draw targets
                for target in self.targets:
                    target.draw(screen)
                    
                # Draw projectiles
                for projectile in self.projectiles:
                    projectile.draw(screen)
                    
                # Draw power-ups
                self.draw_power_ups(screen)
                
                # Draw player
                player_color = self.COLORS[self.current_color_index]
                pygame.draw.rect(screen, player_color,
                               (self.player_x - self.player_width//2,
                                self.WINDOW_SIZE[1] - self.player_height,
                                self.player_width,
                                self.player_height))
                
                # Draw particles
                self.particle_system.draw(screen)
                
                # Draw HUD
                self.draw_hud(screen)
                
                # Draw combo text
                if self.combo_text and self.combo_timer > 0:
                    combo_surface = self.menu_font.render(
                        self.combo_text, True, self.WHITE)
                    alpha = min(255, self.combo_timer * 4)
                    combo_surface.set_alpha(alpha)
                    combo_rect = combo_surface.get_rect(
                        center=(self.WINDOW_SIZE[0]//2,
                               self.WINDOW_SIZE[1]//2))
                    screen.blit(combo_surface, combo_rect)
                    self.combo_timer -= 1
                    
            elif self.game_state == self.STATE_GAME_OVER:
                self.draw_game_over(screen)
                
            pygame.display.flip()
            
            # Control game speed
            if self.slow_motion:
                clock.tick(self.FPS // 2)
            else:
                clock.tick(self.FPS)
            
        return True  # Return to main menu
