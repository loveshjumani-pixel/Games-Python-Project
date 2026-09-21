import pygame
import random
import sys
import math

# Initialize Pygame
pygame.init()
pygame.mixer.init()

# Screen Settings
WIDTH = 900
HEIGHT = 700
FPS = 60

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 50, 50)
GREEN = (50, 255, 50)
BLUE = (50, 150, 255)
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
ORANGE = (255, 165, 0)
PURPLE = (180, 0, 255)
DARK_BLUE = (5, 5, 30)
NEON_BLUE = (100, 200, 255)
NEON_RED = (255, 80, 80)
NEON_GREEN = (80, 255, 80)

# Initialize display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('🚀 Space Destroyer - Advanced Edition')
clock = pygame.time.Clock()

# Fonts
font_small = pygame.font.SysFont('arial', 20, bold=True)
font_medium = pygame.font.SysFont('arial', 32, bold=True)
font_large = pygame.font.SysFont('arial', 50, bold=True)
font_xlarge = pygame.font.SysFont('arial', 70, bold=True)

class Star:
    """Background stars with parallax effect"""
    def __init__(self):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(0, HEIGHT)
        self.size = random.randint(1, 3)
        self.speed = self.size * 0.5
        self.brightness = random.randint(100, 255)
    
    def update(self, scroll_speed):
        self.y += self.speed + scroll_speed * 0.1
        if self.y > HEIGHT:
            self.y = 0
            self.x = random.randint(0, WIDTH)
    
    def draw(self, surface):
        color = (self.brightness, self.brightness, min(255, self.brightness + 50))
        pygame.draw.circle(surface, color, (int(self.x), int(self.y)), self.size)

class Particle:
    """Explosion and effect particles"""
    def __init__(self, x, y, color, speed_x, speed_y, lifetime, size=None):
        self.x = x
        self.y = y
        self.color = color
        self.speed_x = speed_x
        self.speed_y = speed_y
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.size = size if size else random.randint(2, 6)
        self.gravity = 0.1
    
    def update(self):
        self.x += self.speed_x
        self.y += self.speed_y
        self.speed_y += self.gravity
        self.lifetime -= 1
        self.size = max(0.5, self.size - 0.1)
    
    def draw(self, surface):
        if self.lifetime > 0:
            alpha = int(255 * (self.lifetime / self.max_lifetime))
            s = pygame.Surface((int(self.size*2), int(self.size*2)), pygame.SRCALPHA)
            color_with_alpha = (self.color[0], self.color[1], self.color[2], alpha)
            pygame.draw.circle(s, color_with_alpha, (int(self.size), int(self.size)), int(self.size))
            surface.blit(s, (int(self.x - self.size), int(self.y - self.size)))

class Bullet:
    """Player and enemy bullets"""
    def __init__(self, x, y, speed_y, color, is_player=True, damage=1):
        self.x = x
        self.y = y
        self.width = 4 if is_player else 6
        self.height = 15 if is_player else 12
        self.speed_y = speed_y
        self.color = color
        self.is_player = is_player
        self.damage = damage
        self.active = True
    
    def update(self):
        self.y += self.speed_y
        if self.y < -20 or self.y > HEIGHT + 20:
            self.active = False
    
    def draw(self, surface):
        # Bullet glow
        glow_rect = pygame.Surface((self.width + 4, self.height + 4), pygame.SRCALPHA)
        glow_color = (self.color[0], self.color[1], self.color[2], 100)
        pygame.draw.rect(glow_rect, glow_color, (0, 0, self.width + 4, self.height + 4), border_radius=3)
        surface.blit(glow_rect, (self.x - 2, self.y - 2))
        
        # Main bullet
        pygame.draw.rect(surface, self.color, 
                        pygame.Rect(self.x, self.y, self.width, self.height), border_radius=2)
        
        # Bullet core
        core_color = WHITE
        pygame.draw.rect(surface, core_color, 
                        pygame.Rect(self.x + 1, self.y + 2, self.width - 2, self.height - 4), border_radius=1)
    
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

class Player:
    """Player spaceship"""
    def __init__(self):
        self.width = 50
        self.height = 60
        self.x = WIDTH // 2 - self.width // 2
        self.y = HEIGHT - 120
        self.speed = 6
        self.health = 100
        self.max_health = 100
        self.shield = 0
        self.max_shield = 50
        self.shield_regen = 0.1
        self.weapon_level = 1
        self.fire_rate = 15  # frames between shots
        self.fire_timer = 0
        self.invincible = 0
        self.power_ups = {
            'rapid_fire': 0,
            'triple_shot': 0,
            'shield_boost': 0
        }
    
    def move(self, keys):
        # Horizontal movement
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.x -= self.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.x += self.speed
        
        # Vertical movement
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.y -= self.speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.y += self.speed
        
        # Keep on screen
        self.x = max(0, min(WIDTH - self.width, self.x))
        self.y = max(0, min(HEIGHT - self.height, self.y))
        
        # Shield regeneration
        if self.shield < self.max_shield:
            self.shield = min(self.max_shield, self.shield + self.shield_regen)
        
        # Invincibility timer
        if self.invincible > 0:
            self.invincible -= 1
        
        # Power-up timers
        for power in self.power_ups:
            if self.power_ups[power] > 0:
                self.power_ups[power] -= 1
    
    def shoot(self):
        self.fire_timer -= 1
        if self.fire_timer <= 0:
            bullets = []
            
            # Determine fire rate
            current_fire_rate = self.fire_rate
            if self.power_ups['rapid_fire'] > 0:
                current_fire_rate = self.fire_rate // 2
            
            self.fire_timer = current_fire_rate
            
            # Center shot
            bullets.append(Bullet(self.x + self.width//2 - 2, self.y, -12, CYAN, True, self.weapon_level))
            
            # Triple shot
            if self.power_ups['triple_shot'] > 0 or self.weapon_level >= 3:
                bullets.append(Bullet(self.x + 5, self.y + 10, -10, CYAN, True, 1))
                bullets.append(Bullet(self.x + self.width - 9, self.y + 10, -10, CYAN, True, 1))
            
            # Double shot at higher levels
            if self.weapon_level >= 2:
                bullets.append(Bullet(self.x + 10, self.y + 5, -11, BLUE, True, 1))
                bullets.append(Bullet(self.x + self.width - 14, self.y + 5, -11, BLUE, True, 1))
            
            return bullets
        return []
    
    def take_damage(self, damage):
        if self.invincible > 0:
            return False
        
        # Shield absorbs damage first
        if self.shield > 0:
            shield_damage = min(self.shield, damage)
            self.shield -= shield_damage
            damage -= shield_damage
        
        if damage > 0:
            self.health -= damage
            self.invincible = 60  # 1 second invincibility
            return True
        return False
    
    def draw(self, surface, frame_count):
        # Flicker when invincible
        if self.invincible > 0 and frame_count % 6 < 3:
            return
        
        # Engine glow
        glow_size = 15 + int(5 * math.sin(frame_count * 0.3))
        engine_glow = pygame.Surface((self.width + 20, glow_size + 10), pygame.SRCALPHA)
        pygame.draw.ellipse(engine_glow, (100, 200, 255, 150), 
                           (5, 0, self.width + 10, glow_size + 10))
        surface.blit(engine_glow, (self.x - 10, self.y + self.height - 5))
        
        # Engine flames
        flame_height = random.randint(15, 25)
        flame_points = [
            (self.x + 15, self.y + self.height),
            (self.x + 35, self.y + self.height),
            (self.x + 25, self.y + self.height + flame_height)
        ]
        pygame.draw.polygon(surface, ORANGE, flame_points)
        pygame.draw.polygon(surface, YELLOW, [
            (self.x + 18, self.y + self.height),
            (self.x + 32, self.y + self.height),
            (self.x + 25, self.y + self.height + flame_height//2)
        ])
        
        # Main ship body
        ship_color = NEON_BLUE if self.shield > 0 else BLUE
        pygame.draw.polygon(surface, ship_color, [
            (self.x + self.width//2, self.y),
            (self.x + self.width - 10, self.y + 20),
            (self.x + self.width, self.y + 40),
            (self.x + self.width - 5, self.y + self.height),
            (self.x + 5, self.y + self.height),
            (self.x, self.y + 40),
            (self.x + 10, self.y + 20)
        ])
        
        # Ship details - cockpit
        pygame.draw.polygon(surface, (20, 20, 60), [
            (self.x + self.width//2, self.y + 10),
            (self.x + self.width//2 + 10, self.y + 25),
            (self.x + self.width//2 - 10, self.y + 25)
        ])
        
        # Wings
        pygame.draw.polygon(surface, (30, 30, 100), [
            (self.x + 5, self.y + 30),
            (self.x - 10, self.y + 50),
            (self.x, self.y + 45)
        ])
        pygame.draw.polygon(surface, (30, 30, 100), [
            (self.x + self.width - 5, self.y + 30),
            (self.x + self.width + 10, self.y + 50),
            (self.x + self.width, self.y + 45)
        ])
        
        # Shield effect
        if self.shield > 0:
            shield_alpha = int(100 + 50 * math.sin(frame_count * 0.1))
            shield_surface = pygame.Surface((self.width + 30, self.height + 30), pygame.SRCALPHA)
            pygame.draw.ellipse(shield_surface, (0, 255, 255, shield_alpha), 
                              (0, 0, self.width + 30, self.height + 30), 3)
            surface.blit(shield_surface, (self.x - 15, self.y - 15))
    
    def get_rect(self):
        return pygame.Rect(self.x + 5, self.y + 5, self.width - 10, self.height - 10)

class Enemy:
    """Enemy spaceship"""
    def __init__(self, x, y, enemy_type='basic'):
        self.x = x
        self.y = y
        self.type = enemy_type
        self.active = True
        self.fire_timer = random.randint(60, 180)
        
        # Type-specific properties
        if enemy_type == 'basic':
            self.width = 40
            self.height = 40
            self.health = 2
            self.speed = 2
            self.score = 100
            self.color = RED
            self.fire_rate = 120
        elif enemy_type == 'fast':
            self.width = 35
            self.height = 35
            self.health = 1
            self.speed = 4
            self.score = 150
            self.color = ORANGE
            self.fire_rate = 90
        elif enemy_type == 'tank':
            self.width = 55
            self.height = 55
            self.health = 5
            self.speed = 1
            self.score = 300
            self.color = PURPLE
            self.fire_rate = 150
        elif enemy_type == 'boss':
            self.width = 120
            self.height = 100
            self.health = 50
            self.speed = 1
            self.score = 2000
            self.color = MAGENTA
            self.fire_rate = 60
            self.phase = 0
            self.phase_timer = 0
    
    def update(self, player_x, player_y):
        # Movement patterns
        if self.type == 'basic':
            self.y += self.speed
            self.x += math.sin(self.y * 0.02) * 2
        elif self.type == 'fast':
            self.y += self.speed
            # Zigzag movement
            self.x += math.sin(self.y * 0.05) * 4
        elif self.type == 'tank':
            self.y += self.speed
        elif self.type == 'boss':
            self.phase_timer += 1
            if self.phase_timer > 180:
                self.phase = (self.phase + 1) % 3
                self.phase_timer = 0
            
            if self.phase == 0:
                # Move side to side
                self.x += math.sin(self.y * 0.01) * 3
                self.y += 0.5
            elif self.phase == 1:
                # Chase player
                if self.x < player_x:
                    self.x += 2
                elif self.x > player_x:
                    self.x -= 2
                self.y += 0.3
            else:
                # Rapid descent
                self.y += 2
        
        # Keep in bounds
        self.x = max(0, min(WIDTH - self.width, self.x))
        
        if self.y > HEIGHT + 50:
            self.active = False
    
    def shoot(self):
        self.fire_timer -= 1
        if self.fire_timer <= 0:
            self.fire_timer = self.fire_rate
            bullets = []
            
            if self.type == 'boss':
                # Boss shoots multiple bullets
                for i in range(5):
                    angle = -90 + (i - 2) * 20
                    rad = math.radians(angle)
                    speed_x = math.cos(rad) * 6
                    speed_y = math.sin(rad) * 6
                    bullets.append(Bullet(self.x + self.width//2, self.y + self.height, 
                                         speed_y, RED, False, 1))
            else:
                bullets.append(Bullet(self.x + self.width//2 - 3, self.y + self.height, 
                                     6, RED, False, 1))
            
            return bullets
        return []
    
    def take_damage(self, damage):
        self.health -= damage
        if self.health <= 0:
            self.active = False
            return True
        return False
    
    def draw(self, surface, frame_count):
        # Enemy glow
        glow_rect = pygame.Surface((self.width + 10, self.height + 10), pygame.SRCALPHA)
        glow_color = (self.color[0], self.color[1], self.color[2], 80)
        pygame.draw.rect(glow_rect, glow_color, (0, 0, self.width + 10, self.height + 10), border_radius=10)
        surface.blit(glow_rect, (self.x - 5, self.y - 5))
        
        # Main body
        if self.type == 'boss':
            # Boss design
            pygame.draw.polygon(surface, self.color, [
                (self.x + self.width//2, self.y + self.height),
                (self.x + self.width - 10, self.y + self.height//2),
                (self.x + self.width, self.y + 20),
                (self.x + self.width - 20, self.y),
                (self.x + 20, self.y),
                (self.x, self.y + 20),
                (self.x + 10, self.y + self.height//2)
            ])
            # Boss details
            pygame.draw.circle(surface, YELLOW, (int(self.x + 30), int(self.y + 30)), 10)
            pygame.draw.circle(surface, YELLOW, (int(self.x + self.width - 30), int(self.y + 30)), 10)
            pygame.draw.rect(surface, RED, 
                           pygame.Rect(self.x + 20, self.y + 50, self.width - 40, 20), border_radius=5)
        else:
            # Regular enemy design
            pygame.draw.polygon(surface, self.color, [
                (self.x + self.width//2, self.y + self.height),
                (self.x + self.width, self.y + self.height//2),
                (self.x + self.width - 10, self.y),
                (self.x + 10, self.y),
                (self.x, self.y + self.height//2)
            ])
            # Enemy cockpit
            pygame.draw.circle(surface, BLACK, 
                             (int(self.x + self.width//2), int(self.y + self.height//2)), 8)
        
        # Health bar for tank and boss
        if self.type in ['tank', 'boss']:
            bar_width = self.width
            bar_height = 6
            health_ratio = self.health / (5 if self.type == 'tank' else 50)
            pygame.draw.rect(surface, DARK_BLUE, 
                           pygame.Rect(self.x, self.y - 15, bar_width, bar_height))
            pygame.draw.rect(surface, GREEN, 
                           pygame.Rect(self.x, self.y - 15, int(bar_width * health_ratio), bar_height))
    
    def get_rect(self):
        return pygame.Rect(self.x + 5, self.y + 5, self.width - 10, self.height - 10)

class PowerUp:
    """Power-up items"""
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 35
        self.height = 35
        self.types = ['health', 'shield', 'weapon', 'rapid', 'triple']
        self.type = random.choice(self.types)
        self.speed = 3
        self.angle = 0
        self.active = True
    
    def update(self):
        self.y += self.speed
        self.angle += 5
        if self.y > HEIGHT + 50:
            self.active = False
    
    def draw(self, surface, frame_count):
        # Rotating glow
        pulse = int(5 + 3 * math.sin(frame_count * 0.1))
        
        colors = {
            'health': GREEN,
            'shield': CYAN,
            'weapon': YELLOW,
            'rapid': ORANGE,
            'triple': MAGENTA
        }
        
        symbols = {
            'health': '+',
            'shield': 'S',
            'weapon': 'W',
            'rapid': 'R',
            'triple': '3'
        }
        
        color = colors[self.type]
        
        # Outer glow
        glow_rect = pygame.Surface((self.width + pulse*2, self.height + pulse*2), pygame.SRCALPHA)
        glow_color = (color[0], color[1], color[2], 100)
        pygame.draw.circle(glow_rect, glow_color, 
                          (int((self.width + pulse*2)//2), int((self.height + pulse*2)//2)), 
                          int((self.width + pulse*2)//2))
        surface.blit(glow_rect, (self.x - pulse, self.y - pulse))
        
        # Main circle
        center_x = int(self.x + self.width//2)
        center_y = int(self.y + self.height//2)
        pygame.draw.circle(surface, color, (center_x, center_y), 18, 3)
        pygame.draw.circle(surface, (color[0]//2, color[1]//2, color[2]//2), 
                          (center_x, center_y), 16)
        
        # Symbol
        text = font_small.render(symbols[self.type], True, WHITE)
        text_rect = text.get_rect(center=(center_x, center_y))
        surface.blit(text, text_rect)
    
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

class Game:
    """Main game class"""
    def __init__(self):
        self.stars = [Star() for _ in range(100)]
        self.player = Player()
        self.bullets = []
        self.enemies = []
        self.particles = []
        self.power_ups = []
        self.score = 0
        self.high_score = 0
        self.level = 1
        self.enemies_destroyed = 0
        self.boss_spawned = False
        self.game_over = False
        self.paused = False
        self.frame_count = 0
        self.spawn_timer = 0
        self.difficulty = 1
    
    def spawn_enemy(self):
        # Don't spawn during boss fight
        if self.boss_spawned:
            return
        
        lanes = [100, 250, 400, 550, 700]
        x = random.choice(lanes)
        
        # Determine enemy type based on level
        rand = random.random()
        if self.level >= 3 and rand < 0.1:
            enemy_type = 'tank'
        elif self.level >= 2 and rand < 0.3:
            enemy_type = 'fast'
        else:
            enemy_type = 'basic'
        
        enemy = Enemy(x, -60, enemy_type)
        self.enemies.append(enemy)
    
    def spawn_boss(self):
        if not self.boss_spawned and self.enemies_destroyed >= self.level * 10:
            boss = Enemy(WIDTH//2 - 60, -120, 'boss')
            self.enemies.append(boss)
            self.boss_spawned = True
    
    def create_explosion(self, x, y, color, count=20):
        for _ in range(count):
            speed_x = random.uniform(-6, 6)
            speed_y = random.uniform(-6, 6)
            lifetime = random.randint(20, 40)
            self.particles.append(Particle(x, y, color, speed_x, speed_y, lifetime))
    
    def update(self):
        if self.game_over or self.paused:
            return
        
        self.frame_count += 1
        
        # Update stars
        for star in self.stars:
            star.update(self.player.speed if hasattr(self.player, 'speed') else 0)
        
        # Player input
        keys = pygame.key.get_pressed()
        self.player.move(keys)
        
        # Player shooting
        if keys[pygame.K_SPACE]:
            new_bullets = self.player.shoot()
            self.bullets.extend(new_bullets)
        
        # Spawn enemies
        self.spawn_timer += 1
        spawn_rate = max(30, 90 - self.level * 5)
        if self.spawn_timer >= spawn_rate:
            self.spawn_timer = 0
            self.spawn_enemy()
        
        # Spawn boss
        self.spawn_boss()
        
        # Update bullets
        for bullet in self.bullets[:]:
            bullet.update()
            if not bullet.active:
                self.bullets.remove(bullet)
        
        # Update enemies
        for enemy in self.enemies[:]:
            enemy.update(self.player.x, self.player.y)
            
            # Enemy shooting
            new_bullets = enemy.shoot()
            self.bullets.extend(new_bullets)
            
            if not enemy.active:
                # Enemy destroyed
                if enemy.type == 'boss':
                    self.boss_spawned = False
                    self.level += 1
                    self.difficulty += 0.5
                    self.create_explosion(enemy.x + enemy.width//2, 
                                        enemy.y + enemy.height//2, MAGENTA, 50)
                else:
                    self.enemies_destroyed += 1
                    self.score += enemy.score
                    self.create_explosion(enemy.x + enemy.width//2, 
                                        enemy.y + enemy.height//2, enemy.color, 25)
                self.enemies.remove(enemy)
        
        # Update power-ups
        for power_up in self.power_ups[:]:
            power_up.update()
            if not power_up.active:
                self.power_ups.remove(power_up)
        
        # Update particles
        for particle in self.particles[:]:
            particle.update()
            if particle.lifetime <= 0:
                self.particles.remove(particle)
        
        # Collision detection - Player bullets vs Enemies
        for bullet in self.bullets[:]:
            if bullet.is_player:
                for enemy in self.enemies[:]:
                    if bullet.active and enemy.active:
                        if bullet.get_rect().colliderect(enemy.get_rect()):
                            bullet.active = False
                            if enemy.take_damage(bullet.damage):
                                # Enemy destroyed
                                if enemy.type == 'boss':
                                    self.boss_spawned = False
                                    self.level += 1
                                    self.create_explosion(enemy.x + enemy.width//2, 
                                                        enemy.y + enemy.height//2, MAGENTA, 50)
                                else:
                                    self.enemies_destroyed += 1
                                    self.score += enemy.score
                                    self.create_explosion(enemy.x + enemy.width//2, 
                                                        enemy.y + enemy.height//2, enemy.color, 25)
                                    # Chance to drop power-up
                                    if random.random() < 0.15:
                                        self.power_ups.append(PowerUp(enemy.x, enemy.y))
                                self.enemies.remove(enemy)
                            else:
                                # Hit but not destroyed
                                self.create_explosion(bullet.x, bullet.y, WHITE, 5)
                            break
        
        # Collision detection - Enemy bullets vs Player
        for bullet in self.bullets[:]:
            if not bullet.is_player and bullet.active:
                if bullet.get_rect().colliderect(self.player.get_rect()):
                    bullet.active = False
                    if self.player.take_damage(bullet.damage * 10):
                        self.create_explosion(self.player.x + self.player.width//2, 
                                            self.player.y + self.player.height//2, CYAN, 15)
                        if self.player.health <= 0:
                            self.game_over = True
                            if self.score > self.high_score:
                                self.high_score = self.score
        
        # Collision detection - Enemies vs Player
        for enemy in self.enemies[:]:
            if enemy.active and enemy.get_rect().colliderect(self.player.get_rect()):
                if self.player.take_damage(20):
                    self.create_explosion(self.player.x + self.player.width//2, 
                                        self.player.y + self.player.height//2, CYAN, 20)
                    enemy.active = False
                    self.enemies.remove(enemy)
                    if self.player.health <= 0:
                        self.game_over = True
                        if self.score > self.high_score:
                            self.high_score = self.score
        
        # Collision detection - Power-ups vs Player
        for power_up in self.power_ups[:]:
            if power_up.active and power_up.get_rect().colliderect(self.player.get_rect()):
                power_up.active = False
                self.power_ups.remove(power_up)
                
                # Apply power-up effect
                if power_up.type == 'health':
                    self.player.health = min(self.player.max_health, self.player.health + 30)
                elif power_up.type == 'shield':
                    self.player.shield = self.player.max_shield
                elif power_up.type == 'weapon':
                    self.player.weapon_level = min(5, self.player.weapon_level + 1)
                elif power_up.type == 'rapid':
                    self.player.power_ups['rapid_fire'] = 600  # 10 seconds
                elif power_up.type == 'triple':
                    self.player.power_ups['triple_shot'] = 600
                
                self.create_explosion(power_up.x + power_up.width//2, 
                                    power_up.y + power_up.height//2, WHITE, 10)
    
    def draw(self):
        # Background
        screen.fill(DARK_BLUE)
        
        # Draw stars
        for star in self.stars:
            star.draw(screen)
        
        # Draw power-ups
        for power_up in self.power_ups:
            power_up.draw(screen, self.frame_count)
        
        # Draw bullets
        for bullet in self.bullets:
            bullet.draw(screen)
        
        # Draw enemies
        for enemy in self.enemies:
            enemy.draw(screen, self.frame_count)
        
        # Draw player
        self.player.draw(screen, self.frame_count)
        
        # Draw particles
        for particle in self.particles:
            particle.draw(screen)
        
        # Draw UI
        self.draw_ui()
        
        # Draw pause or game over screen
        if self.paused:
            self.draw_pause_screen()
        elif self.game_over:
            self.draw_game_over_screen()
    
    def draw_ui(self):
        # Health bar
        pygame.draw.rect(screen, DARK_BLUE, pygame.Rect(10, 10, 200, 25), border_radius=5)
        pygame.draw.rect(screen, RED, pygame.Rect(10, 10, 200, 25), 2, border_radius=5)
        health_width = int(196 * (self.player.health / self.player.max_health))
        health_color = GREEN if self.player.health > 50 else (YELLOW if self.player.health > 25 else RED)
        pygame.draw.rect(screen, health_color, pygame.Rect(12, 12, health_width, 21), border_radius=3)
        draw_text('HP', font_small, WHITE, 15, 12)
        
        # Shield bar
        pygame.draw.rect(screen, DARK_BLUE, pygame.Rect(10, 40, 200, 20), border_radius=5)
        pygame.draw.rect(screen, CYAN, pygame.Rect(10, 40, 200, 20), 2, border_radius=5)
        shield_width = int(196 * (self.player.shield / self.player.max_shield))
        pygame.draw.rect(screen, CYAN, pygame.Rect(12, 42, shield_width, 16), border_radius=3)
        draw_text('SHIELD', font_small, WHITE, 15, 42)
        
        # Score
        draw_text(f'SCORE: {self.score}', font_medium, YELLOW, WIDTH - 10, 15, center=False)
        draw_text(f'LEVEL: {self.level}', font_small, CYAN, WIDTH - 10, 50, center=False)
        draw_text(f'HIGH: {self.high_score}', font_small, WHITE, WIDTH - 10, 75, center=False)
        
        # Weapon level
        weapon_text = f'WEAPON: {"★" * self.player.weapon_level}'
        draw_text(weapon_text, font_small, ORANGE, 10, 70)
        
        # Active power-ups
        power_y = 95
        if self.player.power_ups['rapid_fire'] > 0:
            draw_text(f'RAPID: {self.player.power_ups["rapid_fire"]//60}s', font_small, ORANGE, 10, power_y)
            power_y += 20
        if self.player.power_ups['triple_shot'] > 0:
            draw_text(f'TRIPLE: {self.player.power_ups["triple_shot"]//60}s', font_small, MAGENTA, 10, power_y)
            power_y += 20
    
    def draw_pause_screen(self):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        screen.blit(overlay, (0, 0))
        
        draw_text('PAUSED', font_xlarge, RED, WIDTH//2, HEIGHT//2 - 50, center=True)
        draw_text('Press P to Resume', font_medium, WHITE, WIDTH//2, HEIGHT//2 + 30, center=True)
        draw_text('Press Q to Quit', font_medium, WHITE, WIDTH//2, HEIGHT//2 + 80, center=True)
    
    def draw_game_over_screen(self):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))
        
        draw_text('GAME OVER', font_xlarge, RED, WIDTH//2, HEIGHT//2 - 100, center=True)
        draw_text(f'Final Score: {self.score}', font_large, YELLOW, WIDTH//2, HEIGHT//2 - 20, center=True)
        draw_text(f'Level Reached: {self.level}', font_medium, CYAN, WIDTH//2, HEIGHT//2 + 40, center=True)
        draw_text(f'High Score: {self.high_score}', font_medium, WHITE, WIDTH//2, HEIGHT//2 + 80, center=True)
        draw_text('Press R to Restart', font_medium, WHITE, WIDTH//2, HEIGHT//2 + 140, center=True)
        draw_text('Press Q to Quit', font_medium, WHITE, WIDTH//2, HEIGHT//2 + 180, center=True)
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    self.paused = not self.paused
                if event.key == pygame.K_q:
                    return False
                if event.key == pygame.K_r and self.game_over:
                    return 'restart'
        return True
    
    def reset(self):
        self.player = Player()
        self.bullets = []
        self.enemies = []
        self.particles = []
        self.power_ups = []
        self.score = 0
        self.level = 1
        self.enemies_destroyed = 0
        self.boss_spawned = False
        self.game_over = False
        self.paused = False
        self.frame_count = 0
        self.spawn_timer = 0
        self.difficulty = 1

def draw_text(text, font, color, x, y, center=False):
    """Draw text with shadow"""
    text_surface = font.render(str(text), True, color)
    text_rect = text_surface.get_rect()
    if center:
        text_rect.center = (x, y)
    else:
        text_rect.topleft = (x, y)
    
    # Shadow
    shadow_surface = font.render(str(text), True, BLACK)
    shadow_rect = text_rect.copy()
    shadow_rect.x += 2
    shadow_rect.y += 2
    screen.blit(shadow_surface, shadow_rect)
    
    screen.blit(text_surface, text_rect)

def intro_screen():
    """Game introduction screen"""
    stars = [Star() for _ in range(100)]
    intro = True
    title_pulse = 0
    
    while intro:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    intro = False
                if event.key == pygame.K_q:
                    pygame.quit()
                    sys.exit()
        
        screen.fill(DARK_BLUE)
        
        # Update and draw stars
        for star in stars:
            star.update(2)
            star.draw(screen)
        
        # Animated title
        title_pulse += 0.08
        glow_size = int(5 + 4 * math.sin(title_pulse))
        
        for i in range(glow_size, 0, -1):
            glow_r = min(255, 100 + i * 30)
            glow_g = min(255, 150 + i * 20)
            glow_b = 255
            glow_color = (glow_r, glow_g, glow_b)
            draw_text("SPACE DESTROYER", font_xlarge, glow_color, 
                     WIDTH//2, 150 - i*2, center=True)
        
        draw_text("SPACE DESTROYER", font_xlarge, CYAN, WIDTH//2, 150, center=True)
        draw_text("⚡ Advanced Edition ⚡", font_medium, YELLOW, WIDTH//2, 230, center=True)
        
        # Instructions box
        pygame.draw.rect(screen, DARK_BLUE, pygame.Rect(150, 280, 600, 320), border_radius=15)
        pygame.draw.rect(screen, NEON_BLUE, pygame.Rect(150, 280, 600, 320), 3, border_radius=15)
        
        instructions = [
            ("CONTROLS:", YELLOW),
            ("Arrow Keys / WASD - Move Ship", WHITE),
            ("SPACE - Shoot", CYAN),
            ("P - Pause Game", WHITE),
            ("", WHITE),
            ("POWER-UPS:", GREEN),
            ("+ Green - Health Boost", GREEN),
            ("S Cyan - Shield Boost", CYAN),
            ("W Yellow - Weapon Upgrade", YELLOW),
            ("R Orange - Rapid Fire", ORANGE),
            ("3 Magenta - Triple Shot", MAGENTA),
            ("", WHITE),
            ("Press ENTER or SPACE to Start", YELLOW),
        ]
        
        for i, (line, color) in enumerate(instructions):
            draw_text(line, font_small, color, WIDTH//2, 305 + i*23, center=True)
        
        pygame.display.update()
        clock.tick(FPS)

def main():
    """Main game function"""
    intro_screen()
    
    game = Game()
    running = True
    
    while running:
        result = game.handle_events()
        if result == False:
            running = False
        elif result == 'restart':
            game.reset()
        
        game.update()
        game.draw()
        
        pygame.display.update()
        clock.tick(FPS)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    print("🚀 Starting Space Destroyer...")
    print("Controls: Arrow Keys/WASD to move, SPACE to shoot, P to pause")
    main()