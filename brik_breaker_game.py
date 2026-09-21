import pygame
import random
import math
import sys
import os

# ==================== INITIALIZATION ====================
pygame.init()

WIDTH, HEIGHT = 900, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Brick Breaker - Ultra Premium")
clock = pygame.time.Clock()
FPS = 60

# ==================== COLORS ====================
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# ==================== FONTS ====================
def get_font(size, bold=False):
    for name in ["consolas", "segoeui", "arial", "dejavusans"]:
        try:
            f = pygame.font.SysFont(name, size, bold=bold)
            if f:
                return f
        except Exception:
            continue
    try:
        return pygame.font.Font(None, size + 10)
    except Exception:
        return pygame.font.Font(pygame.font.get_default_font(), size + 10)

FONT_HUGE = get_font(64, bold=True)
FONT_BIG = get_font(48, bold=True)
FONT_MED = get_font(32, bold=True)
FONT_SMALL = get_font(22)
FONT_TINY = get_font(16)

# ==================== HIGH SCORE ====================
SCORE_FILE = "highscore.txt"

def load_high_score():
    try:
        if os.path.exists(SCORE_FILE):
            with open(SCORE_FILE, "r") as f:
                return int(f.read().strip() or 0)
    except Exception:
        pass
    return 0

def save_high_score(score):
    try:
        with open(SCORE_FILE, "w") as f:
            f.write(str(score))
    except Exception:
        pass

# ==================== UTILITY FUNCTIONS ====================
def draw_gradient_rect(surface, color1, color2, rect, vertical=True):
    x, y, w, h = rect
    if w <= 0 or h <= 0:
        return
    x, y, w, h = int(x), int(y), int(w), int(h)
    if vertical:
        step = max(1, h // 25)
        for i in range(0, h, step):
            ratio = i / max(1, h - 1)
            r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
            g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
            b = int(color1[2] * (1 - ratio) + color2[2] * ratio)
            pygame.draw.rect(surface, (r, g, b), (x, y + i, w, step))
    else:
        step = max(1, w // 25)
        for i in range(0, w, step):
            ratio = i / max(1, w - 1)
            r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
            g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
            b = int(color1[2] * (1 - ratio) + color2[2] * ratio)
            pygame.draw.rect(surface, (r, g, b), (x + i, y, step, h))

def draw_glow(surface, center, radius, color, alpha=100):
    if radius <= 0:
        return
    size = radius * 2
    try:
        glow_surf = pygame.Surface((size, size), pygame.SRCALPHA)
        for i in range(radius, 0, max(1, radius // 5)):
            a = int(alpha * (i / radius))
            pygame.draw.circle(glow_surf, (*color, a), (radius, radius), i)
        surface.blit(glow_surf, (center[0] - radius, center[1] - radius))
    except Exception:
        pass

def draw_text_centered(surface, text, font, color, y_pos, shadow=True):
    try:
        if shadow:
            shadow_txt = font.render(text, True, (0, 0, 0))
            surface.blit(shadow_txt, (WIDTH // 2 - shadow_txt.get_width() // 2 + 3, y_pos + 3))
        txt = font.render(text, True, color)
        surface.blit(txt, (WIDTH // 2 - txt.get_width() // 2, y_pos))
    except Exception:
        pass

def draw_vignette(surface):
    """Draw vignette effect (dark corners)"""
    try:
        vignette = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        for i in range(50):
            alpha = int(100 * (i / 50))
            pygame.draw.rect(vignette, (0, 0, 0, alpha),
                           (i, i, WIDTH - 2*i, HEIGHT - 2*i), 1)
        surface.blit(vignette, (0, 0))
    except Exception:
        pass

# ==================== PARTICLE CLASS ====================
class Particle:
    def __init__(self, x, y, color, size_range=(2, 6), speed_range=(2, 8)):
        self.x = float(x)
        self.y = float(y)
        angle = random.uniform(0, math.pi * 2)
        speed = random.uniform(*speed_range)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.color = color
        self.life = random.randint(25, 50)
        self.max_life = self.life
        self.size = random.randint(*size_range)
        self.rotation = random.uniform(0, math.pi * 2)
        self.rotation_speed = random.uniform(-0.2, 0.2)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.18
        self.vx *= 0.97
        self.life -= 1
        self.rotation += self.rotation_speed

    def draw(self, surface):
        if self.life <= 0:
            return
        ratio = self.life / self.max_life
        size = max(1, int(self.size * ratio))
        try:
            temp = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
            alpha = int(255 * ratio)
            pygame.draw.circle(temp, (*self.color, alpha), (size, size), size)
            surface.blit(temp, (int(self.x) - size, int(self.y) - size))
        except Exception:
            pass

    def is_dead(self):
        return self.life <= 0

# ==================== BALL CLASS ====================
class Ball:
    def __init__(self, x, y, fireball=False):
        self.x = float(x)
        self.y = float(y)
        self.radius = 12
        self.speed = 6
        angle = random.uniform(math.pi * 0.25, math.pi * 0.75)
        direction = 1 if random.random() > 0.5 else -1
        self.vx = math.cos(angle) * self.speed * direction
        self.vy = -math.sin(angle) * self.speed
        self.trail = []
        self.fireball = fireball
        self.fire_timer = 0
        self.pulse = 0

    def update(self):
        self.trail.append((self.x, self.y))
        if len(self.trail) > 15:
            self.trail.pop(0)
        self.x += self.vx
        self.y += self.vy
        self.pulse += 0.15
        if self.fireball:
            self.fire_timer -= 1
            if self.fire_timer <= 0:
                self.fireball = False

    def draw(self, surface):
        try:
            # Enhanced trail with gradient
            trail_color = (255, 150, 50) if self.fireball else (100, 200, 255)
            for i, (tx, ty) in enumerate(self.trail):
                ratio = i / max(1, len(self.trail))
                size = int(self.radius * ratio * 0.8)
                if size < 1:
                    continue
                alpha = int(180 * ratio)
                temp = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
                pygame.draw.circle(temp, (*trail_color, alpha), (size, size), size)
                surface.blit(temp, (int(tx) - size, int(ty) - size))

            # Glow
            glow_color = (255, 120, 50) if self.fireball else (100, 200, 255)
            pulse_size = int(self.radius * 3 + math.sin(self.pulse) * 5)
            draw_glow(surface, (int(self.x), int(self.y)), pulse_size, glow_color, 100)

            # Main ball with 3D effect
            if self.fireball:
                pygame.draw.circle(surface, (255, 220, 100), (int(self.x), int(self.y)), self.radius)
                pygame.draw.circle(surface, (255, 150, 50), (int(self.x), int(self.y)), self.radius - 2)
                pygame.draw.circle(surface, (255, 100, 30), (int(self.x), int(self.y)), self.radius - 4)
            else:
                pygame.draw.circle(surface, WHITE, (int(self.x), int(self.y)), self.radius)
                pygame.draw.circle(surface, (180, 230, 255), (int(self.x), int(self.y)), self.radius - 2)
                pygame.draw.circle(surface, (100, 200, 255), (int(self.x), int(self.y)), self.radius - 4)
            
            # Highlight
            pygame.draw.circle(surface, WHITE, (int(self.x) - 4, int(self.y) - 4), 4)
        except Exception:
            pass

    def get_rect(self):
        return pygame.Rect(self.x - self.radius, self.y - self.radius,
                          self.radius * 2, self.radius * 2)

    def ensure_vertical_speed(self):
        min_vy = self.speed * 0.3
        if abs(self.vy) < min_vy:
            self.vy = min_vy if self.vy >= 0 else -min_vy
            remaining = math.sqrt(max(0, self.speed ** 2 - self.vy ** 2))
            self.vx = remaining if self.vx >= 0 else -remaining

# ==================== PADDLE CLASS ====================
class Paddle:
    def __init__(self):
        self.width = 140
        self.height = 20
        self.x = WIDTH // 2 - self.width // 2
        self.y = HEIGHT - 60
        self.speed = 10
        self.base_width = 140
        self.laser_timer = 0
        self.laser_cooldown = 0
        self.shield_active = False
        self.target_x = None
        self.glow_pulse = 0

    def update(self, keys):
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.x -= self.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.x += self.speed

        if self.target_x is not None:
            target_center = self.target_x
            current_center = self.x + self.width / 2
            diff = target_center - current_center
            if abs(diff) > 2:
                self.x += max(-self.speed * 1.5, min(self.speed * 1.5, diff))

        self.x = max(0, min(WIDTH - self.width, self.x))
        self.glow_pulse += 0.1

        if self.laser_timer > 0:
            self.laser_timer -= 1
        if self.laser_cooldown > 0:
            self.laser_cooldown -= 1

    def draw(self, surface):
        try:
            rect = (self.x, self.y, self.width, self.height)

            # Shield aura
            if self.shield_active:
                pulse = int(80 + math.sin(self.glow_pulse) * 10)
                draw_glow(surface, (int(self.x + self.width / 2),
                                    int(self.y + self.height / 2)),
                          pulse, (100, 255, 200), 80)

            # Laser mode glow
            if self.laser_timer > 0:
                pulse = int(70 + math.sin(self.glow_pulse * 2) * 10)
                draw_glow(surface, (int(self.x + self.width / 2),
                                    int(self.y + self.height / 2)),
                          pulse, (255, 100, 100), 70)

            # Main paddle with 3D gradient
            if self.laser_timer > 0:
                draw_gradient_rect(surface, (255, 100, 100), (200, 50, 150), rect, vertical=False)
            else:
                draw_gradient_rect(surface, (50, 220, 255), (150, 80, 255), rect, vertical=False)

            # Top highlight (3D effect)
            pygame.draw.rect(surface, (220, 250, 255),
                           (self.x + 5, self.y + 2, self.width - 10, 4))
            
            # Bottom shadow
            pygame.draw.rect(surface, (0, 100, 150),
                           (self.x + 5, self.y + self.height - 4, self.width - 10, 3))

            # Side caps with glow
            cap_color = (255, 150, 150) if self.laser_timer > 0 else (150, 220, 255)
            pygame.draw.circle(surface, cap_color,
                             (int(self.x + 8), int(self.y + self.height // 2)), 6)
            pygame.draw.circle(surface, cap_color,
                             (int(self.x + self.width - 8), int(self.y + self.height // 2)), 6)

            # General glow
            draw_glow(surface, (int(self.x + self.width / 2), int(self.y + self.height / 2)),
                      60, (100, 150, 255), 50)
        except Exception:
            pass

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

# ==================== BRICK CLASS ====================
class Brick:
    COLORS = {
        1: [(255, 100, 100), (220, 50, 50), (180, 30, 30)],
        2: [(255, 200, 80), (220, 150, 40), (180, 100, 20)],
        3: [(255, 240, 100), (220, 200, 60), (180, 160, 40)],
        4: [(100, 240, 140), (60, 200, 100), (40, 160, 80)],
        5: [(120, 180, 255), (80, 140, 220), (50, 100, 180)],
    }

    def __init__(self, x, y, w, h, hp=1):
        self.rect = pygame.Rect(x, y, w, h)
        self.hp = hp
        self.max_hp = hp
        self.shake = 0
        self.colors = self.COLORS.get(hp, self.COLORS[1])
        self.anim_offset = random.uniform(0, math.pi * 2)

    def hit(self):
        self.hp -= 1
        self.shake = 6
        self.colors = self.COLORS.get(self.hp, self.COLORS[1])
        return self.hp <= 0

    def draw(self, surface):
        try:
            sx = sy = 0
            if self.shake > 0:
                sx = random.randint(-3, 3)
                sy = random.randint(-3, 3)
                self.shake -= 1
            
            rect = (self.rect.x + sx, self.rect.y + sy, self.rect.width, self.rect.height)
            
            # 3D brick with multiple layers
            # Shadow
            pygame.draw.rect(surface, self.colors[2],
                           (rect[0] + 2, rect[1] + 2, rect[2], rect[3]))
            
            # Main body
            draw_gradient_rect(surface, self.colors[0], self.colors[1], rect)
            
            # Top shine (3D effect)
            pygame.draw.rect(surface, (255, 255, 255),
                           (rect[0] + 4, rect[1] + 3, rect[2] - 8, 4))
            
            # Bottom edge
            pygame.draw.rect(surface, self.colors[2],
                           (rect[0] + 4, rect[1] + rect[3] - 5, rect[2] - 8, 3))
            
            # Border
            pygame.draw.rect(surface, (0, 0, 0), rect, 2)
            
            # Animated shine
            t = pygame.time.get_ticks() / 1000
            shine_x = int(rect[0] + (math.sin(t + self.anim_offset) + 1) * rect[2] / 2)
            pygame.draw.circle(surface, (255, 255, 255, 100), (shine_x, rect[1] + 5), 3)

            # HP indicator
            if self.max_hp > 1:
                txt = FONT_SMALL.render(str(self.hp), True, WHITE)
                surface.blit(txt, (rect[0] + rect[2] // 2 - txt.get_width() // 2,
                                   rect[1] + rect[3] // 2 - txt.get_height() // 2))
        except Exception:
            pass

# ==================== POWERUP CLASS ====================
class PowerUp:
    TYPES = ['wide', 'multi', 'fire', 'life', 'laser', 'shield']
    COLORS = {
        'wide': (0, 255, 150),
        'multi': (255, 100, 200),
        'fire': (255, 150, 50),
        'life': (255, 80, 80),
        'laser': (255, 100, 100),
        'shield': (100, 255, 200),
    }
    ICONS = {'wide': 'W', 'multi': 'M', 'fire': 'F',
             'life': '♥', 'laser': 'L', 'shield': 'S'}

    def __init__(self, x, y, ptype=None):
        self.x = float(x)
        self.y = float(y)
        self.size = 20
        self.vy = 2.5
        self.type = ptype if ptype else random.choice(self.TYPES)
        self.angle = 0
        self.pulse = 0

    def update(self, paddle_x=None, paddle_width=None):
        self.y += self.vy
        self.angle += 0.1
        self.pulse += 0.15
        if paddle_x is not None and paddle_width is not None:
            paddle_center = paddle_x + paddle_width / 2
            dx = paddle_center - self.x
            dy = (HEIGHT - 60) - self.y
            dist = math.hypot(dx, dy)
            if dist < 150 and self.y > HEIGHT // 2 and dist > 1:
                self.x += dx / dist * 1.5
                self.y += dy / dist * 0.8

    def draw(self, surface):
        try:
            color = self.COLORS[self.type]
            pulse_size = int(self.size + math.sin(self.pulse) * 3)
            
            # Glow
            draw_glow(surface, (int(self.x), int(self.y)),
                      pulse_size + 12, color, 100)
            
            # Rotating diamond
            s = pulse_size
            points = [
                (int(self.x), int(self.y - s)),
                (int(self.x + s), int(self.y)),
                (int(self.x), int(self.y + s)),
                (int(self.x - s), int(self.y)),
            ]
            pygame.draw.polygon(surface, color, points)
            pygame.draw.polygon(surface, WHITE, points, 3)
            
            # Inner glow
            inner_s = int(s * 0.6)
            inner_points = [
                (int(self.x), int(self.y - inner_s)),
                (int(self.x + inner_s), int(self.y)),
                (int(self.x), int(self.y + inner_s)),
                (int(self.x - inner_s), int(self.y)),
            ]
            pygame.draw.polygon(surface, (255, 255, 255), inner_points)
            
            # Icon
            icon = FONT_SMALL.render(self.ICONS[self.type], True, color)
            surface.blit(icon, (int(self.x) - icon.get_width() // 2,
                               int(self.y) - icon.get_height() // 2))
        except Exception:
            pass

    def get_rect(self):
        return pygame.Rect(self.x - self.size, self.y - self.size,
                          self.size * 2, self.size * 2)

# ==================== LASER CLASS ====================
class Laser:
    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)
        self.width = 5
        self.height = 20
        self.speed = 14
        self.active = True
        self.pulse = 0

    def update(self):
        self.y -= self.speed
        self.pulse += 0.2
        if self.y < 0:
            self.active = False

    def draw(self, surface):
        try:
            glow_size = int(18 + math.sin(self.pulse) * 3)
            draw_glow(surface, (int(self.x), int(self.y)), glow_size, (255, 100, 100), 100)
            pygame.draw.rect(surface, (255, 255, 220),
                           (int(self.x) - self.width // 2, int(self.y) - self.height // 2,
                            self.width, self.height))
            pygame.draw.rect(surface, (255, 150, 150),
                           (int(self.x) - self.width // 2 - 1,
                            int(self.y) - self.height // 2,
                            self.width + 2, self.height), 1)
        except Exception:
            pass

    def get_rect(self):
        return pygame.Rect(int(self.x) - self.width // 2,
                          int(self.y) - self.height // 2,
                          self.width, self.height)

# ==================== LEVEL PATTERNS ====================
def get_level_pattern(level):
    positions = []
    rows = min(4 + level, 8)
    cols = 10

    if level == 1:
        for r in range(rows):
            for c in range(cols):
                positions.append((r, c))
    elif level == 2:
        for r in range(rows):
            for c in range(cols):
                if (r + c) % 2 == 0:
                    positions.append((r, c))
    elif level == 3:
        center_r, center_c = rows // 2, cols // 2
        for r in range(rows):
            for c in range(cols):
                if abs(r - center_r) + abs(c - center_c) <= max(rows, cols) // 2:
                    positions.append((r, c))
    elif level == 4:
        for r in range(rows):
            for c in range(r, cols - r):
                positions.append((r, c))
    elif level == 5:
        for r in range(rows):
            for c in range(cols):
                if not (r % 2 == 0 and c % 3 == 0):
                    positions.append((r, c))
    else:
        for r in range(rows):
            for c in range(cols):
                positions.append((r, c))
    return positions

# ==================== MAIN GAME CLASS ====================
class Game:
    def __init__(self):
        self.state = 'MENU'
        self.high_score = load_high_score()
        self.mouse_pos = None
        self.menu_anim = 0
        self.reset()

    def reset(self):
        self.paddle = Paddle()
        self.balls = [Ball(WIDTH // 2, HEIGHT - 90)]
        self.bricks = []
        self.particles = []
        self.powerups = []
        self.lasers = []
        self.score = 0
        self.lives = 3
        self.level = 1
        self.combo = 0
        self.combo_timer = 0
        self.shake_amount = 0
        self.total_bricks = 0
        self.setup_level(1)

    def setup_level(self, level):
        self.bricks = []
        self.lasers = []
        positions = get_level_pattern(level)
        cols = 10
        brick_w = (WIDTH - 80) // cols
        brick_h = 30
        for r, c in positions:
            x = 40 + c * brick_w
            y = 80 + r * (brick_h + 5)
            hp = min(1 + (r // 2) + (level // 2), 5)
            self.bricks.append(Brick(x, y, brick_w - 4, brick_h, hp))
        self.total_bricks = len(self.bricks)

    def spawn_particles(self, x, y, color, count=20):
        for _ in range(count):
            self.particles.append(Particle(x, y, color))

    def apply_powerup(self, ptype):
        if ptype == 'wide':
            self.paddle.width = min(260, self.paddle.width + 40)
            self.spawn_particles(self.paddle.x + self.paddle.width / 2,
                               self.paddle.y, (0, 255, 150), 25)
        elif ptype == 'multi':
            new_balls = []
            for b in self.balls:
                for _ in range(2):
                    nb = Ball(b.x, b.y)
                    nb.vx = random.uniform(-5, 5)
                    nb.vy = -abs(b.vy)
                    nb.ensure_vertical_speed()
                    new_balls.append(nb)
            self.balls.extend(new_balls)
        elif ptype == 'fire':
            for b in self.balls:
                b.fireball = True
                b.fire_timer = 600
        elif ptype == 'life':
            self.lives += 1
        elif ptype == 'laser':
            self.paddle.laser_timer = 600
        elif ptype == 'shield':
            self.paddle.shield_active = True

    def fire_laser(self):
        if self.paddle.laser_timer > 0 and self.paddle.laser_cooldown <= 0:
            self.lasers.append(Laser(self.paddle.x + 15, self.paddle.y))
            self.lasers.append(Laser(self.paddle.x + self.paddle.width - 15, self.paddle.y))
            self.paddle.laser_cooldown = 12

    def handle_events(self):
        for event in pygame.event.get():
            try:
                if event.type == pygame.QUIT:
                    return False

                elif event.type == pygame.KEYDOWN:
                    if self.state == 'MENU' and event.key == pygame.K_SPACE:
                        self.state = 'PLAYING'
                    elif self.state == 'PLAYING' and event.key == pygame.K_ESCAPE:
                        self.state = 'PAUSED'
                    elif self.state == 'PAUSED' and event.key == pygame.K_ESCAPE:
                        self.state = 'PLAYING'
                    elif self.state in ('GAME_OVER', 'WIN'):
                        if event.key == pygame.K_r:
                            self.reset()
                            self.state = 'PLAYING'
                        elif event.key == pygame.K_m:
                            self.state = 'MENU'

                elif event.type == pygame.MOUSEMOTION:
                    if self.state == 'PLAYING':
                        self.paddle.target_x = event.pos[0]
                    self.mouse_pos = event.pos

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if self.state == 'MENU':
                        self.state = 'PLAYING'
                    elif self.state in ('GAME_OVER', 'WIN'):
                        self.reset()
                        self.state = 'PLAYING'
                    elif self.state == 'PAUSED':
                        self.state = 'PLAYING'
                    elif self.state == 'PLAYING':
                        self.paddle.target_x = event.pos[0]

            except Exception:
                pass
        return True

    def update(self):
        if not self.handle_events():
            return False

        self.menu_anim += 0.05

        if self.state != 'PLAYING':
            return True

        keys = pygame.key.get_pressed()
        self.paddle.update(keys)

        if self.paddle.laser_timer > 0:
            self.fire_laser()

        # Update balls
        for ball in self.balls[:]:
            ball.update()

            if ball.x - ball.radius < 0:
                ball.x = ball.radius
                ball.vx = abs(ball.vx)
            if ball.x + ball.radius > WIDTH:
                ball.x = WIDTH - ball.radius
                ball.vx = -abs(ball.vx)
            if ball.y - ball.radius < 0:
                ball.y = ball.radius
                ball.vy = abs(ball.vy)

            if ball.y > HEIGHT:
                if self.paddle.shield_active:
                    self.paddle.shield_active = False
                    ball.y = HEIGHT - 100
                    ball.vy = -abs(ball.vy)
                    self.spawn_particles(ball.x, ball.y, (100, 255, 200), 35)
                    self.shake_amount = 10
                else:
                    self.balls.remove(ball)
                    continue

            ball.ensure_vertical_speed()

            if ball.get_rect().colliderect(self.paddle.get_rect()) and ball.vy > 0:
                ball.y = self.paddle.y - ball.radius
                hit_pos = (ball.x - self.paddle.x) / self.paddle.width
                hit_pos = max(0, min(1, hit_pos))
                angle = (hit_pos - 0.5) * math.pi * 0.7
                speed = math.hypot(ball.vx, ball.vy)
                speed = max(speed, ball.speed)
                ball.vx = speed * math.sin(angle)
                ball.vy = -abs(speed * math.cos(angle))
                ball.ensure_vertical_speed()
                self.spawn_particles(ball.x, ball.y, (100, 200, 255), 12)

            for brick in self.bricks[:]:
                if ball.get_rect().colliderect(brick.rect):
                    destroy_color = brick.colors[0]

                    overlap_x = min(ball.get_rect().right - brick.rect.left,
                                   brick.rect.right - ball.get_rect().left)
                    overlap_y = min(ball.get_rect().bottom - brick.rect.top,
                                   brick.rect.bottom - ball.get_rect().top)

                    if not ball.fireball:
                        if overlap_x < overlap_y:
                            ball.vx *= -1
                        else:
                            ball.vy *= -1

                    destroyed = brick.hit()
                    if destroyed:
                        self.spawn_particles(brick.rect.centerx, brick.rect.centery,
                                           destroy_color, 30)
                        self.bricks.remove(brick)
                        self.combo += 1
                        self.combo_timer = 90
                        self.score += 10 * self.combo
                        self.shake_amount = 8
                        if random.random() < 0.22:
                            self.powerups.append(PowerUp(brick.rect.centerx,
                                                        brick.rect.centery))
                    else:
                        self.spawn_particles(ball.x, ball.y, (255, 255, 255), 8)
                    if not ball.fireball:
                        break

        # Update lasers
        for laser in self.lasers[:]:
            laser.update()
            if not laser.active:
                self.lasers.remove(laser)
                continue
            for brick in self.bricks[:]:
                if laser.get_rect().colliderect(brick.rect):
                    destroy_color = brick.colors[0]
                    laser.active = False
                    destroyed = brick.hit()
                    if destroyed:
                        self.spawn_particles(brick.rect.centerx, brick.rect.centery,
                                           destroy_color, 25)
                        self.bricks.remove(brick)
                        self.score += 10
                        self.shake_amount = 4
                        if random.random() < 0.18:
                            self.powerups.append(PowerUp(brick.rect.centerx,
                                                        brick.rect.centery))
                    else:
                        self.spawn_particles(laser.x, laser.y, (255, 150, 150), 10)
                    break

        # Update particles
        for p in self.particles[:]:
            p.update()
            if p.is_dead():
                self.particles.remove(p)

        # Update powerups
        for pu in self.powerups[:]:
            pu.update(self.paddle.x, self.paddle.width)
            if pu.get_rect().colliderect(self.paddle.get_rect()):
                self.apply_powerup(pu.type)
                self.powerups.remove(pu)
            elif pu.y > HEIGHT:
                self.powerups.remove(pu)

        if self.combo_timer > 0:
            self.combo_timer -= 1
        else:
            self.combo = 0

        if self.shake_amount > 0:
            self.shake_amount *= 0.85
            if self.shake_amount < 0.1:
                self.shake_amount = 0

        if not self.balls:
            self.lives -= 1
            if self.lives <= 0:
                self.state = 'GAME_OVER'
                if self.score > self.high_score:
                    self.high_score = self.score
                    save_high_score(self.high_score)
            else:
                self.balls = [Ball(self.paddle.x + self.paddle.width // 2,
                                  self.paddle.y - 30)]
                self.paddle.width = self.paddle.base_width

        if not self.bricks:
            self.score += 100 * self.level
            self.level += 1
            if self.level > 5:
                self.state = 'WIN'
                if self.score > self.high_score:
                    self.high_score = self.score
                    save_high_score(self.high_score)
            else:
                self.setup_level(self.level)
                self.balls = [Ball(WIDTH // 2, HEIGHT - 90)]
                self.paddle.width = self.paddle.base_width

        return True

    def draw(self):
        try:
            # Animated background
            t = pygame.time.get_ticks() / 3000
            c1 = (int(25 + 20 * math.sin(t)), 15, int(50 + 25 * math.sin(t + 1)))
            c2 = (15, int(25 + 20 * math.sin(t + 2)), int(60 + 25 * math.sin(t + 3)))
            draw_gradient_rect(screen, c1, c2, (0, 0, WIDTH, HEIGHT))

            # Animated stars
            for i in range(50):
                x = int((i * 137 + t * 60) % WIDTH)
                y = int((i * 211 + t * 40) % HEIGHT)
                twinkle = int(180 + 70 * math.sin(t * 3 + i))
                pygame.draw.circle(screen, (twinkle, twinkle, twinkle), (x, y), 1)

            # Screen shake
            if self.shake_amount > 0.5:
                sx = int(random.uniform(-self.shake_amount, self.shake_amount))
                sy = int(random.uniform(-self.shake_amount, self.shake_amount))
                temp = screen.copy()
                screen.fill(BLACK)
                screen.blit(temp, (sx, sy))

            # Vignette effect
            draw_vignette(screen)

            if self.state == 'MENU':
                self.draw_menu()
            elif self.state == 'PLAYING':
                self.draw_game()
            elif self.state == 'PAUSED':
                self.draw_game()
                self.draw_pause()
            elif self.state == 'GAME_OVER':
                self.draw_game()
                self.draw_overlay("GAME OVER", (255, 80, 80),
                                f"Score: {self.score}", "R - Restart | M - Menu")
            elif self.state == 'WIN':
                self.draw_game()
                self.draw_overlay("VICTORY!", (100, 255, 150),
                                f"Score: {self.score}", "R - Play Again | M - Menu")

            pygame.display.flip()
        except Exception as e:
            print(f"Draw error: {e}")

    def draw_game(self):
        try:
            for brick in self.bricks:
                brick.draw(screen)
            for pu in self.powerups:
                pu.draw(screen)
            for laser in self.lasers:
                laser.draw(screen)
            self.paddle.draw(screen)
            for ball in self.balls:
                ball.draw(screen)
            for p in self.particles:
                p.draw(screen)
            self.draw_hud()
        except Exception as e:
            print(f"Game draw error: {e}")

    def draw_hud(self):
        try:
            # Premium HUD bar
            hud_rect = (0, 0, WIDTH, 55)
            draw_gradient_rect(screen, (20, 20, 40), (40, 40, 80), hud_rect)
            pygame.draw.line(screen, (100, 200, 255), (0, 55), (WIDTH, 55), 3)

            # Score with icon
            score_icon = FONT_MED.render("★", True, (255, 230, 100))
            screen.blit(score_icon, (15, 12))
            score_txt = FONT_MED.render(f"{self.score}", True, WHITE)
            screen.blit(score_txt, (45, 12))

            # Level with icon
            level_icon = FONT_MED.render("◆", True, (100, 255, 200))
            screen.blit(level_icon, (WIDTH // 2 - 60, 12))
            level_txt = FONT_MED.render(f"Level {self.level}", True, (100, 255, 200))
            screen.blit(level_txt, (WIDTH // 2 - 30, 12))

            # Lives with hearts
            lives_x = WIDTH - 150
            for i in range(self.lives):
                heart = FONT_MED.render("♥", True, (255, 80, 80))
                screen.blit(heart, (lives_x + i * 30, 12))

            # Progress bar
            if self.total_bricks > 0:
                progress = 1 - (len(self.bricks) / self.total_bricks)
                bar_w, bar_h = 220, 8
                bar_x = WIDTH // 2 - bar_w // 2
                bar_y = 45
                pygame.draw.rect(screen, (30, 30, 50), (bar_x, bar_y, bar_w, bar_h))
                pygame.draw.rect(screen, (100, 255, 200),
                               (bar_x, bar_y, int(bar_w * progress), bar_h))
                pygame.draw.rect(screen, (200, 200, 255), (bar_x, bar_y, bar_w, bar_h), 2)

            # Combo
            if self.combo > 1:
                combo_txt = FONT_BIG.render(f"COMBO x{self.combo}!", True, (255, 230, 80))
                screen.blit(combo_txt, (WIDTH // 2 - combo_txt.get_width() // 2, 85))
        except Exception:
            pass

    def draw_menu(self):
        try:
            # Dark overlay
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            screen.blit(overlay, (0, 0))

            # Animated title
            title_y = 120 + math.sin(self.menu_anim) * 10
            draw_text_centered(screen, "BRICK BREAKER", FONT_HUGE, (100, 220, 255), int(title_y))
            draw_text_centered(screen, "ULTRA PREMIUM", FONT_BIG, (255, 200, 100), int(title_y + 70))

            # Animated prompt
            t = pygame.time.get_ticks() / 500
            brightness = int(180 + 70 * math.sin(t))
            color = (brightness, brightness, brightness)
            draw_text_centered(screen, "Click or Press SPACE", FONT_MED, color, 350)

            # High score
            if self.high_score > 0:
                draw_text_centered(screen, f"Best Score: {self.high_score}",
                                 FONT_MED, (255, 230, 100), 420)

            # Controls
            controls = [
                "🖱️ Mouse/Touch: Move paddle",
                "⌨️ Keyboard: Arrow keys or A/D",
                "⏸️ ESC: Pause | R: Restart",
                "",
                "Power-ups: W=Wide  M=Multi  F=Fire",
                "           L=Laser  S=Shield  ♥=Life"
            ]
            y = 500
            for line in controls:
                if line:
                    draw_text_centered(screen, line, FONT_SMALL, (220, 220, 220), y)
                y += 28
        except Exception:
            pass

    def draw_pause(self):
        try:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 200))
            screen.blit(overlay, (0, 0))

            draw_text_centered(screen, "PAUSED", FONT_HUGE, (100, 200, 255), 250)
            draw_text_centered(screen, "Click or Press ESC", FONT_MED, WHITE, 350)
        except Exception:
            pass

    def draw_overlay(self, title, color, score_text, hint):
        try:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 200))
            screen.blit(overlay, (0, 0))

            draw_text_centered(screen, title, FONT_HUGE, color, 200)
            draw_text_centered(screen, score_text, FONT_BIG, WHITE, 300)

            if self.score >= self.high_score and self.score > 0:
                draw_text_centered(screen, "★ NEW HIGH SCORE! ★",
                                 FONT_MED, (255, 230, 100), 370)

            draw_text_centered(screen, hint, FONT_MED, (220, 220, 220), 430)
        except Exception:
            pass

# ==================== MAIN LOOP ====================
def main():
    game = Game()
    running = True
    while running:
        try:
            running = game.update()
            game.draw()
        except Exception as e:
            print(f"Error: {e}")
        clock.tick(FPS)
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()