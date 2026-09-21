import pygame
import random
import sys
import math
import json
import os
from dataclasses import dataclass
from typing import List, Tuple, Optional
from enum import Enum

# ============ CONSTANTS ============
pygame.init()
WIDTH, HEIGHT = 1000, 650
FPS = 60

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("NEON PONG ULTIMATE")
clock = pygame.time.Clock()

try:
    font_title = pygame.font.SysFont("consolas", 64, bold=True)
    font_big = pygame.font.SysFont("consolas", 42, bold=True)
    font_med = pygame.font.SysFont("consolas", 28)
    font_small = pygame.font.SysFont("consolas", 20)
    font_tiny = pygame.font.SysFont("consolas", 16)
except Exception:
    font_title = pygame.font.Font(None, 72)
    font_big = pygame.font.Font(None, 48)
    font_med = pygame.font.Font(None, 32)
    font_small = pygame.font.Font(None, 24)
    font_tiny = pygame.font.Font(None, 18)

BG = (6, 6, 18)
CYAN = (0, 240, 255)
PINK = (255, 40, 160)
YELLOW = (255, 230, 60)
GREEN = (60, 255, 120)
PURPLE = (180, 80, 255)
ORANGE = (255, 140, 40)
RED = (255, 60, 80)
WHITE = (240, 240, 255)
DIM = (70, 70, 110)


class GameState(Enum):
    MENU = 0
    MODE_SELECT = 1
    DIFFICULTY_SELECT = 2
    PLAYING = 3
    PAUSED = 4
    GAMEOVER = 5
    HIGHSCORES = 6


class GameMode(Enum):
    VS_AI = "VS AI"
    TWO_PLAYER = "2 PLAYER"
    SURVIVAL = "SURVIVAL"
    TIME_ATTACK = "TIME ATTACK"


class Difficulty(Enum):
    EASY = ("EASY", 0.6, 5.0)
    NORMAL = ("NORMAL", 0.8, 6.5)
    HARD = ("HARD", 0.95, 8.0)
    INSANE = ("INSANE", 1.0, 10.0)


@dataclass
class Particle:
    x: float
    y: float
    vx: float
    vy: float
    life: float
    max_life: float
    color: Tuple[int, int, int]
    size: float
    gravity: float = 0.0

    def update(self, dt: float) -> bool:
        self.x += self.vx * dt * 60
        self.y += self.vy * dt * 60
        self.vy += self.gravity * dt * 60
        self.vx *= 0.96
        self.vy *= 0.96
        self.life -= dt
        return self.life > 0

    def draw(self, surface):
        alpha = max(0.0, self.life / self.max_life)
        r = max(1, int(self.size * alpha))
        c = (int(self.color[0] * alpha),
             int(self.color[1] * alpha),
             int(self.color[2] * alpha))
        pygame.draw.circle(surface, c, (int(self.x), int(self.y)), r)


@dataclass
class FloatingText:
    x: float
    y: float
    text: str
    color: Tuple[int, int, int]
    life: float = 1.2
    max_life: float = 1.2
    vy: float = -1.5
    font: Optional[pygame.font.Font] = None

    def update(self, dt: float) -> bool:
        self.y += self.vy * dt * 60
        self.life -= dt
        return self.life > 0

    def draw(self, surface):
        alpha = max(0.0, self.life / self.max_life)
        c = (int(self.color[0] * alpha),
             int(self.color[1] * alpha),
             int(self.color[2] * alpha))
        f = self.font if self.font is not None else font_med
        txt = f.render(self.text, True, c)
        rect = txt.get_rect(center=(int(self.x), int(self.y)))
        surface.blit(txt, rect)


class Ball:
    def __init__(self):
        self.radius = 9
        self.trail: List[Tuple[float, float, Tuple[int, int, int]]] = []
        self.max_trail = 18
        self.x = float(WIDTH / 2)
        self.y = float(HEIGHT / 2)
        self.vx = 0.0
        self.vy = 0.0
        self.base_speed = 6.5
        self.speed = 6.5
        self.frozen = False
        self.freeze_time = 0.0
        self.reset()

    def reset(self, direction: int = 1):
        self.x = float(WIDTH / 2)
        self.y = float(HEIGHT / 2)
        angle = random.uniform(-math.pi / 5, math.pi / 5)
        self.base_speed = 6.5
        self.speed = self.base_speed
        self.vx = math.cos(angle) * self.speed * direction
        self.vy = math.sin(angle) * self.speed
        self.trail.clear()
        self.frozen = False
        self.freeze_time = 0.0

    def current_speed(self):
        return math.hypot(self.vx, self.vy)

    def update(self, dt, particles, time_scale=1.0):
        if self.frozen:
            self.freeze_time -= dt
            if self.freeze_time <= 0:
                self.frozen = False
            return

        self.trail.append((self.x, self.y, (CYAN[0], CYAN[1], CYAN[2])))
        if len(self.trail) > self.max_trail:
            self.trail.pop(0)

        self.x += self.vx * dt * 60 * time_scale
        self.y += self.vy * dt * 60 * time_scale

        if self.y - self.radius < 0:
            self.y = float(self.radius)
            self.vy = -self.vy
            self._wall_fx(particles)
        elif self.y + self.radius > HEIGHT:
            self.y = float(HEIGHT - self.radius)
            self.vy = -self.vy
            self._wall_fx(particles)

    def _wall_fx(self, particles):
        for _ in range(10):
            particles.append(Particle(
                self.x, self.y,
                random.uniform(-3, 3), random.uniform(-3, 3),
                random.uniform(0.3, 0.6), 0.6,
                YELLOW, random.uniform(2, 4)
            ))

    def draw(self, surface):
        trail_len = len(self.trail)
        if trail_len > 0:
            for i, (tx, ty, c) in enumerate(self.trail):
                alpha = (i + 1) / trail_len
                r = int(self.radius * alpha * 0.8)
                if r > 0:
                    color = (int(c[0] * alpha), int(c[1] * alpha), int(c[2] * alpha))
                    pygame.draw.circle(surface, color, (int(tx), int(ty)), r)
        pygame.draw.circle(surface, WHITE, (int(self.x), int(self.y)), self.radius + 4)
        pygame.draw.circle(surface, CYAN, (int(self.x), int(self.y)), self.radius)


class Paddle:
    def __init__(self, x, color, is_ai=False):
        self.x = x
        self.y = float(HEIGHT / 2)
        self.base_width = 14
        self.base_height = 100
        self.width = self.base_width
        self.height = float(self.base_height)
        self.vy = 0.0
        self.base_speed = 8.0
        self.speed = self.base_speed
        self.color = color
        self.is_ai = is_ai
        self.hit_flash = 0.0

    @property
    def rect(self) -> pygame.Rect:
        return pygame.Rect(
            self.x - self.width // 2,
            int(self.y - self.height / 2),
            self.width,
            max(1, int(self.height))
        )

    def update(self, dt):
        self.y += self.vy * dt * 60
        half_h = self.height / 2
        if self.y - half_h < 0:
            self.y = half_h
        elif self.y + half_h > HEIGHT:
            self.y = HEIGHT - half_h
        if self.hit_flash > 0:
            self.hit_flash -= dt

    def draw(self, surface):
        r = self.rect
        glow = pygame.Rect(r.x - 6, r.y - 6, r.width + 12, r.height + 12)
        glow_color = (self.color[0] // 3, self.color[1] // 3, self.color[2] // 3)
        pygame.draw.rect(surface, glow_color, glow, border_radius=8)
        main_color = WHITE if self.hit_flash > 0 else self.color
        pygame.draw.rect(surface, main_color, r, border_radius=5)

    def collide(self, ball: Ball) -> bool:
        r = self.rect
        closest_x = max(r.left, min(ball.x, r.right))
        closest_y = max(r.top, min(ball.y, r.bottom))
        dx = ball.x - closest_x
        dy = ball.y - closest_y
        return (dx * dx + dy * dy) < (ball.radius * ball.radius)


SCORE_FILE = "neon_pong_scores.json"


def load_scores() -> dict:
    if os.path.exists(SCORE_FILE):
        try:
            with open(SCORE_FILE, 'r') as f:
                data = json.load(f)
                if isinstance(data, dict):
                    return data
        except Exception:
            pass
    return {"VS_AI": [], "SURVIVAL": [], "TIME_ATTACK": []}


def save_scores(scores):
    try:
        with open(SCORE_FILE, 'w') as f:
            json.dump(scores, f, indent=2)
    except Exception as e:
        print(f"Could not save scores: {e}")


class Game:
    def __init__(self):
        self.state = GameState.MENU
        self.mode = GameMode.VS_AI
        self.difficulty = Difficulty.NORMAL
        self.scores = load_scores()

        self.left_paddle = Paddle(60, CYAN)
        self.right_paddle = Paddle(WIDTH - 60, PINK, is_ai=True)
        self.balls: List[Ball] = [Ball()]
        self.particles: List[Particle] = []
        self.floating_texts: List[FloatingText] = []

        self.score_left = 0
        self.score_right = 0
        self.combo_left = 0
        self.combo_right = 0
        self.max_combo_left = 0
        self.max_combo_right = 0
        self.hits_left = 0
        self.hits_right = 0

        self.winner: Optional[str] = None
        self.shake = 0
        self.win_score = 7
        self.survival_time = 0.0
        self.time_attack_time = 30.0
        self.time_attack_score = 0
        self.game_time = 0.0

        self.menu_time = 0.0
        self.menu_particles: List[Particle] = []
        self._init_menu_particles()

        self.selected_menu = 0
        self.selected_mode = 0
        self.selected_diff = 1

    def _init_menu_particles(self):
        self.menu_particles = []
        for _ in range(60):
            self.menu_particles.append(Particle(
                random.uniform(0, WIDTH),
                random.uniform(0, HEIGHT),
                random.uniform(-0.5, 0.5),
                random.uniform(-0.5, 0.5),
                999.0, 999.0,
                random.choice([CYAN, PINK, PURPLE, YELLOW]),
                random.uniform(1, 3)
            ))

    def reset_round(self, direction: int = 1):
        self.balls = [Ball()]
        self.balls[0].reset(direction)
        self.left_paddle.y = float(HEIGHT / 2)
        self.right_paddle.y = float(HEIGHT / 2)
        self.powerups_clear()
        self.time_scale = 1.0
        self.time_scale_effect = 0.0

    def powerups_clear(self):
        pass

    def reset_game(self):
        self.score_left = 0
        self.score_right = 0
        self.combo_left = 0
        self.combo_right = 0
        self.max_combo_left = 0
        self.max_combo_right = 0
        self.hits_left = 0
        self.hits_right = 0
        self.winner = None
        self.survival_time = 0.0
        self.time_attack_score = 0
        self.time_attack_time = 30.0
        self.game_time = 0.0
        self.reset_round(1 if random.random() < 0.5 else -1)

    def spawn_hit_fx(self, x, y, color, count=18):
        for _ in range(count):
            a = random.uniform(0, math.tau)
            s = random.uniform(2, 9)
            self.particles.append(Particle(
                x, y, math.cos(a) * s, math.sin(a) * s,
                random.uniform(0.4, 1.0), 1.0,
                color, random.uniform(2, 5)
            ))

    def spawn_score_fx(self, x):
        for _ in range(50):
            a = random.uniform(0, math.tau)
            s = random.uniform(3, 12)
            self.particles.append(Particle(
                x, HEIGHT / 2, math.cos(a) * s, math.sin(a) * s,
                random.uniform(0.6, 1.4), 1.4,
                YELLOW, random.uniform(3, 6), gravity=0.1
            ))

    def handle_paddle_collision(self, paddle: Paddle, ball: Ball, direction: int, is_left: bool):
        if paddle.collide(ball):
            half_h = paddle.height / 2
            if half_h < 1:
                half_h = 1
            hit_pos = (ball.y - paddle.y) / half_h
            hit_pos = max(-1.0, min(1.0, hit_pos))
            max_angle = math.pi / 3
            angle = hit_pos * max_angle
            speed = min(ball.current_speed() + 0.3, 15.0)
            ball.vx = math.cos(angle) * speed * direction
            ball.vy = math.sin(angle) * speed
            if direction > 0:
                ball.x = paddle.x + paddle.width // 2 + ball.radius + 1
            else:
                ball.x = paddle.x - paddle.width // 2 - ball.radius - 1
            self.spawn_hit_fx(ball.x, ball.y, paddle.color)
            paddle.hit_flash = 0.15
            self.shake = 6

            if is_left:
                self.combo_left += 1
                self.hits_left += 1
                self.max_combo_left = max(self.max_combo_left, self.combo_left)
                if self.combo_left >= 3:
                    self.floating_texts.append(FloatingText(
                        ball.x, ball.y - 30, f"COMBO x{self.combo_left}!", YELLOW))
            else:
                self.combo_right += 1
                self.hits_right += 1
                self.max_combo_right = max(self.max_combo_right, self.combo_right)

    def update_playing(self, dt, keys):
        self.game_time += dt

        self.left_paddle.vy = 0.0
        if keys[pygame.K_w]:
            self.left_paddle.vy = -self.left_paddle.speed
        if keys[pygame.K_s]:
            self.left_paddle.vy = self.left_paddle.speed

        if self.mode == GameMode.TWO_PLAYER:
            self.right_paddle.vy = 0.0
            if keys[pygame.K_UP]:
                self.right_paddle.vy = -self.right_paddle.speed
            if keys[pygame.K_DOWN]:
                self.right_paddle.vy = self.right_paddle.speed
        else:
            self._update_ai()

        self.left_paddle.update(dt)
        self.right_paddle.update(dt)

        for ball in self.balls[:]:
            if ball not in self.balls:
                continue
            ball.update(dt, self.particles, 1.0)
            self.handle_paddle_collision(self.left_paddle, ball, 1, True)
            self.handle_paddle_collision(self.right_paddle, ball, -1, False)

            if ball.x < -30:
                if len(self.balls) > 1:
                    if ball in self.balls:
                        self.balls.remove(ball)
                else:
                    self._score_right()
                    return
            elif ball.x > WIDTH + 30:
                if len(self.balls) > 1:
                    if ball in self.balls:
                        self.balls.remove(ball)
                else:
                    self._score_left()
                    return

        if self.mode == GameMode.TIME_ATTACK:
            self.time_attack_time -= dt
            if self.time_attack_time <= 0:
                self.time_attack_time = 0.0
                self._end_game_time_attack()
                return

        if self.mode == GameMode.SURVIVAL:
            self.survival_time += dt

    def _update_ai(self):
        diff = self.difficulty
        skill = diff.value[1]
        ai_speed = diff.value[2]

        target_ball = None
        for b in self.balls:
            if b.vx > 0:
                if target_ball is None or b.x > target_ball.x:
                    target_ball = b

        if target_ball is not None:
            vx_safe = max(0.5, abs(target_ball.vx))
            time_to_reach = (self.right_paddle.x - target_ball.x) / vx_safe
            predicted_y = target_ball.y + target_ball.vy * time_to_reach * skill

            bounces = 0
            while (predicted_y < 0 or predicted_y > HEIGHT) and bounces < 10:
                bounces += 1
                if predicted_y < 0:
                    predicted_y = -predicted_y
                elif predicted_y > HEIGHT:
                    predicted_y = 2 * HEIGHT - predicted_y

            predicted_y = max(0.0, min(float(HEIGHT), predicted_y))

            diff_y = predicted_y - self.right_paddle.y
            imperfection = (1.0 - skill) * 40
            diff_y += random.uniform(-imperfection, imperfection)

            if abs(diff_y) > 15:
                self.right_paddle.vy = ai_speed * (1.0 if diff_y > 0 else -1.0)
            else:
                self.right_paddle.vy = 0.0
        else:
            diff_y = HEIGHT / 2 - self.right_paddle.y
            if abs(diff_y) > 30:
                self.right_paddle.vy = 3.0 * (1.0 if diff_y > 0 else -1.0)
            else:
                self.right_paddle.vy = 0.0

    def _score_left(self):
        self.score_left += 1
        self.combo_right = 0
        self.spawn_score_fx(WIDTH)
        self.shake = 18
        if self.mode == GameMode.TIME_ATTACK:
            self.time_attack_score += 1
            self.time_attack_time += 3.0
        if self._check_win():
            return
        self.reset_round(-1)

    def _score_right(self):
        self.score_right += 1
        self.combo_left = 0
        self.spawn_score_fx(0)
        self.shake = 18
        if self._check_win():
            return
        self.reset_round(1)

    def _check_win(self) -> bool:
        if self.mode == GameMode.TIME_ATTACK:
            return False
        if self.score_left >= self.win_score:
            self.winner = "PLAYER 1" if self.mode == GameMode.TWO_PLAYER else "YOU"
            self._end_game(True)
            return True
        if self.score_right >= self.win_score:
            self.winner = "PLAYER 2" if self.mode == GameMode.TWO_PLAYER else "AI"
            self._end_game(self.mode != GameMode.VS_AI)
            return True
        return False

    def _end_game(self, player_won: bool):
        try:
            if self.mode == GameMode.VS_AI and player_won:
                score_entry = {
                    "score": f"{self.score_left}-{self.score_right}",
                    "difficulty": self.difficulty.value[0],
                    "combo": self.max_combo_left,
                    "time": round(self.game_time, 1)
                }
                self.scores.setdefault("VS_AI", []).append(score_entry)
                self.scores["VS_AI"] = sorted(
                    self.scores["VS_AI"],
                    key=lambda x: x.get("combo", 0), reverse=True
                )[:10]
                save_scores(self.scores)
            elif self.mode == GameMode.SURVIVAL:
                score_entry = {"time": round(self.survival_time, 1), "score": self.score_left}
                self.scores.setdefault("SURVIVAL", []).append(score_entry)
                self.scores["SURVIVAL"] = sorted(
                    self.scores["SURVIVAL"],
                    key=lambda x: x.get("time", 0), reverse=True
                )[:10]
                save_scores(self.scores)
            elif self.mode == GameMode.TIME_ATTACK:
                score_entry = {"score": self.time_attack_score, "time": round(self.game_time, 1)}
                self.scores.setdefault("TIME_ATTACK", []).append(score_entry)
                self.scores["TIME_ATTACK"] = sorted(
                    self.scores["TIME_ATTACK"],
                    key=lambda x: x.get("score", 0), reverse=True
                )[:10]
                save_scores(self.scores)
        except Exception as e:
            print(f"Score save error: {e}")

        self.state = GameState.GAMEOVER

    def _end_game_time_attack(self):
        self.winner = "TIME UP"
        try:
            score_entry = {"score": self.time_attack_score, "time": round(self.game_time, 1)}
            self.scores.setdefault("TIME_ATTACK", []).append(score_entry)
            self.scores["TIME_ATTACK"] = sorted(
                self.scores["TIME_ATTACK"],
                key=lambda x: x.get("score", 0), reverse=True
            )[:10]
            save_scores(self.scores)
        except Exception as e:
            print(f"Score save error: {e}")
        self.state = GameState.GAMEOVER

    def draw_text_centered(self, surface, text, font, color, y, shadow=True):
        if shadow:
            s = font.render(text, True, (0, 0, 0))
            rect = s.get_rect(center=(WIDTH // 2 + 2, y + 2))
            surface.blit(s, rect)
        rendered = font.render(text, True, color)
        rect = rendered.get_rect(center=(WIDTH // 2, y))
        surface.blit(rendered, rect)

    def draw_background(self, surface):
        surface.fill(BG)
        for x in range(0, WIDTH, 40):
            pygame.draw.line(surface, (15, 15, 35), (x, 0), (x, HEIGHT))
        for y in range(0, HEIGHT, 40):
            pygame.draw.line(surface, (15, 15, 35), (0, y), (WIDTH, y))
        for y in range(10, HEIGHT, 30):
            pygame.draw.rect(surface, DIM, (WIDTH // 2 - 2, y, 4, 15))
        pygame.draw.rect(surface, DIM, (5, 5, WIDTH - 10, HEIGHT - 10), 2, border_radius=12)

    def draw_menu(self, surface):
        self.menu_time += 0.016
        surface.fill(BG)
        for p in self.menu_particles:
            p.x += p.vx
            p.y += p.vy
            if p.x < 0:
                p.x = float(WIDTH)
            if p.x > WIDTH:
                p.x = 0.0
            if p.y < 0:
                p.y = float(HEIGHT)
            if p.y > HEIGHT:
                p.y = 0.0
            p.draw(surface)

        pulse = 1.0 + 0.05 * math.sin(self.menu_time * 3)
        title = font_title.render("NEON PONG", True, CYAN)
        new_w = max(1, int(title.get_width() * pulse))
        new_h = max(1, int(title.get_height() * pulse))
        title = pygame.transform.scale(title, (new_w, new_h))
        rect = title.get_rect(center=(WIDTH // 2, 120))
        glow = pygame.Surface((rect.width + 40, rect.height + 40), pygame.SRCALPHA)
        pygame.draw.rect(glow, (*CYAN, 40),
                         (0, 0, rect.width + 40, rect.height + 40), border_radius=20)
        surface.blit(glow, (rect.x - 20, rect.y - 20))
        surface.blit(title, rect)

        subtitle = font_med.render("ULTIMATE EDITION", True, PINK)
        rect = subtitle.get_rect(center=(WIDTH // 2, 180))
        surface.blit(subtitle, rect)

        options = ["PLAY", "HIGH SCORES", "QUIT"]
        for i, opt in enumerate(options):
            y = 300 + i * 60
            color = YELLOW if i == self.selected_menu else WHITE
            if i == self.selected_menu:
                pygame.draw.rect(surface, YELLOW,
                                 (WIDTH // 2 - 140, y - 22, 280, 44), 2, border_radius=8)
            txt = font_big.render(opt, True, color)
            rect = txt.get_rect(center=(WIDTH // 2, y))
            surface.blit(txt, rect)

        self.draw_text_centered(surface, "UP/DOWN Navigate  |  ENTER Select",
                                font_small, DIM, HEIGHT - 50, shadow=False)

    def draw_mode_select(self, surface):
        surface.fill(BG)
        for p in self.menu_particles:
            p.draw(surface)
        self.draw_text_centered(surface, "SELECT MODE", font_big, CYAN, 80)

        modes = [
            ("VS AI", "Classic match against AI", CYAN),
            ("2 PLAYER", "Local multiplayer", PINK),
            ("SURVIVAL", "How long can you last?", GREEN),
            ("TIME ATTACK", "Score max in 30 seconds", ORANGE),
        ]
        for i, (name, desc, color) in enumerate(modes):
            y = 180 + i * 100
            c = YELLOW if i == self.selected_mode else color
            pygame.draw.rect(surface, (20, 20, 40),
                             (WIDTH // 2 - 220, y - 35, 440, 80), border_radius=10)
            if i == self.selected_mode:
                pygame.draw.rect(surface, YELLOW,
                                 (WIDTH // 2 - 220, y - 35, 440, 80), 3, border_radius=10)
            txt = font_big.render(name, True, c)
            surface.blit(txt, (WIDTH // 2 - 200, y - 25))
            d = font_small.render(desc, True, DIM)
            surface.blit(d, (WIDTH // 2 - 200, y + 15))

        self.draw_text_centered(surface, "UP/DOWN Select  |  ENTER Confirm  |  ESC Back",
                                font_small, DIM, HEIGHT - 40, shadow=False)

    def draw_difficulty_select(self, surface):
        surface.fill(BG)
        for p in self.menu_particles:
            p.draw(surface)
        self.draw_text_centered(surface, "SELECT DIFFICULTY", font_big, CYAN, 80)

        diffs = [
            ("EASY", "Slow AI, forgiving", GREEN),
            ("NORMAL", "Balanced challenge", YELLOW),
            ("HARD", "Fast, smart AI", ORANGE),
            ("INSANE", "Near perfect AI", RED),
        ]
        for i, (name, desc, color) in enumerate(diffs):
            y = 200 + i * 90
            c = YELLOW if i == self.selected_diff else color
            pygame.draw.rect(surface, (20, 20, 40),
                             (WIDTH // 2 - 200, y - 30, 400, 70), border_radius=10)
            if i == self.selected_diff:
                pygame.draw.rect(surface, YELLOW,
                                 (WIDTH // 2 - 200, y - 30, 400, 70), 3, border_radius=10)
            txt = font_big.render(name, True, c)
            surface.blit(txt, (WIDTH // 2 - 180, y - 20))
            d = font_small.render(desc, True, DIM)
            surface.blit(d, (WIDTH // 2 - 180, y + 15))

        self.draw_text_centered(surface, "UP/DOWN Select  |  ENTER Confirm  |  ESC Back",
                                font_small, DIM, HEIGHT - 40, shadow=False)

    def draw_playing(self, surface):
        self.draw_background(surface)
        for p in self.particles:
            p.draw(surface)
        self.left_paddle.draw(surface)
        self.right_paddle.draw(surface)
        for b in self.balls:
            b.draw(surface)
        for ft in self.floating_texts:
            ft.draw(surface)

        s1 = font_big.render(str(self.score_left), True, CYAN)
        s2 = font_big.render(str(self.score_right), True, PINK)
        surface.blit(s1, (WIDTH // 2 - 100, 20))
        surface.blit(s2, (WIDTH // 2 + 60, 20))

        mode_txt = font_small.render(self.mode.value, True, DIM)
        surface.blit(mode_txt, (20, 20))

        if self.combo_left >= 3:
            c = font_small.render(f"COMBO x{self.combo_left}", True, YELLOW)
            surface.blit(c, (20, 50))
        if self.combo_right >= 3:
            c = font_small.render(f"COMBO x{self.combo_right}", True, YELLOW)
            rect = c.get_rect(topright=(WIDTH - 20, 50))
            surface.blit(c, rect)

        if self.mode == GameMode.TIME_ATTACK:
            t = max(0.0, self.time_attack_time)
            color = RED if t < 5 else YELLOW
            txt = font_big.render(f"TIME: {t:.1f}s", True, color)
            rect = txt.get_rect(center=(WIDTH // 2, 80))
            surface.blit(txt, rect)
            score = font_med.render(f"SCORE: {self.time_attack_score}", True, GREEN)
            rect = score.get_rect(center=(WIDTH // 2, 120))
            surface.blit(score, rect)

        if self.mode == GameMode.SURVIVAL:
            txt = font_med.render(f"TIME: {self.survival_time:.1f}s", True, GREEN)
            rect = txt.get_rect(center=(WIDTH // 2, 80))
            surface.blit(txt, rect)

    def draw_paused(self, surface):
        self.draw_playing(surface)
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        surface.blit(overlay, (0, 0))
        self.draw_text_centered(surface, "PAUSED", font_title, YELLOW, HEIGHT // 2 - 40)
        self.draw_text_centered(surface, "P - Resume  |  ESC - Quit to Menu",
                                font_med, WHITE, HEIGHT // 2 + 40)

    def draw_gameover(self, surface):
        self.draw_playing(surface)
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        surface.blit(overlay, (0, 0))

        if self.winner in ("YOU", "PLAYER 1"):
            color = CYAN
        elif self.winner == "TIME UP":
            color = ORANGE
        else:
            color = PINK

        title_text = f"{self.winner} WINS!" if self.winner != "TIME UP" else "TIME UP!"
        self.draw_text_centered(surface, title_text, font_title, color, 120)

        if self.mode != GameMode.TIME_ATTACK:
            self.draw_text_centered(surface, f"{self.score_left}  -  {self.score_right}",
                                    font_big, WHITE, 200)

        stats_y = 280
        self.draw_text_centered(surface, "MATCH STATS", font_med, YELLOW, stats_y)
        stats_y += 40
        self.draw_text_centered(surface, f"Max Combo: {self.max_combo_left}",
                                font_small, WHITE, stats_y)
        stats_y += 30
        self.draw_text_centered(surface, f"Total Hits: {self.hits_left}",
                                font_small, WHITE, stats_y)
        stats_y += 30
        self.draw_text_centered(surface, f"Match Time: {self.game_time:.1f}s",
                                font_small, WHITE, stats_y)

        if self.mode == GameMode.SURVIVAL:
            stats_y += 40
            self.draw_text_centered(surface,
                                    f"Survival Time: {self.survival_time:.1f}s",
                                    font_med, GREEN, stats_y)
        elif self.mode == GameMode.TIME_ATTACK:
            stats_y += 40
            self.draw_text_centered(surface,
                                    f"Final Score: {self.time_attack_score}",
                                    font_med, ORANGE, stats_y)

        self.draw_text_centered(surface, "R - Play Again  |  ESC - Menu",
                                font_med, WHITE, HEIGHT - 60)

    def draw_highscores(self, surface):
        surface.fill(BG)
        for p in self.menu_particles:
            p.draw(surface)
        self.draw_text_centered(surface, "HIGH SCORES", font_big, CYAN, 60)

        categories = [
            ("VS AI (Combo)", "VS_AI",
             lambda x: f"C:{x.get('combo', 0)} | {x.get('score', '')} | {x.get('difficulty', '')}"),
            ("SURVIVAL (Time)", "SURVIVAL",
             lambda x: f"T:{x.get('time', 0)}s | S:{x.get('score', 0)}"),
            ("TIME ATTACK", "TIME_ATTACK",
             lambda x: f"Score: {x.get('score', 0)}"),
        ]

        x_offset = 40
        for title, key, formatter in categories:
            txt = font_med.render(title, True, YELLOW)
            surface.blit(txt, (x_offset, 120))
            entries = self.scores.get(key, [])
            if not entries:
                no = font_small.render("No scores yet", True, DIM)
                surface.blit(no, (x_offset, 160))
            else:
                for i, entry in enumerate(entries[:5]):
                    line = f"{i + 1}. {formatter(entry)}"
                    t = font_small.render(line, True, WHITE)
                    surface.blit(t, (x_offset, 160 + i * 28))
            x_offset += 320

        self.draw_text_centered(surface, "ESC - Back",
                                font_small, DIM, HEIGHT - 40, shadow=False)

    def draw(self, surface):
        offset_x = 0
        offset_y = 0
        if self.shake > 0:
            offset_x = random.randint(-self.shake, self.shake)
            offset_y = random.randint(-self.shake, self.shake)
            self.shake = max(0, self.shake - 1)

        game_surface = pygame.Surface((WIDTH, HEIGHT))

        if self.state == GameState.MENU:
            self.draw_menu(game_surface)
        elif self.state == GameState.MODE_SELECT:
            self.draw_mode_select(game_surface)
        elif self.state == GameState.DIFFICULTY_SELECT:
            self.draw_difficulty_select(game_surface)
        elif self.state == GameState.PLAYING:
            self.draw_playing(game_surface)
        elif self.state == GameState.PAUSED:
            self.draw_paused(game_surface)
        elif self.state == GameState.GAMEOVER:
            self.draw_gameover(game_surface)
        elif self.state == GameState.HIGHSCORES:
            self.draw_highscores(game_surface)

        surface.blit(game_surface, (offset_x, offset_y))

    def update(self, dt, keys):
        self.particles = [p for p in self.particles if p.update(dt)]
        self.floating_texts = [ft for ft in self.floating_texts if ft.update(dt)]

        if self.state == GameState.PLAYING:
            self.update_playing(dt, keys)


def main():
    game = Game()
    running = True

    while running:
        dt = clock.tick(FPS) / 1000.0
        dt = min(dt, 0.05)
        keys = pygame.key.get_pressed()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if game.state == GameState.MENU:
                    if event.key == pygame.K_UP:
                        game.selected_menu = (game.selected_menu - 1) % 3
                    elif event.key == pygame.K_DOWN:
                        game.selected_menu = (game.selected_menu + 1) % 3
                    elif event.key == pygame.K_RETURN:
                        if game.selected_menu == 0:
                            game.state = GameState.MODE_SELECT
                        elif game.selected_menu == 1:
                            game.state = GameState.HIGHSCORES
                        elif game.selected_menu == 2:
                            running = False

                elif game.state == GameState.MODE_SELECT:
                    if event.key == pygame.K_UP:
                        game.selected_mode = (game.selected_mode - 1) % 4
                    elif event.key == pygame.K_DOWN:
                        game.selected_mode = (game.selected_mode + 1) % 4
                    elif event.key == pygame.K_RETURN:
                        mode_list = [GameMode.VS_AI, GameMode.TWO_PLAYER,
                                     GameMode.SURVIVAL, GameMode.TIME_ATTACK]
                        game.mode = mode_list[game.selected_mode]
                        if game.mode == GameMode.VS_AI:
                            game.state = GameState.DIFFICULTY_SELECT
                        else:
                            game.difficulty = Difficulty.NORMAL
                            game.reset_game()
                            game.state = GameState.PLAYING
                    elif event.key == pygame.K_ESCAPE:
                        game.state = GameState.MENU

                elif game.state == GameState.DIFFICULTY_SELECT:
                    if event.key == pygame.K_UP:
                        game.selected_diff = (game.selected_diff - 1) % 4
                    elif event.key == pygame.K_DOWN:
                        game.selected_diff = (game.selected_diff + 1) % 4
                    elif event.key == pygame.K_RETURN:
                        diff_list = [Difficulty.EASY, Difficulty.NORMAL,
                                     Difficulty.HARD, Difficulty.INSANE]
                        game.difficulty = diff_list[game.selected_diff]
                        game.reset_game()
                        game.state = GameState.PLAYING
                    elif event.key == pygame.K_ESCAPE:
                        game.state = GameState.MODE_SELECT

                elif game.state == GameState.PLAYING:
                    if event.key == pygame.K_p:
                        game.state = GameState.PAUSED
                    elif event.key == pygame.K_ESCAPE:
                        game.state = GameState.PAUSED

                elif game.state == GameState.PAUSED:
                    if event.key == pygame.K_p:
                        game.state = GameState.PLAYING
                    elif event.key == pygame.K_ESCAPE:
                        game.state = GameState.MENU

                elif game.state == GameState.GAMEOVER:
                    if event.key == pygame.K_r:
                        game.reset_game()
                        game.state = GameState.PLAYING
                    elif event.key == pygame.K_ESCAPE:
                        game.state = GameState.MENU

                elif game.state == GameState.HIGHSCORES:
                    if event.key == pygame.K_ESCAPE:
                        game.state = GameState.MENU

        game.update(dt, keys)
        game.draw(screen)
        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()