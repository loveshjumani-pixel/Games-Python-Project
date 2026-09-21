import pygame
import sys
import random
import math

# --- INITIALIZATION ---
pygame.init()

# Screen settings
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Neon Cyber Runner - Endless")
clock = pygame.time.Clock()
FPS = 60

# Colors (Neon Palette)
BG_COLOR = (10, 5, 25)
GRID_COLOR = (80, 0, 120)
PLAYER_COLOR = (0, 255, 255)       # Cyan
OBSTACLE_COLOR = (255, 0, 100)     # Neon Pink
SUN_COLOR = (255, 100, 0)          # Orange
TEXT_COLOR = (255, 255, 255)
PARTICLE_COLORS = [(0, 255, 255), (255, 0, 255), (255, 255, 0)]

# Fonts
font_large = pygame.font.SysFont("consolas", 48, bold=True)
font_medium = pygame.font.SysFont("consolas", 24)

# --- CLASSES ---

class Particle:
    def __init__(self, x, y, color, is_explosion=False):
        self.x = x
        self.y = y
        self.color = color
        self.is_explosion = is_explosion
        
        if is_explosion:
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(2, 8)
            self.vx = math.cos(angle) * speed
            self.vy = math.sin(angle) * speed
            self.size = random.randint(3, 6)
            self.life = random.randint(20, 40)
        else:
            self.vx = random.uniform(-1, 1)
            self.vy = random.uniform(-1, 1)
            self.size = random.randint(2, 4)
            self.life = random.randint(10, 20)
            
        self.max_life = self.life

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.life -= 1
        self.size = max(0, self.size - 0.1)

    def draw(self, surface):
        alpha = int((self.life / self.max_life) * 255)
        # Create a surface for the particle to handle transparency
        s = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
        pygame.draw.circle(s, (*self.color, alpha), (self.size, self.size), int(self.size))
        surface.blit(s, (int(self.x - self.size), int(self.y - self.size)))

    def is_dead(self):
        return self.life <= 0


class Player:
    def __init__(self):
        self.width = 40
        self.height = 40
        self.x = 100
        self.y = HEIGHT - 150 - self.height
        self.ground_y = self.y
        self.vy = 0
        self.gravity = 0.8
        self.jump_strength = -16
        self.is_jumping = False
        self.rotation = 0
        
    def jump(self):
        if not self.is_jumping:
            self.vy = self.jump_strength
            self.is_jumping = True
            # Jump particles
            for _ in range(10):
                particles.append(Particle(self.x + self.width//2, self.y + self.height, random.choice(PARTICLE_COLORS)))

    def update(self):
        # Physics
        self.vy += self.gravity
        self.y += self.vy
        
        if self.y >= self.ground_y:
            self.y = self.ground_y
            self.vy = 0
            self.is_jumping = False
            self.rotation = 0
        else:
            self.rotation += 10  # Spin while in air
            
        # Trail particles
        if random.random() < 0.5:
            particles.append(Particle(self.x, self.y + self.height//2, PLAYER_COLOR))

    def draw(self, surface):
        # Draw player as a glowing diamond/ship
        center = (self.x + self.width//2, self.y + self.height//2)
        
        # Create a surface for rotation
        s = pygame.Surface((self.width * 2, self.height * 2), pygame.SRCALPHA)
        local_center = (self.width, self.height)
        
        # Glow effect (outer)
        points_outer = [
            (local_center[0], local_center[1] - self.height//2 - 5),
            (local_center[0] + self.width//2 + 5, local_center[1]),
            (local_center[0], local_center[1] + self.height//2 + 5),
            (local_center[0] - self.width//2 - 5, local_center[1])
        ]
        pygame.draw.polygon(s, (*PLAYER_COLOR, 50), points_outer)
        
        # Main body
        points_inner = [
            (local_center[0], local_center[1] - self.height//2),
            (local_center[0] + self.width//2, local_center[1]),
            (local_center[0], local_center[1] + self.height//2),
            (local_center[0] - self.width//2, local_center[1])
        ]
        pygame.draw.polygon(s, PLAYER_COLOR, points_inner)
        pygame.draw.polygon(s, (255, 255, 255), points_inner, 2)
        
        # Rotate
        rotated_s = pygame.transform.rotate(s, self.rotation)
        new_rect = rotated_s.get_rect(center=center)
        surface.blit(rotated_s, new_rect.topleft)

    def get_rect(self):
        # Slightly smaller hitbox for better game feel
        return pygame.Rect(self.x + 5, self.y + 5, self.width - 10, self.height - 10)


class Obstacle:
    def __init__(self, speed):
        self.width = random.randint(30, 50)
        self.height = random.randint(40, 80)
        self.x = WIDTH + 50
        self.y = HEIGHT - 150 - self.height
        self.speed = speed
        self.passed = False

    def update(self):
        self.x -= self.speed

    def draw(self, surface):
        rect = pygame.Rect(self.x, self.y, self.width, self.height)
        # Glow
        glow_rect = rect.inflate(10, 10)
        pygame.draw.rect(surface, (*OBSTACLE_COLOR, 30), glow_rect, border_radius=5)
        # Main
        pygame.draw.rect(surface, OBSTACLE_COLOR, rect, border_radius=3)
        pygame.draw.rect(surface, (255, 255, 255), rect, 2, border_radius=3)
        
        # Inner detail
        inner_rect = rect.inflate(-10, -10)
        pygame.draw.rect(surface, (150, 0, 50), inner_rect, border_radius=2)

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)
        
    def is_offscreen(self):
        return self.x + self.width < 0


class Background:
    def __init__(self):
        self.stars = [[random.randint(0, WIDTH), random.randint(0, HEIGHT//2), random.randint(1, 3)] for _ in range(100)]
        self.grid_offset = 0
        self.sun_y = HEIGHT // 2 - 50

    def update(self, speed):
        # Parallax stars
        for star in self.stars:
            star[0] -= speed * 0.2
            if star[0] < 0:
                star[0] = WIDTH
                star[1] = random.randint(0, HEIGHT//2)
                
        # Scrolling grid
        self.grid_offset = (self.grid_offset + speed) % 50

    def draw(self, surface):
        # Sky gradient (simple dark to purple)
        for i in range(HEIGHT // 2):
            color_val = int(10 + (i / (HEIGHT // 2)) * 40)
            pygame.draw.line(surface, (color_val, 0, color_val * 2), (0, i), (WIDTH, i))
            
        # Sun
        pygame.draw.circle(surface, SUN_COLOR, (WIDTH // 2, self.sun_y), 80)
        # Sun lines (synthwave style)
        for i in range(5):
            y_pos = self.sun_y + 20 + i * 15
            pygame.draw.line(surface, BG_COLOR, (WIDTH // 2 - 80, y_pos), (WIDTH // 2 + 80, y_pos), 4)

        # Stars
        for star in self.stars:
            pygame.draw.circle(surface, (255, 255, 255), (int(star[0]), int(star[1])), star[2])

        # Ground
        pygame.draw.rect(surface, (20, 0, 40), (0, HEIGHT - 150, WIDTH, 150))
        
        # Perspective Grid on ground
        ground_top = HEIGHT - 150
        # Horizontal lines
        for i in range(6):
            y = ground_top + i * 30
            pygame.draw.line(surface, GRID_COLOR, (0, y), (WIDTH, y), 2)
            
        # Vertical lines (scrolling)
        for i in range(-1, int(WIDTH / 50) + 2):
            x = i * 50 - self.grid_offset
            pygame.draw.line(surface, GRID_COLOR, (x, ground_top), (x, HEIGHT), 2)


# --- GAME STATE ---
def reset_game():
    global player, obstacles, particles, score, high_score, game_speed, game_state, spawn_timer, bg
    player = Player()
    obstacles = []
    particles = []
    score = 0
    game_speed = 6
    spawn_timer = 0
    bg = Background()
    # high_score persists

high_score = 0
game_state = "MENU" # MENU, PLAYING, GAMEOVER
reset_game()

# --- MAIN LOOP ---
running = True
while running:
    screen.fill(BG_COLOR)
    
    # Event Handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
        if event.type == pygame.KEYDOWN:
            if game_state == "MENU":
                if event.key == pygame.K_SPACE:
                    game_state = "PLAYING"
                    reset_game()
            elif game_state == "PLAYING":
                if event.key == pygame.K_SPACE or event.key == pygame.K_UP:
                    player.jump()
            elif game_state == "GAMEOVER":
                if event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                    game_state = "PLAYING"
                    reset_game()

    if game_state == "MENU":
        bg.update(2)
        bg.draw(screen)
        
        title_text = font_large.render("NEON CYBER RUNNER", True, PLAYER_COLOR)
        sub_text = font_medium.render("Press SPACE to Start", True, TEXT_COLOR)
        
        screen.blit(title_text, (WIDTH//2 - title_text.get_width()//2, HEIGHT//3))
        screen.blit(sub_text, (WIDTH//2 - sub_text.get_width()//2, HEIGHT//2))
        
    elif game_state == "PLAYING":
        # Update
        bg.update(game_speed)
        player.update()
        
        spawn_timer += 1
        # Dynamic spawn rate based on speed
        spawn_threshold = max(40, 90 - int(game_speed * 2)) 
        if spawn_timer > spawn_threshold:
            spawn_timer = 0
            obstacles.append(Obstacle(game_speed))
            
        for obs in obstacles:
            obs.update()
            
        # Collision & Scoring
        player_rect = player.get_rect()
        for obs in obstacles:
            if player_rect.colliderect(obs.get_rect()):
                game_state = "GAMEOVER"
                if score > high_score:
                    high_score = score
                # Explosion particles
                for _ in range(50):
                    particles.append(Particle(player.x + player.width//2, player.y + player.height//2, random.choice(PARTICLE_COLORS), is_explosion=True))
                    
            if not obs.passed and obs.x + obs.width < player.x:
                obs.passed = True
                score += 10
                
        # Increase speed over time
        game_speed += 0.002
        
        # Update particles
        for p in particles:
            p.update()
        particles = [p for p in particles if not p.is_dead()]
        
        # Remove offscreen obstacles
        obstacles = [obs for obs in obstacles if not obs.is_offscreen()]
        
        # Draw
        bg.draw(screen)
        for obs in obstacles:
            obs.draw(screen)
        player.draw(screen)
        for p in particles:
            p.draw(screen)
            
        # UI
        score_text = font_medium.render(f"SCORE: {score}", True, TEXT_COLOR)
        screen.blit(score_text, (20, 20))
        
    elif game_state == "GAMEOVER":
        # Keep drawing the last frame (background, etc)
        bg.draw(screen)
        for obs in obstacles:
            obs.draw(screen)
            
        # Update and draw explosion particles
        for p in particles:
            p.update()
            p.draw(screen)
        particles = [p for p in particles if not p.is_dead()]
        
        # Overlay
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        screen.blit(overlay, (0, 0))
        
        go_text = font_large.render("GAME OVER", True, OBSTACLE_COLOR)
        score_text = font_medium.render(f"Score: {score}  |  High Score: {high_score}", True, TEXT_COLOR)
        restart_text = font_medium.render("Press SPACE to Restart", True, PLAYER_COLOR)
        
        screen.blit(go_text, (WIDTH//2 - go_text.get_width()//2, HEIGHT//3))
        screen.blit(score_text, (WIDTH//2 - score_text.get_width()//2, HEIGHT//2 - 20))
        screen.blit(restart_text, (WIDTH//2 - restart_text.get_width()//2, HEIGHT//2 + 30))

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()