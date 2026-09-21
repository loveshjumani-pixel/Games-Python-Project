import pygame
import random
import sys
import math

# Initialize Pygame
pygame.init()

# Screen Settings
DISPLAY_WIDTH = 900
DISPLAY_HEIGHT = 700
FPS = 60

# Colors (Neon Theme)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (40, 40, 40)
DARK_GRAY = (20, 20, 20)
RED = (255, 50, 50)
GREEN = (50, 255, 50)
BLUE = (50, 150, 255)
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
ORANGE = (255, 165, 0)
PURPLE = (180, 0, 255)
DARK_BLUE = (10, 10, 50)
NEON_BLUE = (100, 200, 255)
NEON_PINK = (255, 100, 200)

# Initialize display
gameDisplay = pygame.display.set_mode((DISPLAY_WIDTH, DISPLAY_HEIGHT))
pygame.display.set_caption('🏎️ Neon Speed Racer - Pro Edition')
clock = pygame.time.Clock()

# Fonts
font_small = pygame.font.SysFont('arial', 22, bold=True)
font_medium = pygame.font.SysFont('arial', 36, bold=True)
font_large = pygame.font.SysFont('arial', 60, bold=True)
font_xlarge = pygame.font.SysFont('arial', 90, bold=True)

# Car Settings
car_width = 55
car_height = 95

class Particle:
    """Particle effects for boost and explosions"""
    def __init__(self, x, y, color, speed_x, speed_y, lifetime):
        self.x = x
        self.y = y
        self.color = color
        self.speed_x = speed_x
        self.speed_y = speed_y
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.size = random.randint(3, 8)
    
    def update(self):
        self.x += self.speed_x
        self.y += self.speed_y
        self.lifetime -= 1
        self.size = max(1, self.size - 0.15)
    
    def draw(self, surface):
        if self.lifetime > 0:
            alpha = int(255 * (self.lifetime / self.max_lifetime))
            color_with_alpha = (self.color[0], self.color[1], self.color[2], alpha)
            s = pygame.Surface((int(self.size*2), int(self.size*2)), pygame.SRCALPHA)
            pygame.draw.circle(s, color_with_alpha, (int(self.size), int(self.size)), int(self.size))
            surface.blit(s, (int(self.x - self.size), int(self.y - self.size)))

class Car:
    """Player car with advanced graphics"""
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = car_width
        self.height = car_height
        self.speed = 0
        self.max_speed = 12
        self.acceleration = 0.2
        self.deceleration = 0.15
        self.color = NEON_BLUE
        self.boost_active = False
        self.boost_timer = 0
        self.tilt = 0  # For turning animation
        
    def move(self, keys):
        # Acceleration
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.speed = min(self.speed + self.acceleration, self.max_speed)
        elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.speed = max(self.speed - self.acceleration, -self.max_speed/2)
        else:
            # Natural deceleration
            if self.speed > 0:
                self.speed = max(self.speed - self.deceleration, 0)
            elif self.speed < 0:
                self.speed = min(self.speed + self.deceleration, 0)
        
        # Horizontal movement with tilt
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.x -= 6
            self.tilt = max(self.tilt - 0.5, -3)
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.x += 6
            self.tilt = min(self.tilt + 0.5, 3)
        else:
            self.tilt *= 0.9  # Return to center
        
        # Boost
        if keys[pygame.K_LSHIFT] and self.boost_timer > 0:
            self.boost_active = True
            self.speed = min(self.speed + 0.4, self.max_speed * 1.6)
            self.boost_timer -= 1
        else:
            self.boost_active = False
        
        # Keep car on screen
        self.x = max(120, min(DISPLAY_WIDTH - 120 - self.width, self.x))
        
    def draw(self, surface):
        # Car body color
        car_color = CYAN if self.boost_active else self.color
        
        # Glow effect (multiple layers)
        for i in range(4, 0, -1):
            glow_alpha = 40 // i
            glow_rect = pygame.Surface((self.width + i*6, self.height + i*6), pygame.SRCALPHA)
            glow_color = (car_color[0], car_color[1], car_color[2], glow_alpha)
            pygame.draw.rect(glow_rect, glow_color, 
                           pygame.Rect(0, 0, self.width + i*6, self.height + i*6), 
                           border_radius=18)
            surface.blit(glow_rect, (self.x - i*3, self.y - i*3))
        
        # Main car body
        body_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        pygame.draw.rect(surface, car_color, body_rect, border_radius=15)
        
        # Car body gradient effect (darker edges)
        pygame.draw.rect(surface, (car_color[0]//2, car_color[1]//2, car_color[2]//2), 
                        pygame.Rect(self.x + 5, self.y + 5, self.width - 10, self.height - 10), 
                        border_radius=12)
        
        # Windshield (front)
        windshield_points = [
            (self.x + 8, self.y + 15),
            (self.x + self.width - 8, self.y + 15),
            (self.x + self.width - 12, self.y + 40),
            (self.x + 12, self.y + 40)
        ]
        pygame.draw.polygon(surface, (20, 20, 60), windshield_points)
        pygame.draw.polygon(surface, (40, 40, 100), windshield_points, 2)
        
        # Rear window
        rear_points = [
            (self.x + 12, self.y + 65),
            (self.x + self.width - 12, self.y + 65),
            (self.x + self.width - 8, self.y + 82),
            (self.x + 8, self.y + 82)
        ]
        pygame.draw.polygon(surface, (20, 20, 60), rear_points)
        
        # Racing stripe (center)
        stripe_width = 8
        pygame.draw.rect(surface, WHITE, 
                        pygame.Rect(self.x + self.width//2 - stripe_width//2, 
                                   self.y + 5, stripe_width, self.height - 10))
        
        # Side stripes
        pygame.draw.rect(surface, RED, 
                        pygame.Rect(self.x + 3, self.y + 20, 4, 40))
        pygame.draw.rect(surface, RED, 
                        pygame.Rect(self.x + self.width - 7, self.y + 20, 4, 40))
        
        # Headlights (front - top)
        pygame.draw.circle(surface, (255, 255, 200), 
                          (int(self.x + 12), int(self.y + 8)), 7)
        pygame.draw.circle(surface, (255, 255, 200), 
                          (int(self.x + self.width - 12), int(self.y + 8)), 7)
        
        # Headlight glow
        for i in range(2):
            pygame.draw.circle(surface, (255, 255, 150, 100), 
                              (int(self.x + 12), int(self.y + 8)), 10 + i*3)
            pygame.draw.circle(surface, (255, 255, 150, 100), 
                              (int(self.x + self.width - 12), int(self.y + 8)), 10 + i*3)
        
        # Taillights (rear - bottom)
        pygame.draw.circle(surface, RED, 
                          (int(self.x + 10), int(self.y + self.height - 8)), 6)
        pygame.draw.circle(surface, RED, 
                          (int(self.x + self.width - 10), int(self.y + self.height - 8)), 6)
        
        # Wheels
        wheel_color = (30, 30, 30)
        wheel_width = 8
        # Front wheels
        pygame.draw.rect(surface, wheel_color, 
                        pygame.Rect(self.x - 6, self.y + 12, wheel_width, 22), border_radius=3)
        pygame.draw.rect(surface, wheel_color, 
                        pygame.Rect(self.x + self.width - 2, self.y + 12, wheel_width, 22), border_radius=3)
        # Rear wheels
        pygame.draw.rect(surface, wheel_color, 
                        pygame.Rect(self.x - 6, self.y + 55, wheel_width, 22), border_radius=3)
        pygame.draw.rect(surface, wheel_color, 
                        pygame.Rect(self.x + self.width - 2, self.y + 55, wheel_width, 22), border_radius=3)
        
        # Boost flame effect
        if self.boost_active:
            flame_height = random.randint(25, 45)
            flame_points = [
                (self.x + 12, self.y + self.height),
                (self.x + self.width - 12, self.y + self.height),
                (self.x + self.width//2, self.y + self.height + flame_height)
            ]
            pygame.draw.polygon(surface, ORANGE, flame_points)
            
            inner_flame = [
                (self.x + 18, self.y + self.height),
                (self.x + self.width - 18, self.y + self.height),
                (self.x + self.width//2, self.y + self.height + flame_height//2)
            ]
            pygame.draw.polygon(surface, YELLOW, inner_flame)
    
    def get_rect(self):
        return pygame.Rect(self.x + 5, self.y + 5, self.width - 10, self.height - 10)

class EnemyCar:
    """Enemy traffic cars with different designs"""
    def __init__(self, x, y, speed):
        self.x = x
        self.y = y
        self.width = car_width
        self.height = car_height
        self.speed = speed
        self.colors = [RED, ORANGE, MAGENTA, PURPLE, (0, 200, 100), (255, 100, 0)]
        self.color = random.choice(self.colors)
        self.design = random.randint(0, 2)  # Different car designs
        
    def move(self, road_speed):
        self.y += self.speed + road_speed
        
    def draw(self, surface):
        # Enemy car body
        body_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        pygame.draw.rect(surface, self.color, body_rect, border_radius=12)
        
        # Darker inner body
        pygame.draw.rect(surface, (self.color[0]//2, self.color[1]//2, self.color[2]//2), 
                        pygame.Rect(self.x + 5, self.y + 5, self.width - 10, self.height - 10), 
                        border_radius=10)
        
        if self.design == 0:
            # Sport car design
            pygame.draw.rect(surface, BLACK, 
                            pygame.Rect(self.x + 8, self.y + 20, self.width - 16, 25), border_radius=5)
            pygame.draw.rect(surface, BLACK, 
                            pygame.Rect(self.x + 10, self.y + 60, self.width - 20, 20), border_radius=5)
        elif self.design == 1:
            # SUV design
            pygame.draw.rect(surface, BLACK, 
                            pygame.Rect(self.x + 6, self.y + 15, self.width - 12, 35), border_radius=5)
        else:
            # Truck design
            pygame.draw.rect(surface, BLACK, 
                            pygame.Rect(self.x + 5, self.y + 10, self.width - 10, 50), border_radius=5)
        
        # Headlights (facing down since they come towards player)
        pygame.draw.circle(surface, YELLOW, 
                          (int(self.x + 12), int(self.y + self.height - 8)), 6)
        pygame.draw.circle(surface, YELLOW, 
                          (int(self.x + self.width - 12), int(self.y + self.height - 8)), 6)
        
        # Taillights (top)
        pygame.draw.circle(surface, (200, 0, 0), 
                          (int(self.x + 10), int(self.y + 8)), 5)
        pygame.draw.circle(surface, (200, 0, 0), 
                          (int(self.x + self.width - 10), int(self.y + 8)), 5)
    
    def get_rect(self):
        return pygame.Rect(self.x + 5, self.y + 5, self.width - 10, self.height - 10)

class PowerUp:
    """Power-up items with rotation animation"""
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 45
        self.height = 45
        self.types = ['boost', 'shield', 'score']
        self.type = random.choice(self.types)
        self.angle = 0
        self.pulse = 0
        
    def move(self, speed):
        self.y += speed
        self.angle += 3
        self.pulse += 0.1
        
    def draw(self, surface):
        # Pulsing glow effect
        pulse_size = int(5 + 3 * math.sin(self.pulse))
        
        if self.type == 'boost':
            color = ORANGE
            symbol = 'B'
        elif self.type == 'shield':
            color = CYAN
            symbol = 'S'
        else:
            color = GREEN
            symbol = '+'
        
        # Outer glow
        glow_rect = pygame.Surface((self.width + pulse_size*2, self.height + pulse_size*2), pygame.SRCALPHA)
        glow_color = (color[0], color[1], color[2], 80)
        pygame.draw.circle(glow_rect, glow_color, 
                          (int((self.width + pulse_size*2)//2), int((self.height + pulse_size*2)//2)), 
                          int((self.width + pulse_size*2)//2))
        surface.blit(glow_rect, (self.x - pulse_size, self.y - pulse_size))
        
        # Main circle
        center_x = int(self.x + self.width//2)
        center_y = int(self.y + self.height//2)
        pygame.draw.circle(surface, color, (center_x, center_y), 22, 3)
        pygame.draw.circle(surface, (color[0]//2, color[1]//2, color[2]//2), 
                          (center_x, center_y), 20)
        
        # Symbol
        text = font_small.render(symbol, True, WHITE)
        text_rect = text.get_rect(center=(center_x, center_y))
        surface.blit(text, text_rect)
    
    def get_rect(self):
        return pygame.Rect(self.x + 5, self.y + 5, self.width - 10, self.height - 10)

class Road:
    """Animated road with neon effects"""
    def __init__(self):
        self.y_offset = 0
        self.lane_markers = []
        for i in range(-100, DISPLAY_HEIGHT + 200, 80):
            self.lane_markers.append(i)
            
    def update(self, speed):
        self.y_offset += speed
        if self.y_offset >= 80:
            self.y_offset -= 80
            
    def draw(self, surface):
        # Road background with gradient
        for y in range(0, DISPLAY_HEIGHT, 5):
            shade = int(30 + (y / DISPLAY_HEIGHT) * 20)
            pygame.draw.line(surface, (shade, shade, shade + 10), 
                           (100, y), (DISPLAY_WIDTH - 100, y))
        
        # Road borders (neon glowing)
        for i in range(3):
            alpha = 255 - i * 60
            border_color = (min(255, 100 + i*50), min(255, 150 + i*30), 255)
            pygame.draw.rect(surface, border_color, 
                           pygame.Rect(95 - i*2, 0, 5 + i*4, DISPLAY_HEIGHT))
            pygame.draw.rect(surface, (255, min(255, 100 + i*50), min(255, 150 + i*30)), 
                           pygame.Rect(DISPLAY_WIDTH - 100 - i*2, 0, 5 + i*4, DISPLAY_HEIGHT))
        
        # Animated lane markers
        for marker_y in self.lane_markers:
            adjusted_y = marker_y + self.y_offset
            if adjusted_y > DISPLAY_HEIGHT + 100:
                adjusted_y -= DISPLAY_HEIGHT + 300
            
            # Center line (dashed)
            pygame.draw.rect(surface, WHITE, 
                           pygame.Rect(DISPLAY_WIDTH//2 - 4, adjusted_y, 8, 40))
            
            # Lane dividers
            pygame.draw.rect(surface, (100, 100, 100), 
                           pygame.Rect(DISPLAY_WIDTH//2 - 180, adjusted_y, 4, 40))
            pygame.draw.rect(surface, (100, 100, 100), 
                           pygame.Rect(DISPLAY_WIDTH//2 + 176, adjusted_y, 4, 40))
        
        # Side neon lights
        for i in range(0, DISPLAY_HEIGHT, 120):
            pos = (i + int(self.y_offset)) % (DISPLAY_HEIGHT + 120) - 60
            # Left side lights
            pygame.draw.rect(surface, NEON_BLUE, pygame.Rect(75, pos, 12, 50), border_radius=3)
            pygame.draw.rect(surface, (50, 100, 150), pygame.Rect(77, pos + 5, 8, 40), border_radius=2)
            # Right side lights
            pygame.draw.rect(surface, NEON_PINK, pygame.Rect(DISPLAY_WIDTH - 87, pos, 12, 50), border_radius=3)
            pygame.draw.rect(surface, (150, 50, 100), pygame.Rect(DISPLAY_WIDTH - 85, pos + 5, 8, 40), border_radius=2)

def draw_background():
    """Draw animated background with grid effect"""
    # Dark background
    gameDisplay.fill(DARK_BLUE)
    
    # Grid effect (perspective)
    for x in range(0, DISPLAY_WIDTH, 60):
        pygame.draw.line(gameDisplay, (25, 25, 70), (x, 0), (x, DISPLAY_HEIGHT), 1)
    for y in range(0, DISPLAY_HEIGHT, 60):
        pygame.draw.line(gameDisplay, (25, 25, 70), (0, y), (DISPLAY_WIDTH, y), 1)
    
    # Vignette effect (darker edges)
    vignette = pygame.Surface((DISPLAY_WIDTH, DISPLAY_HEIGHT), pygame.SRCALPHA)
    for i in range(50):
        alpha = i * 2
        pygame.draw.rect(vignette, (0, 0, 0, alpha), 
                        pygame.Rect(i, i, DISPLAY_WIDTH - i*2, DISPLAY_HEIGHT - i*2), 1)
    gameDisplay.blit(vignette, (0, 0))

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
    gameDisplay.blit(shadow_surface, shadow_rect)
    
    gameDisplay.blit(text_surface, text_rect)

def intro_screen():
    """Game introduction screen"""
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
        
        draw_background()
        
        # Animated title
        title_pulse += 0.08
        glow_size = int(5 + 4 * math.sin(title_pulse))
        
        # Title with glow effect
        for i in range(glow_size, 0, -1):
            glow_r = min(255, 50 + i * 40)
            glow_g = min(255, 100 + i * 30)
            glow_b = 255
            glow_color = (glow_r, glow_g, glow_b)
            draw_text("NEON SPEED RACER", font_xlarge, glow_color, 
                     DISPLAY_WIDTH//2, 120 - i*2, center=True)
        
        draw_text("NEON SPEED RACER", font_xlarge, CYAN, 
                 DISPLAY_WIDTH//2, 120, center=True)
        
        # Subtitle
        draw_text("⚡ Pro Edition ⚡", font_medium, YELLOW, 
                 DISPLAY_WIDTH//2, 210, center=True)
        
        # Instructions box
        pygame.draw.rect(gameDisplay, DARK_BLUE, 
                        pygame.Rect(200, 260, 500, 320), border_radius=15)
        pygame.draw.rect(gameDisplay, NEON_BLUE, 
                        pygame.Rect(200, 260, 500, 320), 3, border_radius=15)
        
        instructions = [
            ("CONTROLS:", YELLOW),
            ("↑↓ or W/S - Accelerate/Brake", WHITE),
            ("←→ or A/D - Steer Left/Right", WHITE),
            ("LEFT SHIFT - Speed Boost", ORANGE),
            ("P or ESC - Pause Game", WHITE),
            ("", WHITE),
            ("POWER-UPS:", CYAN),
            ("B (Orange) - Speed Boost", ORANGE),
            ("S (Cyan) - Shield Protection", CYAN),
            ("+ (Green) - Bonus Points", GREEN),
            ("", WHITE),
            ("Press ENTER or SPACE to Start", YELLOW),
        ]
        
        for i, (line, color) in enumerate(instructions):
            draw_text(line, font_small, color, DISPLAY_WIDTH//2, 285 + i*25, center=True)
        
        pygame.display.update()
        clock.tick(FPS)

def pause_screen():
    """Pause menu"""
    paused = True
    
    while paused:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p or event.key == pygame.K_ESCAPE:
                    paused = False
                if event.key == pygame.K_q:
                    pygame.quit()
                    sys.exit()
        
        # Darken background
        dark_overlay = pygame.Surface((DISPLAY_WIDTH, DISPLAY_HEIGHT), pygame.SRCALPHA)
        dark_overlay.fill((0, 0, 0, 150))
        gameDisplay.blit(dark_overlay, (0, 0))
        
        draw_text("PAUSED", font_xlarge, RED, DISPLAY_WIDTH//2, 250, center=True)
        draw_text("Press P to Resume", font_medium, WHITE, DISPLAY_WIDTH//2, 360, center=True)
        draw_text("Press Q to Quit", font_medium, WHITE, DISPLAY_WIDTH//2, 420, center=True)
        
        pygame.display.update()
        clock.tick(FPS)

def game_over_screen(score, high_score):
    """Game over screen"""
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    return True  # Restart
                if event.key == pygame.K_q:
                    pygame.quit()
                    sys.exit()
        
        draw_background()
        
        draw_text("GAME OVER", font_xlarge, RED, DISPLAY_WIDTH//2, 180, center=True)
        draw_text(f"Score: {score}", font_large, YELLOW, DISPLAY_WIDTH//2, 300, center=True)
        draw_text(f"High Score: {high_score}", font_medium, CYAN, DISPLAY_WIDTH//2, 380, center=True)
        draw_text("Press R to Restart", font_medium, WHITE, DISPLAY_WIDTH//2, 470, center=True)
        draw_text("Press Q to Quit", font_medium, WHITE, DISPLAY_WIDTH//2, 530, center=True)
        
        pygame.display.update()
        clock.tick(FPS)

def game_loop():
    """Main game loop"""
    # Initialize game objects
    player = Car(DISPLAY_WIDTH * 0.45, DISPLAY_HEIGHT * 0.75)
    road = Road()
    
    # Game variables
    enemy_cars = []
    powerups = []
    particles = []
    score = 0
    high_score = 0
    distance = 0
    road_speed = 4
    enemy_speed = 2
    spawn_timer = 0
    powerup_timer = 0
    shield_active = False
    shield_timer = 0
    frame_count = 0
    
    running = True
    
    while running:
        frame_count += 1
        
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p or event.key == pygame.K_ESCAPE:
                    pause_screen()
                if event.key == pygame.K_q:
                    running = False
        
        # Get keys
        keys = pygame.key.get_pressed()
        
        # Update player
        player.move(keys)
        
        # Update road
        current_speed = road_speed + player.speed
        road.update(current_speed)
        
        # Spawn enemies
        spawn_timer += 1
        spawn_rate = max(60, 150 - int(score/50))
        if spawn_timer >= spawn_rate:
            spawn_timer = 0
            lanes = [180, 360, 540, 720]
            lane = random.choice(lanes)
            # Check if lane is clear
            lane_clear = True
            for enemy in enemy_cars:
                if abs(enemy.x - lane) < 60 and enemy.y < 150:
                    lane_clear = False
                    break
            if lane_clear:
                enemy = EnemyCar(lane, -120, enemy_speed)
                enemy_cars.append(enemy)
        
        # Spawn powerups
        powerup_timer += 1
        if powerup_timer >= 500:  # Every ~8 seconds
            powerup_timer = 0
            lanes = [180, 360, 540, 720]
            lane = random.choice(lanes)
            powerup = PowerUp(lane - 20, -80)
            powerups.append(powerup)
        
        # Update enemies
        for enemy in enemy_cars[:]:
            enemy.move(current_speed)
            
            # Check collision with player
            if player.get_rect().colliderect(enemy.get_rect()):
                if shield_active:
                    # Destroy enemy with shield
                    enemy_cars.remove(enemy)
                    shield_active = False
                    # Create explosion particles
                    for _ in range(25):
                        particles.append(Particle(
                            enemy.x + enemy.width//2,
                            enemy.y + enemy.height//2,
                            enemy.color,
                            random.uniform(-6, 6),
                            random.uniform(-6, 6),
                            random.randint(20, 40)
                        ))
                    score += 50
                else:
                    # Game over
                    if score > high_score:
                        high_score = score
                    restart = game_over_screen(score, high_score)
                    if restart:
                        return game_loop()
                    else:
                        return
            elif enemy.y > DISPLAY_HEIGHT + 50:
                if enemy in enemy_cars:
                    enemy_cars.remove(enemy)
                    score += 10
        
        # Update powerups
        for powerup in powerups[:]:
            powerup.move(current_speed)
            
            if player.get_rect().colliderect(powerup.get_rect()):
                if powerup.type == 'boost':
                    player.boost_timer = 300  # 5 seconds at 60 FPS
                elif powerup.type == 'shield':
                    shield_active = True
                    shield_timer = 600  # 10 seconds
                else:  # score
                    score += 100
                if powerup in powerups:
                    powerups.remove(powerup)
                # Collection particles
                for _ in range(15):
                    particles.append(Particle(
                        powerup.x + powerup.width//2,
                        powerup.y + powerup.height//2,
                        (255, 255, 255),
                        random.uniform(-4, 4),
                        random.uniform(-4, 4),
                        random.randint(15, 30)
                    ))
            elif powerup.y > DISPLAY_HEIGHT + 50:
                if powerup in powerups:
                    powerups.remove(powerup)
        
        # Update particles
        for particle in particles[:]:
            particle.update()
            if particle.lifetime <= 0:
                particles.remove(particle)
        
        # Update shield timer
        if shield_active:
            shield_timer -= 1
            if shield_timer <= 0:
                shield_active = False
        
        # Update score and distance
        distance += player.speed * 0.5
        if player.speed > 0:
            score += int(player.speed / 5)
        
        # Increase difficulty gradually
        enemy_speed = 2 + score / 800
        
        # Drawing
        draw_background()
        road.draw(gameDisplay)
        
        # Draw powerups
        for powerup in powerups:
            powerup.draw(gameDisplay)
        
        # Draw enemies
        for enemy in enemy_cars:
            enemy.draw(gameDisplay)
        
        # Draw player
        if not (shield_active and frame_count % 10 < 5):  # Flicker when shield active
            player.draw(gameDisplay)
        
        # Draw shield effect
        if shield_active:
            shield_alpha = int(100 + 50 * math.sin(frame_count * 0.1))
            shield_surface = pygame.Surface((player.width + 30, player.height + 30), pygame.SRCALPHA)
            pygame.draw.circle(shield_surface, (0, 255, 255, shield_alpha), 
                             (int((player.width + 30)//2), int((player.height + 30)//2)), 
                             int((player.width + 30)//2), 3)
            gameDisplay.blit(shield_surface, 
                           (player.x - 15, player.y - 15))
        
        # Draw particles
        for particle in particles:
            particle.draw(gameDisplay)
        
        # Speed lines effect (when boosting or high speed)
        if player.boost_active or player.speed > 8:
            num_lines = 5 if player.boost_active else 2
            for _ in range(num_lines):
                x = random.randint(120, DISPLAY_WIDTH - 120)
                y = random.randint(0, DISPLAY_HEIGHT)
                length = random.randint(40, 100)
                line_alpha = 150 if player.boost_active else 80
                line_surface = pygame.Surface((2, length), pygame.SRCALPHA)
                line_surface.fill((255, 255, 255, line_alpha))
                gameDisplay.blit(line_surface, (x, y))
        
        # Draw UI
        # Score board (top-left)
        pygame.draw.rect(gameDisplay, DARK_BLUE, pygame.Rect(10, 10, 220, 130), border_radius=12)
        pygame.draw.rect(gameDisplay, NEON_BLUE, pygame.Rect(10, 10, 220, 130), 3, border_radius=12)
        
        draw_text(f"SCORE: {score}", font_medium, YELLOW, 25, 20)
        draw_text(f"DIST: {int(distance)}m", font_small, WHITE, 25, 60)
        
        speed_text = f"SPD: {int(player.speed * 15)} km/h"
        speed_color = CYAN if player.boost_active else WHITE
        draw_text(speed_text, font_small, speed_color, 25, 85)
        
        # Boost bar
        boost_max = 300
        boost_width = int(120 * (player.boost_timer / boost_max)) if player.boost_timer > 0 else 0
        pygame.draw.rect(gameDisplay, DARK_GRAY, pygame.Rect(25, 110, 120, 18), border_radius=5)
        if boost_width > 0:
            pygame.draw.rect(gameDisplay, ORANGE, pygame.Rect(25, 110, boost_width, 18), border_radius=5)
        draw_text("BOOST", font_small, WHITE, 155, 112)
        
        # High score (top-right)
        pygame.draw.rect(gameDisplay, DARK_BLUE, pygame.Rect(DISPLAY_WIDTH - 230, 10, 220, 50), border_radius=12)
        pygame.draw.rect(gameDisplay, NEON_PINK, pygame.Rect(DISPLAY_WIDTH - 230, 10, 220, 50), 3, border_radius=12)
        draw_text(f"HIGH: {high_score}", font_medium, CYAN, DISPLAY_WIDTH - 120, 35, center=True)
        
        # Shield indicator
        if shield_active:
            shield_text = f"SHIELD: {shield_timer//60}s"
            draw_text(shield_text, font_small, CYAN, DISPLAY_WIDTH//2, 20, center=True)
        
        # Controls hint (bottom)
        draw_text("SHIFT=Boost | P=Pause", font_small, (150, 150, 150), 
                 DISPLAY_WIDTH//2, DISPLAY_HEIGHT - 30, center=True)
        
        pygame.display.update()
        clock.tick(FPS)

# Main execution
if __name__ == "__main__":
    print("️ Starting Neon Speed Racer...")
    print("Controls: Arrow Keys/WASD to move, SHIFT to boost, P to pause")
    intro_screen()
    game_loop()
    pygame.quit()
    sys.exit()