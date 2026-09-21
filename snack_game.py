import pygame
import random
import sys
import math

# ============ CONFIGURATION ============
WINDOW_WIDTH = 600
WINDOW_HEIGHT = 600
CELL_SIZE = 25
GRID_W = WINDOW_WIDTH // CELL_SIZE
GRID_H = WINDOW_HEIGHT // CELL_SIZE
FPS = 10

# Colors (Neon Theme)
BG_DARK = (10, 10, 25)
BG_LIGHT = (25, 20, 50)
GRID_COLOR = (30, 30, 60)
SNAKE_HEAD = (0, 255, 180)
SNAKE_BODY = (0, 200, 150)
SNAKE_GLOW = (0, 255, 200)
FOOD_COLOR = (255, 60, 100)
FOOD_GLOW = (255, 100, 150)
TEXT_COLOR = (255, 255, 255)
ACCENT = (255, 200, 50)

# Directions
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# ============ PARTICLE CLASS ============
class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        angle = random.uniform(0, math.pi * 2)
        speed = random.uniform(2, 6)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.life = random.randint(20, 40)
        self.max_life = self.life
        self.size = random.randint(2, 5)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vx *= 0.95
        self.vy *= 0.95
        self.life -= 1

    def draw(self, surface):
        alpha = self.life / self.max_life
        r = int(self.size * alpha)
        if r > 0:
            col = (
                int(self.color[0] * alpha),
                int(self.color[1] * alpha),
                int(self.color[2] * alpha)
            )
            pygame.draw.circle(surface, col, (int(self.x), int(self.y)), r)

    def is_dead(self):
        return self.life <= 0

# ============ MAIN GAME ============
class SnakeGame:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("🐍 Neon Snake Game")
        self.clock = pygame.time.Clock()
        self.font_big = pygame.font.SysFont("consolas", 60, bold=True)
        self.font_med = pygame.font.SysFont("consolas", 30, bold=True)
        self.font_small = pygame.font.SysFont("consolas", 22)
        self.high_score = 0
        self.reset()
        self.state = "menu"  # menu, playing, gameover

    def reset(self):
        mid_x = GRID_W // 2
        mid_y = GRID_H // 2
        self.snake = [(mid_x, mid_y), (mid_x - 1, mid_y), (mid_x - 2, mid_y)]
        self.direction = RIGHT
        self.next_direction = RIGHT
        self.score = 0
        self.particles = []
        self.food = self.spawn_food()
        self.food_pulse = 0

    def spawn_food(self):
        while True:
            pos = (random.randint(0, GRID_W - 1), random.randint(0, GRID_H - 1))
            if pos not in self.snake:
                return pos

    def spawn_particles(self, x, y, color, count=20):
        for _ in range(count):
            px = x * CELL_SIZE + CELL_SIZE // 2
            py = y * CELL_SIZE + CELL_SIZE // 2
            self.particles.append(Particle(px, py, color))

    def draw_background(self):
        # Gradient background
        for y in range(0, WINDOW_HEIGHT, 2):
            ratio = y / WINDOW_HEIGHT
            r = int(BG_DARK[0] * (1 - ratio) + BG_LIGHT[0] * ratio)
            g = int(BG_DARK[1] * (1 - ratio) + BG_LIGHT[1] * ratio)
            b = int(BG_DARK[2] * (1 - ratio) + BG_LIGHT[2] * ratio)
            pygame.draw.line(self.screen, (r, g, b), (0, y), (WINDOW_WIDTH, y), 2)

        # Grid
        for x in range(0, WINDOW_WIDTH, CELL_SIZE):
            pygame.draw.line(self.screen, GRID_COLOR, (x, 0), (x, WINDOW_HEIGHT), 1)
        for y in range(0, WINDOW_HEIGHT, CELL_SIZE):
            pygame.draw.line(self.screen, GRID_COLOR, (0, y), (WINDOW_WIDTH, y), 1)

    def draw_snake(self):
        for i, (x, y) in enumerate(self.snake):
            px = x * CELL_SIZE
            py = y * CELL_SIZE
            if i == 0:
                color = SNAKE_HEAD
                glow_color = SNAKE_GLOW
                size = CELL_SIZE - 2
            else:
                fade = 1 - (i / len(self.snake)) * 0.5
                color = (
                    int(SNAKE_BODY[0] * fade),
                    int(SNAKE_BODY[1] * fade),
                    int(SNAKE_BODY[2] * fade)
                )
                glow_color = color
                size = CELL_SIZE - 4

            # Glow effect
            glow_surf = pygame.Surface((size + 10, size + 10), pygame.SRCALPHA)
            pygame.draw.circle(glow_surf, (*glow_color, 40), (size // 2 + 5, size // 2 + 5), size // 2 + 5)
            self.screen.blit(glow_surf, (px - 3, py - 3))

            # Body
            rect = pygame.Rect(px + (CELL_SIZE - size) // 2, py + (CELL_SIZE - size) // 2, size, size)
            pygame.draw.rect(self.screen, color, rect, border_radius=size // 3)

            # Eyes on head
            if i == 0:
                eye_size = 4
                if self.direction == RIGHT:
                    ex1, ey1 = px + size - 8, py + 6
                    ex2, ey2 = px + size - 8, py + size - 10
                elif self.direction == LEFT:
                    ex1, ey1 = px + 4, py + 6
                    ex2, ey2 = px + 4, py + size - 10
                elif self.direction == UP:
                    ex1, ey1 = px + 6, py + 4
                    ex2, ey2 = px + size - 10, py + 4
                else:
                    ex1, ey1 = px + 6, py + size - 8
                    ex2, ey2 = px + size - 10, py + size - 8
                pygame.draw.circle(self.screen, (255, 255, 255), (ex1, ey1), eye_size)
                pygame.draw.circle(self.screen, (255, 255, 255), (ex2, ey2), eye_size)
                pygame.draw.circle(self.screen, (0, 0, 0), (ex1, ey1), 2)
                pygame.draw.circle(self.screen, (0, 0, 0), (ex2, ey2), 2)

    def draw_food(self):
        self.food_pulse += 0.15
        pulse = math.sin(self.food_pulse) * 3
        px = self.food[0] * CELL_SIZE + CELL_SIZE // 2
        py = self.food[1] * CELL_SIZE + CELL_SIZE // 2
        radius = CELL_SIZE // 2 - 2 + pulse

        # Outer glow
        for i in range(3):
            glow_surf = pygame.Surface((int(radius * 3), int(radius * 3)), pygame.SRCALPHA)
            pygame.draw.circle(glow_surf, (*FOOD_GLOW, 30 - i * 8), (int(radius * 1.5), int(radius * 1.5)), int(radius + i * 4))
            self.screen.blit(glow_surf, (int(px - radius * 1.5), int(py - radius * 1.5)))

        # Main food
        pygame.draw.circle(self.screen, FOOD_COLOR, (px, py), int(radius))
        pygame.draw.circle(self.screen, (255, 200, 200), (int(px - radius // 3), int(py - radius // 3)), int(radius // 4))

    def draw_particles(self):
        for p in self.particles[:]:
            p.update()
            p.draw(self.screen)
            if p.is_dead():
                self.particles.remove(p)

    def draw_hud(self):
        # Score panel
        panel = pygame.Surface((200, 60), pygame.SRCALPHA)
        panel.fill((0, 0, 0, 120))
        pygame.draw.rect(panel, ACCENT, (0, 0, 200, 60), 2, border_radius=10)
        self.screen.blit(panel, (10, 10))

        score_text = self.font_med.render(f"SCORE: {self.score}", True, ACCENT)
        self.screen.blit(score_text, (25, 15))
        hi_text = self.font_small.render(f"HI: {self.high_score}", True, TEXT_COLOR)
        self.screen.blit(hi_text, (25, 42))

    def draw_menu(self):
        self.draw_background()

        # Title with glow
        title = self.font_big.render("NEON SNAKE", True, SNAKE_GLOW)
        title_rect = title.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 3))
        glow = pygame.Surface((title_rect.width + 40, title_rect.height + 40), pygame.SRCALPHA)
        pygame.draw.rect(glow, (*SNAKE_GLOW, 50), glow.get_rect(), border_radius=20)
        self.screen.blit(glow, (title_rect.x - 20, title_rect.y - 20))
        self.screen.blit(title, title_rect)

        # Subtitle
        sub = self.font_med.render("🐍 Classic Snake, Modern Style", True, TEXT_COLOR)
        self.screen.blit(sub, sub.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)))

        # Blinking prompt
        if pygame.time.get_ticks() // 500 % 2 == 0:
            prompt = self.font_med.render("Press SPACE to Start", True, ACCENT)
            self.screen.blit(prompt, prompt.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 80)))

        # Controls
        ctrl = self.font_small.render("Arrow Keys / WASD to move | P to Pause", True, (180, 180, 200))
        self.screen.blit(ctrl, ctrl.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 60)))

    def draw_game_over(self):
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        go_text = self.font_big.render("GAME OVER", True, FOOD_COLOR)
        self.screen.blit(go_text, go_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 3)))

        score_text = self.font_med.render(f"Your Score: {self.score}", True, TEXT_COLOR)
        self.screen.blit(score_text, score_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)))

        hi_text = self.font_med.render(f"High Score: {self.high_score}", True, ACCENT)
        self.screen.blit(hi_text, hi_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 50)))

        if pygame.time.get_ticks() // 500 % 2 == 0:
            prompt = self.font_med.render("Press SPACE to Restart", True, ACCENT)
            self.screen.blit(prompt, prompt.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 130)))

    def update(self):
        if self.state != "playing":
            return

        self.direction = self.next_direction
        hx, hy = self.snake[0]
        dx, dy = self.direction
        new_head = (hx + dx, hy + dy)

        # Wall collision
        if (new_head[0] < 0 or new_head[0] >= GRID_W or
            new_head[1] < 0 or new_head[1] >= GRID_H):
            self.game_over()
            return

        # Self collision
        if new_head in self.snake:
            self.game_over()
            return

        self.snake.insert(0, new_head)

        # Eat food
        if new_head == self.food:
            self.score += 10
            self.spawn_particles(self.food[0], self.food[1], FOOD_COLOR, 25)
            self.food = self.spawn_food()
        else:
            self.snake.pop()

    def game_over(self):
        if self.score > self.high_score:
            self.high_score = self.score
        self.state = "gameover"

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if self.state == "menu":
                    if event.key == pygame.K_SPACE:
                        self.state = "playing"
                elif self.state == "playing":
                    if event.key in (pygame.K_UP, pygame.K_w) and self.direction != DOWN:
                        self.next_direction = UP
                    elif event.key in (pygame.K_DOWN, pygame.K_s) and self.direction != UP:
                        self.next_direction = DOWN
                    elif event.key in (pygame.K_LEFT, pygame.K_a) and self.direction != RIGHT:
                        self.next_direction = LEFT
                    elif event.key in (pygame.K_RIGHT, pygame.K_d) and self.direction != LEFT:
                        self.next_direction = RIGHT
                    elif event.key == pygame.K_p:
                        self.state = "paused"
                    elif event.key == pygame.K_ESCAPE:
                        self.state = "menu"
                elif self.state == "paused":
                    if event.key == pygame.K_p or event.key == pygame.K_SPACE:
                        self.state = "playing"
                elif self.state == "gameover":
                    if event.key == pygame.K_SPACE:
                        self.reset()
                        self.state = "playing"
                    elif event.key == pygame.K_ESCAPE:
                        self.reset()
                        self.state = "menu"

    def run(self):
        while True:
            self.handle_events()

            if self.state == "menu":
                self.draw_menu()
            elif self.state == "playing":
                self.update()
                self.draw_background()
                self.draw_food()
                self.draw_snake()
                self.draw_particles()
                self.draw_hud()
            elif self.state == "paused":
                self.draw_background()
                self.draw_food()
                self.draw_snake()
                self.draw_hud()
                overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 150))
                self.screen.blit(overlay, (0, 0))
                p_text = self.font_big.render("PAUSED", True, ACCENT)
                self.screen.blit(p_text, p_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)))
            elif self.state == "gameover":
                self.draw_background()
                self.draw_food()
                self.draw_snake()
                self.draw_particles()
                self.draw_hud()
                self.draw_game_over()

            pygame.display.flip()
            self.clock.tick(FPS)

if __name__ == "__main__":
    game = SnakeGame()
    game.run()