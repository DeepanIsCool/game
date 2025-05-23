import pygame
import random
import math
import numpy as np
from typing import List, Dict, Tuple
import os

class Collectible:
    def __init__(self, x: int, y: int, type: str):
        self.x = x
        self.y = y
        self.type = type
        self.collected = False
        self.glow_radius = 0
        self.pulse = 0
        
    def update(self):
        self.pulse = (math.sin(pygame.time.get_ticks() * 0.003) + 1) * 0.5
        
    def draw(self, screen, cell_size: int, visible: bool):
        if self.collected:
            return
            
        if visible or self.type in ['key', 'treasure']:
            x = self.x * cell_size + cell_size // 2
            y = self.y * cell_size + cell_size // 2
            
            # Draw glow effect
            glow_surface = pygame.Surface((cell_size * 2, cell_size * 2), 
                                        pygame.SRCALPHA)
            glow_radius = int(cell_size * (0.5 + self.pulse * 0.2))
            
            if self.type == 'coin':
                color = (255, 215, 0, 100)  # Gold
            elif self.type == 'key':
                color = (0, 255, 255, 100)  # Cyan
            else:  # treasure
                color = (255, 100, 100, 100)  # Red
                
            pygame.draw.circle(glow_surface, color, 
                             (cell_size, cell_size), glow_radius)
            screen.blit(glow_surface, 
                       (x - cell_size, y - cell_size))
            
            # Draw item
            if self.type == 'coin':
                pygame.draw.circle(screen, (255, 215, 0), 
                                 (x, y), cell_size // 4)
            elif self.type == 'key':
                key_rect = pygame.Rect(x - cell_size//4, y - cell_size//8, 
                                     cell_size//2, cell_size//4)
                pygame.draw.rect(screen, (0, 255, 255), key_rect)
            else:  # treasure
                chest_rect = pygame.Rect(x - cell_size//3, y - cell_size//3, 
                                       cell_size*2//3, cell_size*2//3)
                pygame.draw.rect(screen, (139, 69, 19), chest_rect)
                pygame.draw.rect(screen, (255, 215, 0), chest_rect, 2)

class Trap:
    def __init__(self, x: int, y: int, type: str):
        self.x = x
        self.y = y
        self.type = type
        self.active = True
        self.animation = 0
        
    def update(self):
        self.animation = (self.animation + 0.1) % (2 * math.pi)
        
    def draw(self, screen, cell_size: int, visible: bool):
        if not visible:
            return
            
        x = self.x * cell_size + cell_size // 2
        y = self.y * cell_size + cell_size // 2
        
        if self.type == 'spikes':
            # Draw spikes
            spike_height = int(cell_size//3 * (1 + math.sin(self.animation) * 0.2))
            for i in range(3):
                spike_x = x - cell_size//3 + (cell_size//3 * i)
                pygame.draw.polygon(screen, (200, 200, 200),
                                  [(spike_x, y + spike_height//2),
                                   (spike_x + cell_size//6, y - spike_height//2),
                                   (spike_x + cell_size//3, y + spike_height//2)])
        elif self.type == 'pit':
            # Draw pit
            pygame.draw.circle(screen, (40, 40, 40), (x, y), 
                             cell_size//3)
            pygame.draw.circle(screen, (20, 20, 20), (x, y), 
                             cell_size//3, 2)

class EchoMaze:
    def __init__(self):
        self.WINDOW_SIZE = (800, 600)
        self.FPS = 60
        self.CELL_SIZE = 40
        self.GRID_WIDTH = self.WINDOW_SIZE[0] // self.CELL_SIZE
        self.GRID_HEIGHT = self.WINDOW_SIZE[1] // self.CELL_SIZE
        
        # Colors
        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)
        self.WALL_COLOR = (100, 100, 100)
        self.PATH_COLOR = (50, 50, 50)
        self.RUNE_COLOR = (0, 255, 255)
        
        # Game states
        self.STATE_MENU = 'menu'
        self.STATE_PLAYING = 'playing'
        self.STATE_GAME_OVER = 'game_over'
        self.STATE_WIN = 'win'
        
        # Load fonts
        self.title_font = pygame.font.Font(None, 74)
        self.menu_font = pygame.font.Font(None, 36)
        self.hud_font = pygame.font.Font(None, 24)
        
        # Initialize game
        self.reset_game()
        
    def reset_game(self):
        self.game_state = self.STATE_MENU
        self.maze = self.generate_maze()
        self.player_pos = [1, 1]
        self.visited = np.zeros((self.GRID_HEIGHT, self.GRID_WIDTH), dtype=bool)
        self.visible = np.zeros((self.GRID_HEIGHT, self.GRID_WIDTH), dtype=bool)
        self.collectibles: List[Collectible] = []
        self.traps: List[Trap] = []
        self.keys_collected = 0
        self.total_keys = 3
        self.coins_collected = 0
        self.total_coins = 10
        self.time_left = 180 * self.FPS  # 3 minutes
        self.echo_timer = 0
        self.echo_cooldown = 60  # 1 second
        self.echo_radius = 5
        self.heartbeat = 0
        self.footstep_timer = 0
        self.rune_animations: List[Dict] = []
        
        # Place collectibles and traps
        self.place_items()
        
    def is_path_available(self, maze: np.ndarray, start: Tuple[int, int], 
                         end: Tuple[int, int]) -> bool:
        """Check if there's a path between start and end points using BFS."""
        if maze[start[1]][start[0]] == 1 or maze[end[1]][end[0]] == 1:
            return False
            
        visited = set()
        queue = [(start[0], start[1])]
        visited.add((start[0], start[1]))
        
        while queue:
            x, y = queue.pop(0)
            if (x, y) == end:
                return True
                
            # Check all four directions
            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                new_x, new_y = x + dx, y + dy
                if (0 <= new_x < self.GRID_WIDTH and 
                    0 <= new_y < self.GRID_HEIGHT and 
                    maze[new_y][new_x] == 0 and 
                    (new_x, new_y) not in visited):
                    queue.append((new_x, new_y))
                    visited.add((new_x, new_y))
        
        return False

    def generate_maze(self) -> np.ndarray:
        while True:
            # Initialize maze with walls
            maze = np.ones((self.GRID_HEIGHT, self.GRID_WIDTH), dtype=int)
            
            def carve_path(x: int, y: int):
                maze[y][x] = 0
                directions = [(0, 2), (2, 0), (0, -2), (-2, 0)]
                random.shuffle(directions)
                
                for dx, dy in directions:
                    new_x, new_y = x + dx, y + dy
                    if (0 <= new_x < self.GRID_WIDTH and 
                        0 <= new_y < self.GRID_HEIGHT and 
                        maze[new_y][new_x] == 1):
                        maze[y + dy//2][x + dx//2] = 0
                        carve_path(new_x, new_y)
            
            # Start from the entrance
            start_x, start_y = 1, 1
            carve_path(start_x, start_y)
            
            # Verify maze connectivity
            # Count accessible cells
            accessible = 0
            for y in range(self.GRID_HEIGHT):
                for x in range(self.GRID_WIDTH):
                    if maze[y][x] == 0:
                        if self.is_path_available(maze, (1, 1), (x, y)):
                            accessible += 1
            
            # Calculate total paths
            total_paths = np.sum(maze == 0)
            
            # If at least 90% of paths are accessible, use this maze
            if accessible >= total_paths * 0.9:
                return maze
        
    def place_items(self):
        # Get all accessible positions
        accessible_positions = []
        for y in range(self.GRID_HEIGHT):
            for x in range(self.GRID_WIDTH):
                if (self.maze[y][x] == 0 and 
                    self.is_path_available(self.maze, (1, 1), (x, y))):
                    accessible_positions.append((x, y))
        
        if len(accessible_positions) < (self.total_keys + self.total_coins + 1):
            # Not enough accessible positions, regenerate maze
            self.maze = self.generate_maze()
            self.place_items()
            return
            
        # Remove starting position from available positions
        if (1, 1) in accessible_positions:
            accessible_positions.remove((1, 1))
            
        # Place keys in increasing distance from start
        key_positions = []
        remaining_positions = accessible_positions.copy()
        for _ in range(self.total_keys):
            # Find position with good spacing from previous keys
            best_pos = None
            best_score = -1
            
            for pos in remaining_positions:
                # Calculate minimum distance to existing keys
                min_key_dist = float('inf')
                if key_positions:
                    for key_pos in key_positions:
                        dist = abs(pos[0] - key_pos[0]) + abs(pos[1] - key_pos[1])
                        min_key_dist = min(min_key_dist, dist)
                else:
                    min_key_dist = abs(pos[0] - 1) + abs(pos[1] - 1)  # Distance from start
                
                # Score based on distance from start and other keys
                score = min_key_dist
                
                if score > best_score:
                    best_score = score
                    best_pos = pos
            
            if best_pos:
                key_positions.append(best_pos)
                remaining_positions.remove(best_pos)
                self.collectibles.append(Collectible(best_pos[0], best_pos[1], 'key'))
            
        # Place coins along paths between keys
        coin_positions = []
        for _ in range(self.total_coins):
            if not remaining_positions:
                break
                
            # Find position with good distribution
            best_pos = None
            best_score = -1
            
            for pos in remaining_positions:
                # Calculate distances to keys and other coins
                min_key_dist = float('inf')
                min_coin_dist = float('inf')
                
                for key_pos in key_positions:
                    dist = abs(pos[0] - key_pos[0]) + abs(pos[1] - key_pos[1])
                    min_key_dist = min(min_key_dist, dist)
                    
                for coin_pos in coin_positions:
                    dist = abs(pos[0] - coin_pos[0]) + abs(pos[1] - coin_pos[1])
                    min_coin_dist = min(min_coin_dist, dist)
                
                # Score based on balanced distribution
                score = min(min_key_dist, min_coin_dist if coin_positions else float('inf'))
                
                if score > best_score:
                    best_score = score
                    best_pos = pos
            
            if best_pos:
                coin_positions.append(best_pos)
                remaining_positions.remove(best_pos)
                self.collectibles.append(Collectible(best_pos[0], best_pos[1], 'coin'))
        
        # Place treasure at the furthest accessible point from start
        if remaining_positions:
            treasure_pos = max(remaining_positions,
                             key=lambda p: abs(p[0] - 1) + abs(p[1] - 1))
            self.collectibles.append(
                Collectible(treasure_pos[0], treasure_pos[1], 'treasure'))
            remaining_positions.remove(treasure_pos)
        
        # Place traps avoiding blocking paths
        num_traps = min(5 + self.GRID_WIDTH // 4, len(remaining_positions))
        for _ in range(num_traps):
            if not remaining_positions:
                break
                
            # Find position that doesn't block critical paths
            valid_positions = []
            for pos in remaining_positions:
                # Temporarily place trap
                self.maze[pos[1]][pos[0]] = 1
                
                # Check if all collectibles are still accessible
                all_accessible = True
                for collectible in self.collectibles:
                    if not collectible.collected and not self.is_path_available(
                        self.maze, (1, 1), (collectible.x, collectible.y)):
                        all_accessible = False
                        break
                
                # Remove temporary trap
                self.maze[pos[1]][pos[0]] = 0
                
                if all_accessible:
                    valid_positions.append(pos)
            
            if valid_positions:
                trap_pos = random.choice(valid_positions)
                remaining_positions.remove(trap_pos)
                trap_type = random.choice(['spikes', 'pit'])
                self.traps.append(Trap(trap_pos[0], trap_pos[1], trap_type))
                    
    def update_visibility(self):
        self.visible.fill(False)
        px, py = self.player_pos
        
        # Update visited cells
        self.visited[py][px] = True
        
        # Calculate visibility using distance from player
        for y in range(max(0, py - self.echo_radius), 
                      min(self.GRID_HEIGHT, py + self.echo_radius + 1)):
            for x in range(max(0, px - self.echo_radius), 
                         min(self.GRID_WIDTH, px + self.echo_radius + 1)):
                dist = math.sqrt((x - px)**2 + (y - py)**2)
                if dist <= self.echo_radius:
                    self.visible[y][x] = True
                    
    def create_rune_animation(self, x: int, y: int):
        self.rune_animations.append({
            'x': x,
            'y': y,
            'alpha': 255,
            'size': 1.0
        })
        
    def update_rune_animations(self):
        for anim in self.rune_animations[:]:
            anim['alpha'] = max(0, anim['alpha'] - 5)
            anim['size'] += 0.02
            if anim['alpha'] <= 0:
                self.rune_animations.remove(anim)
                
    def draw_menu(self, screen):
        # Draw title
        title = self.title_font.render("ECHO MAZE:", True, self.WHITE)
        subtitle = self.title_font.render("The Forgotten Temple", True, 
                                        self.RUNE_COLOR)
        title_rect = title.get_rect(center=(self.WINDOW_SIZE[0]//2, 150))
        subtitle_rect = subtitle.get_rect(center=(self.WINDOW_SIZE[0]//2, 220))
        screen.blit(title, title_rect)
        screen.blit(subtitle, subtitle_rect)
        
        # Draw intro text
        intro_text = [
            "You are deep within an ancient maze.",
            "Only your echo reveals the way forward.",
            "Can you find the treasure before time runs out?"
        ]
        
        for i, text in enumerate(intro_text):
            text_surface = self.menu_font.render(text, True, self.WHITE)
            text_rect = text_surface.get_rect(
                center=(self.WINDOW_SIZE[0]//2, 300 + i*40))
            screen.blit(text_surface, text_rect)
            
        # Draw controls
        controls = [
            "Controls:",
            "Arrow keys/WASD: Move",
            "Space: Ping (Reveal surroundings)",
            "M: Toggle map"
        ]
        
        for i, text in enumerate(controls):
            text_surface = self.menu_font.render(text, True, self.WHITE)
            text_rect = text_surface.get_rect(
                center=(self.WINDOW_SIZE[0]//2, 420 + i*30))
            screen.blit(text_surface, text_rect)
            
        # Draw "Press Space to Start"
        if (pygame.time.get_ticks() // 500) % 2:
            start_text = self.menu_font.render("Press SPACE to Start", 
                                             True, self.RUNE_COLOR)
            start_rect = start_text.get_rect(
                center=(self.WINDOW_SIZE[0]//2, 550))
            screen.blit(start_text, start_rect)
            
    def draw_game_over(self, screen):
        # Draw "Game Over"
        game_over = self.title_font.render("GAME OVER", True, self.WHITE)
        game_over_rect = game_over.get_rect(
            center=(self.WINDOW_SIZE[0]//2, 200))
        screen.blit(game_over, game_over_rect)
        
        # Draw stats
        stats = [
            f"Keys Collected: {self.keys_collected}/{self.total_keys}",
            f"Coins Collected: {self.coins_collected}/{self.total_coins}",
            f"Time Remaining: {self.time_left // self.FPS}s"
        ]
        
        for i, text in enumerate(stats):
            text_surface = self.menu_font.render(text, True, self.WHITE)
            text_rect = text_surface.get_rect(
                center=(self.WINDOW_SIZE[0]//2, 300 + i*40))
            screen.blit(text_surface, text_rect)
            
        # Draw restart instructions
        if (pygame.time.get_ticks() // 500) % 2:
            restart_text = self.menu_font.render(
                "Press R to Retry or ESC to Exit", True, self.WHITE)
            restart_rect = restart_text.get_rect(
                center=(self.WINDOW_SIZE[0]//2, 450))
            screen.blit(restart_text, restart_rect)
            
    def draw_win_screen(self, screen):
        # Draw "Victory!"
        win_text = self.title_font.render("VICTORY!", True, self.RUNE_COLOR)
        win_rect = win_text.get_rect(center=(self.WINDOW_SIZE[0]//2, 200))
        screen.blit(win_text, win_rect)
        
        # Draw stats
        stats = [
            f"Keys Collected: {self.keys_collected}/{self.total_keys}",
            f"Coins Collected: {self.coins_collected}/{self.total_coins}",
            f"Time Remaining: {self.time_left // self.FPS}s"
        ]
        
        for i, text in enumerate(stats):
            text_surface = self.menu_font.render(text, True, self.WHITE)
            text_rect = text_surface.get_rect(
                center=(self.WINDOW_SIZE[0]//2, 300 + i*40))
            screen.blit(text_surface, text_rect)
            
        # Draw restart instructions
        if (pygame.time.get_ticks() // 500) % 2:
            restart_text = self.menu_font.render(
                "Press R to Play Again or ESC to Exit", True, self.WHITE)
            restart_rect = restart_text.get_rect(
                center=(self.WINDOW_SIZE[0]//2, 450))
            screen.blit(restart_text, restart_rect)
            
    def draw_hud(self, screen):
        # Draw time
        time_text = self.hud_font.render(
            f"Time: {self.time_left // self.FPS}s", True, self.WHITE)
        screen.blit(time_text, (10, 10))
        
        # Draw keys
        key_text = self.hud_font.render(
            f"Keys: {self.keys_collected}/{self.total_keys}", True, 
            (0, 255, 255))
        screen.blit(key_text, (10, 40))
        
        # Draw coins
        coin_text = self.hud_font.render(
            f"Coins: {self.coins_collected}/{self.total_coins}", True, 
            (255, 215, 0))
        screen.blit(coin_text, (10, 70))
        
        # Draw echo cooldown
        if self.echo_timer > 0:
            cooldown = self.echo_timer / self.echo_cooldown
            pygame.draw.rect(screen, (50, 50, 50),
                           (self.WINDOW_SIZE[0] - 110, 10, 100, 20))
            pygame.draw.rect(screen, self.RUNE_COLOR,
                           (self.WINDOW_SIZE[0] - 110, 10, 
                            100 * (1 - cooldown), 20))
            
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
                        elif (self.game_state == self.STATE_PLAYING and 
                              self.echo_timer <= 0):
                            self.echo_timer = self.echo_cooldown
                            # Create echo effect
                            self.echo_radius = 8  # Temporary larger radius
                    elif event.key == pygame.K_r and self.game_state in [
                        self.STATE_GAME_OVER, self.STATE_WIN]:
                        self.reset_game()
                        self.game_state = self.STATE_PLAYING
                        
            if self.game_state == self.STATE_PLAYING:
                # Move player
                keys = pygame.key.get_pressed()
                new_pos = self.player_pos.copy()
                moved = False
                
                if (keys[pygame.K_LEFT] or keys[pygame.K_a]) and \
                   self.player_pos[0] > 0:
                    new_pos[0] -= 1
                    moved = True
                elif (keys[pygame.K_RIGHT] or keys[pygame.K_d]) and \
                     self.player_pos[0] < self.GRID_WIDTH - 1:
                    new_pos[0] += 1
                    moved = True
                elif (keys[pygame.K_UP] or keys[pygame.K_w]) and \
                     self.player_pos[1] > 0:
                    new_pos[1] -= 1
                    moved = True
                elif (keys[pygame.K_DOWN] or keys[pygame.K_s]) and \
                     self.player_pos[1] < self.GRID_HEIGHT - 1:
                    new_pos[1] += 1
                    moved = True
                    
                # Check if move is valid
                if moved and self.maze[new_pos[1]][new_pos[0]] == 0:
                    self.player_pos = new_pos
                    self.create_rune_animation(*self.player_pos)
                    self.footstep_timer = 10
                    
                # Update collectibles
                for collectible in self.collectibles:
                    if not collectible.collected and \
                       collectible.x == self.player_pos[0] and \
                       collectible.y == self.player_pos[1]:
                        collectible.collected = True
                        if collectible.type == 'key':
                            self.keys_collected += 1
                        elif collectible.type == 'coin':
                            self.coins_collected += 1
                        elif collectible.type == 'treasure' and \
                             self.keys_collected >= self.total_keys:
                            self.game_state = self.STATE_WIN
                            
                # Check traps
                for trap in self.traps:
                    if trap.active and \
                       trap.x == self.player_pos[0] and \
                       trap.y == self.player_pos[1]:
                        self.game_state = self.STATE_GAME_OVER
                        
                # Update timers
                if self.echo_timer > 0:
                    self.echo_timer -= 1
                    if self.echo_timer == 0:
                        self.echo_radius = 5  # Reset to normal radius
                        
                self.time_left -= 1
                if self.time_left <= 0:
                    self.game_state = self.STATE_GAME_OVER
                    
                # Update animations
                self.update_rune_animations()
                for collectible in self.collectibles:
                    collectible.update()
                for trap in self.traps:
                    trap.update()
                    
                # Update visibility
                self.update_visibility()
                
            # Draw everything
            screen.fill(self.BLACK)
            
            if self.game_state == self.STATE_MENU:
                self.draw_menu(screen)
            else:
                # Draw maze
                for y in range(self.GRID_HEIGHT):
                    for x in range(self.GRID_WIDTH):
                        if self.visible[y][x] or self.visited[y][x]:
                            rect = pygame.Rect(x * self.CELL_SIZE,
                                            y * self.CELL_SIZE,
                                            self.CELL_SIZE,
                                            self.CELL_SIZE)
                            
                            if self.maze[y][x] == 1:
                                # Draw wall
                                color = self.WALL_COLOR
                                if not self.visible[y][x]:
                                    color = tuple(c // 3 for c in color)
                                pygame.draw.rect(screen, color, rect)
                                # Add edge highlight
                                pygame.draw.rect(screen, 
                                               tuple(min(255, c + 50) 
                                                     for c in color),
                                               rect, 1)
                            else:
                                # Draw floor
                                color = self.PATH_COLOR
                                if not self.visible[y][x]:
                                    color = tuple(c // 3 for c in color)
                                pygame.draw.rect(screen, color, rect)
                                
                # Draw rune animations
                for anim in self.rune_animations:
                    surface = pygame.Surface((self.CELL_SIZE * 2, 
                                           self.CELL_SIZE * 2), 
                                          pygame.SRCALPHA)
                    size = int(self.CELL_SIZE * anim['size'])
                    pygame.draw.rect(surface,
                                   (*self.RUNE_COLOR[:3], anim['alpha']),
                                   (self.CELL_SIZE - size//2,
                                    self.CELL_SIZE - size//2,
                                    size, size))
                    screen.blit(surface,
                              (anim['x'] * self.CELL_SIZE - self.CELL_SIZE//2,
                               anim['y'] * self.CELL_SIZE - self.CELL_SIZE//2))
                    
                # Draw collectibles
                for collectible in self.collectibles:
                    collectible.draw(screen, self.CELL_SIZE,
                                   self.visible[collectible.y][collectible.x])
                    
                # Draw traps
                for trap in self.traps:
                    trap.draw(screen, self.CELL_SIZE,
                            self.visible[trap.y][trap.x])
                    
                # Draw player
                pygame.draw.circle(screen, self.RUNE_COLOR,
                                 (self.player_pos[0] * self.CELL_SIZE + 
                                  self.CELL_SIZE // 2,
                                  self.player_pos[1] * self.CELL_SIZE + 
                                  self.CELL_SIZE // 2),
                                 self.CELL_SIZE // 3)
                
                # Draw HUD
                self.draw_hud(screen)
                
                if self.game_state == self.STATE_GAME_OVER:
                    self.draw_game_over(screen)
                elif self.game_state == self.STATE_WIN:
                    self.draw_win_screen(screen)
                    
            pygame.display.flip()
            clock.tick(self.FPS)
            
        return True  # Return to main menu
