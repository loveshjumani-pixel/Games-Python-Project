"""
ZOMBIE SIEGE — Advanced single-file Python zombie shooter
Engine: pygame

Chalane ka tareeqa:
    pip install pygame
    python zombie_siege.py

Sab kuch is ek file me hai — koi image ya sound file nahi chahiye.
Graphics procedurally draw hote hain: dynamic lighting/flashlight, blood
decals, particle system, screen shake, minimap, floating damage numbers.

CONTROLS
    WASD / Arrow keys   - Move
    Mouse               - Aim
    Left Click (hold)   - Shoot
    R                   - Reload
    Left Shift          - Sprint
    1 / 2 / 3 / 4        - Switch weapon (Pistol / SMG / Shotgun / Rifle)
    ESC                 - Pause
    ENTER               - Start / Restart
"""

import sys
import math
import random
from dataclasses import dataclass

import pygame
from pygame.math import Vector2

# ============================== CONFIG ================================

WIDTH, HEIGHT = 1280, 720
WORLD_W, WORLD_H = 3200, 3200
FPS = 60

DARK_BG = (10, 12, 16)
FLOOR_A = (34, 38, 34)
FLOOR_B = (28, 32, 28)
BLOOD = (130, 12, 14)
UI_BG = (12, 16, 22)
UI_BORDER = (60, 80, 110)
TEXT_MAIN = (235, 240, 248)
TEXT_MUTED = (140, 155, 175)
HEALTH_GOOD = (80, 210, 120)
HEALTH_MID = (240, 190, 70)
HEALTH_LOW = (230, 70, 70)
ACCENT = (90, 160, 255)


def clamp(value, low, high):
    return max(low, min(high, value))


def lerp(a, b, t):
    return a + (b - a) * t


# ===================== PRECOMPUTED LIGHT SURFACES ======================
# Ek hi dafa banate hain, phir har frame reuse — is se lighting sasti par
# behtar lagti hai. Bare circle radius se chhote radius tak draw karte hain,
# taake center chamakdaar aur kinaray dheere dheere gaib ho jayein.

def make_light_surface(radius, color=(255, 235, 190), max_alpha=235):
    surf = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
    for r in range(radius, 0, -2):
        t = 1 - (r / radius)
        alpha = int(max_alpha * (t ** 1.6))
        pygame.draw.circle(surf, (*color, alpha), (radius, radius), r)
    return surf


def make_vignette(width, height, strength=150):
    surf = pygame.Surface((width, height), pygame.SRCALPHA)
    max_r = int(math.hypot(width / 2, height / 2))
    for r in range(max_r, 0, -6):
        t = r / max_r
        alpha = int(strength * (t ** 2.2))
        pygame.draw.circle(surf, (0, 0, 0, alpha), (width // 2, height // 2), r)
    return surf


# =============================== WEAPONS ================================

@dataclass
class WeaponType:
    name: str
    damage: float
    fire_rate: float      # shots per second
    spread: float         # degrees
    bullet_speed: float
    pellets: int = 1
    mag_size: int = 12
    reload_time: float = 1.1
    color: tuple = (255, 225, 130)
    tracer_len: int = 14


WEAPONS = {
    "pistol":  WeaponType("Pistol",  damage=24, fire_rate=4.2, spread=2.5,
                          bullet_speed=980, pellets=1, mag_size=12,
                          reload_time=0.9, color=(255, 225, 130)),
    "smg":     WeaponType("SMG",     damage=11, fire_rate=11.0, spread=6.5,
                          bullet_speed=1020, pellets=1, mag_size=30,
                          reload_time=1.5, color=(160, 220, 255)),
    "shotgun": WeaponType("Shotgun", damage=10, fire_rate=1.5, spread=16,
                          bullet_speed=880, pellets=7, mag_size=6,
                          reload_time=1.8, color=(255, 150, 90), tracer_len=9),
    "rifle":   WeaponType("Rifle",   damage=46, fire_rate=2.8, spread=1.2,
                          bullet_speed=1450, pellets=1, mag_size=8,
                          reload_time=1.6, color=(180, 255, 170), tracer_len=22),
}
WEAPON_ORDER = ["pistol", "smg", "shotgun", "rifle"]


# =============================== PARTICLES ==============================

class Particle:
    __slots__ = ("pos", "vel", "life", "max_life", "size", "color", "gravity", "kind")

    def __init__(self, pos, vel, life, size, color, gravity=0.0, kind="dot"):
        self.pos = Vector2(pos)
        self.vel = Vector2(vel)
        self.life = life
        self.max_life = life
        self.size = size
        self.color = color
        self.gravity = gravity
        self.kind = kind

    def update(self, dt):
        self.vel *= 0.90
        self.vel.y += self.gravity * dt
        self.pos += self.vel * dt
        self.life -= dt
        return self.life > 0

    def draw(self, surface, camera):
        t = clamp(self.life / self.max_life, 0, 1)
        screen_pos = camera.to_screen(self.pos)
        size = max(1, int(self.size * t))
        alpha = int(255 * t)
        color = (*self.color, alpha)
        glow = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
        pygame.draw.circle(glow, color, (size, size), size)
        surface.blit(glow, (screen_pos.x - size, screen_pos.y - size))


class FloatingText:
    __slots__ = ("pos", "text", "life", "max_life", "color", "vel")

    def __init__(self, pos, text, color=(255, 235, 120)):
        self.pos = Vector2(pos)
        self.vel = Vector2(random.uniform(-15, 15), -60)
        self.text = text
        self.life = 0.8
        self.max_life = 0.8
        self.color = color

    def update(self, dt):
        self.pos += self.vel * dt
        self.vel *= 0.95
        self.life -= dt
        return self.life > 0


class ParticleSystem:
    def __init__(self):
        self.particles = []
        self.texts = []

    def burst(self, pos, count, color, speed_range=(60, 260), life_range=(0.25, 0.6),
             size_range=(2, 5), gravity=0.0, kind="dot"):
        for _ in range(count):
            angle = random.uniform(0, 360)
            speed = random.uniform(*speed_range)
            vel = Vector2(speed, 0).rotate(angle)
            life = random.uniform(*life_range)
            size = random.uniform(*size_range)
            self.particles.append(Particle(pos, vel, life, size, color, gravity, kind))

    def floating_text(self, pos, text, color=(255, 235, 120)):
        self.texts.append(FloatingText(pos, text, color))

    def update(self, dt):
        self.particles = [p for p in self.particles if p.update(dt)]
        self.texts = [t for t in self.texts if t.update(dt)]
        # Perf ehtiyat: kabhi bohot zyada particles jama ho jayein to purane hata do.
        if len(self.particles) > 500:
            self.particles = self.particles[-500:]

    def draw(self, surface, camera, font):
        for p in self.particles:
            p.draw(surface, camera)
        for t in self.texts:
            alpha = int(255 * clamp(t.life / t.max_life, 0, 1))
            screen_pos = camera.to_screen(t.pos)
            label = font.render(t.text, True, t.color)
            label.set_alpha(alpha)
            surface.blit(label, (screen_pos.x - label.get_width() / 2, screen_pos.y))


# =============================== CAMERA ==================================

class Camera:
    def __init__(self):
        self.offset = Vector2(0, 0)
        self.shake_time = 0.0
        self.shake_strength = 0.0
        self.shake_offset = Vector2(0, 0)

    def follow(self, target_pos):
        desired = target_pos - Vector2(WIDTH / 2, HEIGHT / 2)
        desired.x = clamp(desired.x, 0, WORLD_W - WIDTH)
        desired.y = clamp(desired.y, 0, WORLD_H - HEIGHT)
        self.offset = self.offset.lerp(desired, 0.15)

    def shake(self, strength, duration):
        self.shake_strength = max(self.shake_strength, strength)
        self.shake_time = max(self.shake_time, duration)

    def update(self, dt):
        if self.shake_time > 0:
            self.shake_time -= dt
            magnitude = self.shake_strength * (self.shake_time / max(0.001, self.shake_time + dt))
            self.shake_offset = Vector2(random.uniform(-1, 1), random.uniform(-1, 1)) * magnitude
        else:
            self.shake_offset = Vector2(0, 0)

    def to_screen(self, world_pos):
        return Vector2(world_pos) - self.offset + self.shake_offset

    def to_world(self, screen_pos):
        return Vector2(screen_pos) + self.offset - self.shake_offset


# =============================== BULLET ==================================

class Bullet:
    __slots__ = ("pos", "vel", "damage", "color", "traveled", "max_range", "tracer_len", "dead")

    def __init__(self, pos, vel, damage, color, tracer_len=14, max_range=1100):
        self.pos = Vector2(pos)
        self.vel = Vector2(vel)
        self.damage = damage
        self.color = color
        self.traveled = 0.0
        self.max_range = max_range
        self.tracer_len = tracer_len
        self.dead = False

    def update(self, dt):
        step = self.vel * dt
        self.pos += step
        self.traveled += step.length()
        if self.traveled > self.max_range:
            self.dead = True
        if not (0 <= self.pos.x <= WORLD_W and 0 <= self.pos.y <= WORLD_H):
            self.dead = True

    def draw(self, surface, camera):
        screen_pos = camera.to_screen(self.pos)
        if self.vel.length_squared() > 0:
            tail_dir = self.vel.normalize() * -self.tracer_len
        else:
            tail_dir = Vector2(0, 0)
        tail = screen_pos + tail_dir
        pygame.draw.line(surface, self.color, tail, screen_pos, 3)
        pygame.draw.circle(surface, (255, 255, 255), (int(screen_pos.x), int(screen_pos.y)), 2)


# =============================== ZOMBIES ==================================

ZOMBIE_STATS = {
    "walker": dict(hp=42, speed=92, damage=9, radius=17,
                   body=(70, 110, 60), dark=(35, 60, 30), score=10),
    "runner": dict(hp=28, speed=175, damage=6, radius=14,
                   body=(140, 150, 40), dark=(75, 80, 20), score=16),
    "brute":  dict(hp=190, speed=58, damage=20, radius=27,
                   body=(90, 55, 55), dark=(45, 25, 25), score=45),
}


class Zombie:
    def __init__(self, kind, pos, wave):
        stats = ZOMBIE_STATS[kind]
        self.kind = kind
        self.pos = Vector2(pos)
        self.vel = Vector2(0, 0)
        scale = 1 + wave * 0.045
        self.max_hp = stats["hp"] * scale
        self.hp = self.max_hp
        self.speed = stats["speed"] * (1 + wave * 0.012)
        self.damage = stats["damage"]
        self.radius = stats["radius"]
        self.body_color = stats["body"]
        self.dark_color = stats["dark"]
        self.score_value = stats["score"]
        self.attack_cooldown = 0.0
        self.hit_flash = 0.0
        self.phase = random.uniform(0, 6.28)
        self.dead = False

    def update(self, dt, player, others, sim_time):
        to_player = player.pos - self.pos
        dist = to_player.length()
        direction = to_player.normalize() if dist > 1e-3 else Vector2(0, 0)

        # Halka separation, taake zombies ek hi jagah dher na ho jayein.
        push = Vector2(0, 0)
        for other in others:
            if other is self:
                continue
            diff = self.pos - other.pos
            d = diff.length()
            if 0 < d < (self.radius + other.radius) * 1.1:
                push += diff.normalize() * (1 - d / ((self.radius + other.radius) * 1.1))

        self.vel = direction * self.speed + push * 140
        self.pos += self.vel * dt

        self.pos.x = clamp(self.pos.x, self.radius, WORLD_W - self.radius)
        self.pos.y = clamp(self.pos.y, self.radius, WORLD_H - self.radius)

        if self.attack_cooldown > 0:
            self.attack_cooldown -= dt
        if self.hit_flash > 0:
            self.hit_flash -= dt

        if dist < self.radius + player.radius and self.attack_cooldown <= 0:
            player.take_damage(self.damage)
            self.attack_cooldown = 0.7
            return "attacked"
        return None

    def take_damage(self, amount):
        self.hp -= amount
        self.hit_flash = 0.12
        if self.hp <= 0:
            self.dead = True

    def draw(self, surface, camera, sim_time):
        screen_pos = camera.to_screen(self.pos)
        wobble = math.sin(sim_time * 8 + self.phase) * 3

        body_color = (255, 255, 255) if self.hit_flash > 0 else self.body_color
        dark_color = self.dark_color

        # Peray (limbs) — chalte hue hilte hain.
        for side in (-1, 1):
            leg_end = screen_pos + Vector2(side * 8, 16 + wobble * side)
            pygame.draw.line(surface, dark_color, screen_pos + Vector2(side * 4, 6),
                             leg_end, 5)

        # Jism
        pygame.draw.circle(surface, body_color, (int(screen_pos.x), int(screen_pos.y)),
                           self.radius)
        pygame.draw.circle(surface, dark_color, (int(screen_pos.x), int(screen_pos.y)),
                           self.radius, 2)

        # Sar
        head_pos = screen_pos + Vector2(0, -self.radius * 0.75)
        pygame.draw.circle(surface, body_color, (int(head_pos.x), int(head_pos.y)),
                           int(self.radius * 0.55))

        # Chamakti aankhein — glow ka bhram
        eye_color = (255, 40, 40)
        pygame.draw.circle(surface, eye_color, (int(head_pos.x - 4), int(head_pos.y - 2)), 3)
        pygame.draw.circle(surface, eye_color, (int(head_pos.x + 4), int(head_pos.y - 2)), 3)

        # Health bar (chhota, sar ke upar) — sirf zakhmi hone par dikhta hai
        if self.hp < self.max_hp:
            bar_w = self.radius * 2
            ratio = clamp(self.hp / self.max_hp, 0, 1)
            top_left = screen_pos + Vector2(-self.radius, -self.radius - 14)
            pygame.draw.rect(surface, (40, 15, 15), (*top_left, bar_w, 4))
            pygame.draw.rect(surface, (210, 60, 60), (*top_left, bar_w * ratio, 4))


def choose_zombie_kind(wave):
    roll = random.random()
    if wave >= 5 and roll < 0.14:
        return "brute"
    if wave >= 2 and roll < 0.14 + 0.28:
        return "runner"
    return "walker"


# =============================== PICKUPS ==================================

PICKUP_COLORS = {
    "health": (90, 220, 120),
    "ammo": (230, 200, 90),
    "weapon_smg": (150, 210, 255),
    "weapon_shotgun": (255, 150, 90),
    "weapon_rifle": (180, 255, 170),
}
PICKUP_LABELS = {
    "health": "+", "ammo": "A",
    "weapon_smg": "S", "weapon_shotgun": "G", "weapon_rifle": "R",
}


class Pickup:
    def __init__(self, kind, pos):
        self.kind = kind
        self.pos = Vector2(pos)
        self.radius = 15
        self.phase = random.uniform(0, 6.28)
        self.dead = False

    def draw(self, surface, camera, sim_time, font):
        bob = math.sin(sim_time * 3 + self.phase) * 4
        screen_pos = camera.to_screen(self.pos) + Vector2(0, bob)
        color = PICKUP_COLORS[self.kind]
        pygame.draw.circle(surface, color, (int(screen_pos.x), int(screen_pos.y)), self.radius)
        pygame.draw.circle(surface, (255, 255, 255), (int(screen_pos.x), int(screen_pos.y)),
                           self.radius, 2)
        label = font.render(PICKUP_LABELS[self.kind], True, (20, 20, 20))
        rect = label.get_rect(center=(screen_pos.x, screen_pos.y))
        surface.blit(label, rect)


# ================================ PLAYER ==================================

class Player:
    def __init__(self, pos):
        self.pos = Vector2(pos)
        self.radius = 18
        self.base_speed = 250
        self.sprint_mult = 1.55
        self.stamina = 100.0
        self.max_health = 100.0
        self.health = self.max_health
        self.invuln = 0.0

        self.owned = {"pistol": True}
        self.mag = {name: 0 for name in WEAPON_ORDER}
        self.mag["pistol"] = WEAPONS["pistol"].mag_size
        self.reserve = {name: 0.0 for name in WEAPON_ORDER}
        self.reserve["pistol"] = float("inf")
        self.current = "pistol"

        self.fire_cooldown = 0.0
        self.reload_timer = 0.0
        self.aim_dir = Vector2(1, 0)

        self.score = 0
        self.kills = 0

    @property
    def weapon(self):
        return WEAPONS[self.current]

    def move(self, keys, dt):
        move = Vector2(0, 0)
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            move.y -= 1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            move.y += 1
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            move.x -= 1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            move.x += 1

        sprinting = (keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]) and self.stamina > 5
        speed = self.base_speed * (self.sprint_mult if sprinting and move.length_squared() > 0 else 1)

        if move.length_squared() > 0:
            move = move.normalize() * speed
            if sprinting:
                self.stamina = max(0, self.stamina - 35 * dt)
        else:
            self.stamina = min(100, self.stamina + 18 * dt)

        if not sprinting:
            self.stamina = min(100, self.stamina + 10 * dt)

        self.pos += move * dt
        self.pos.x = clamp(self.pos.x, self.radius, WORLD_W - self.radius)
        self.pos.y = clamp(self.pos.y, self.radius, WORLD_H - self.radius)

    def start_reload(self):
        weapon = self.weapon
        if self.reload_timer <= 0 and self.mag[self.current] < weapon.mag_size \
           and self.reserve[self.current] > 0:
            self.reload_timer = weapon.reload_time

    def switch_weapon(self, key_index):
        if 0 <= key_index < len(WEAPON_ORDER):
            name = WEAPON_ORDER[key_index]
            if self.owned.get(name):
                self.current = name
                self.reload_timer = 0.0

    def try_shoot(self, mouse_world):
        weapon = self.weapon
        if self.reload_timer > 0 or self.fire_cooldown > 0:
            return None
        if self.mag[self.current] <= 0:
            self.start_reload()
            return None

        aim = mouse_world - self.pos
        if aim.length_squared() < 1:
            aim = self.aim_dir
        aim = aim.normalize()
        self.aim_dir = aim

        bullets = []
        for _ in range(weapon.pellets):
            spread_deg = random.uniform(-weapon.spread, weapon.spread)
            direction = aim.rotate(spread_deg)
            spawn_pos = self.pos + aim * (self.radius + 10)
            bullets.append(Bullet(spawn_pos, direction * weapon.bullet_speed,
                                  weapon.damage, weapon.color, weapon.tracer_len))

        self.mag[self.current] -= 1
        self.fire_cooldown = 1.0 / weapon.fire_rate
        return bullets

    def update(self, dt):
        if self.fire_cooldown > 0:
            self.fire_cooldown -= dt
        if self.invuln > 0:
            self.invuln -= dt

        if self.reload_timer > 0:
            self.reload_timer -= dt
            if self.reload_timer <= 0:
                weapon = self.weapon
                needed = weapon.mag_size - self.mag[self.current]
                available = self.reserve[self.current]
                take = needed if available == float("inf") else min(needed, available)
                self.mag[self.current] += take
                if self.reserve[self.current] != float("inf"):
                    self.reserve[self.current] -= take

    def take_damage(self, amount):
        if self.invuln > 0:
            return
        self.health -= amount
        self.invuln = 0.5

    def heal(self, amount):
        self.health = min(self.max_health, self.health + amount)

    def collect_pickup(self, kind):
        if kind == "health":
            self.heal(35)
        elif kind == "ammo":
            for name in WEAPON_ORDER:
                if self.owned.get(name) and self.reserve[name] != float("inf"):
                    self.reserve[name] += WEAPONS[name].mag_size * 1.5
        else:
            weapon_name = kind.replace("weapon_", "")
            first_time = not self.owned.get(weapon_name)
            self.owned[weapon_name] = True
            self.reserve[weapon_name] += WEAPONS[weapon_name].mag_size * 2.5
            if first_time:
                self.mag[weapon_name] = WEAPONS[weapon_name].mag_size
                self.current = weapon_name

    def draw(self, surface, camera):
        screen_pos = camera.to_screen(self.pos)
        flash = self.invuln > 0 and int(self.invuln * 20) % 2 == 0
        color = (255, 160, 160) if flash else (225, 230, 240)

        gun_end = screen_pos + self.aim_dir * (self.radius + 22)
        pygame.draw.line(surface, (40, 40, 45), screen_pos, gun_end, 6)

        pygame.draw.circle(surface, (30, 55, 90), (int(screen_pos.x), int(screen_pos.y)),
                           self.radius + 3)
        pygame.draw.circle(surface, color, (int(screen_pos.x), int(screen_pos.y)), self.radius)
        pygame.draw.circle(surface, ACCENT, (int(screen_pos.x), int(screen_pos.y)),
                           self.radius, 2)


# ============================== WAVE MANAGER ==============================

class WaveManager:
    def __init__(self):
        self.wave = 0
        self.state = "intermission"
        self.between_wave_timer = 3.0
        self.zombies_to_spawn = 0
        self.spawn_timer = 0.0
        self.spawn_interval = 1.0
        self.banner_text = "GET READY"
        self.banner_timer = 2.0

    def start_next_wave(self):
        self.wave += 1
        self.zombies_to_spawn = 5 + self.wave * 3
        self.spawn_interval = max(0.22, 1.15 - self.wave * 0.05)
        self.state = "spawning"
        self.banner_text = f"WAVE {self.wave}"
        self.banner_timer = 2.2

    def update(self, dt, game):
        if self.banner_timer > 0:
            self.banner_timer -= dt

        if self.state == "intermission":
            self.between_wave_timer -= dt
            if self.between_wave_timer <= 0:
                self.start_next_wave()

        elif self.state == "spawning":
            self.spawn_timer -= dt
            if self.spawn_timer <= 0 and self.zombies_to_spawn > 0:
                game.spawn_zombie(self.wave)
                self.zombies_to_spawn -= 1
                self.spawn_timer = self.spawn_interval
            if self.zombies_to_spawn <= 0:
                self.state = "clearing"

        elif self.state == "clearing":
            if not game.zombies:
                self.state = "intermission"
                self.between_wave_timer = 4.0
                game.player.heal(18)
                game.spawn_pickup(force=True)


# ================================= HUD ====================================

def draw_bar(surface, pos, size, ratio, color_good, color_mid, color_low, bg=(25, 20, 20)):
    x, y = pos
    w, h = size
    pygame.draw.rect(surface, bg, (x, y, w, h), border_radius=4)
    ratio = clamp(ratio, 0, 1)
    if ratio > 0.5:
        color = color_good
    elif ratio > 0.25:
        color = color_mid
    else:
        color = color_low
    if ratio > 0:
        pygame.draw.rect(surface, color, (x, y, w * ratio, h), border_radius=4)
    pygame.draw.rect(surface, UI_BORDER, (x, y, w, h), 2, border_radius=4)


class HUD:
    def __init__(self):
        self.font_small = pygame.font.SysFont("consolas", 16)
        self.font_med = pygame.font.SysFont("consolas", 22, bold=True)
        self.font_big = pygame.font.SysFont("consolas", 46, bold=True)
        self.font_title = pygame.font.SysFont("consolas", 64, bold=True)

    def draw_playing(self, surface, player, wave, camera, zombies, sim_time):
        # Health
        draw_bar(surface, (24, HEIGHT - 54), (260, 22),
                player.health / player.max_health,
                HEALTH_GOOD, HEALTH_MID, HEALTH_LOW)
        label = self.font_small.render(
            f"HP {max(0, int(player.health))}/{int(player.max_health)}", True, TEXT_MAIN)
        surface.blit(label, (30, HEIGHT - 52))

        # Stamina
        draw_bar(surface, (24, HEIGHT - 26), (260, 10),
                player.stamina / 100, (90, 170, 255), (90, 170, 255), (90, 170, 255))

        # Weapon / ammo
        weapon = player.weapon
        ammo_text = "RELOADING..." if player.reload_timer > 0 else \
            f"{int(player.mag[player.current])} / " + \
            ("∞" if player.reserve[player.current] == float("inf")
             else str(int(player.reserve[player.current])))
        weapon_panel = pygame.Surface((230, 64), pygame.SRCALPHA)
        pygame.draw.rect(weapon_panel, (*UI_BG, 210), (0, 0, 230, 64), border_radius=8)
        pygame.draw.rect(weapon_panel, UI_BORDER, (0, 0, 230, 64), 2, border_radius=8)
        weapon_panel.blit(self.font_med.render(weapon.name.upper(), True, TEXT_MAIN), (14, 8))
        ammo_color = (255, 120, 120) if player.reload_timer > 0 else TEXT_MAIN
        weapon_panel.blit(self.font_small.render(ammo_text, True, ammo_color), (14, 36))
        surface.blit(weapon_panel, (WIDTH - 250, HEIGHT - 84))

        # Score / kills / wave
        top_panel = pygame.Surface((300, 90), pygame.SRCALPHA)
        pygame.draw.rect(top_panel, (*UI_BG, 200), (0, 0, 300, 90), border_radius=8)
        pygame.draw.rect(top_panel, UI_BORDER, (0, 0, 300, 90), 2, border_radius=8)
        top_panel.blit(self.font_med.render(f"WAVE {wave.wave}", True, ACCENT), (14, 8))
        top_panel.blit(self.font_small.render(f"Score: {player.score}", True, TEXT_MUTED), (14, 38))
        top_panel.blit(self.font_small.render(f"Kills: {player.kills}", True, TEXT_MUTED), (14, 58))
        surface.blit(top_panel, (24, 20))

        # Wave banner
        if wave.banner_timer > 0:
            t = clamp(wave.banner_timer / 2.2, 0, 1)
            label = self.font_title.render(wave.banner_text, True, (255, 240, 200))
            label.set_alpha(int(255 * t))
            rect = label.get_rect(center=(WIDTH / 2, HEIGHT * 0.28))
            surface.blit(label, rect)

        self.draw_minimap(surface, player, zombies, camera)

    def draw_minimap(self, surface, player, zombies, camera):
        panel_size = 160
        margin = 20
        cx = WIDTH - panel_size / 2 - margin
        cy = panel_size / 2 + margin
        panel = pygame.Surface((panel_size, panel_size), pygame.SRCALPHA)
        pygame.draw.circle(panel, (*UI_BG, 190), (panel_size // 2, panel_size // 2), panel_size // 2)
        pygame.draw.circle(panel, UI_BORDER, (panel_size // 2, panel_size // 2), panel_size // 2, 2)
        scale = 0.045
        for zombie in zombies:
            rel = (zombie.pos - player.pos) * scale
            if rel.length() < panel_size / 2 - 6:
                pos = (panel_size / 2 + rel.x, panel_size / 2 + rel.y)
                pygame.draw.circle(panel, (230, 70, 70), pos, 3)
        pygame.draw.circle(panel, (255, 255, 255), (panel_size // 2, panel_size // 2), 4)
        surface.blit(panel, (cx - panel_size / 2, cy - panel_size / 2))

    def draw_menu(self, surface, sim_time):
        title = self.font_title.render("ZOMBIE SIEGE", True, (230, 60, 60))
        pulse = 1 + 0.03 * math.sin(sim_time * 3)
        title = pygame.transform.smoothscale(
            title, (int(title.get_width() * pulse), int(title.get_height() * pulse)))
        rect = title.get_rect(center=(WIDTH / 2, HEIGHT * 0.32))
        surface.blit(title, rect)

        sub = self.font_med.render("An advanced top-down survival shooter", True, TEXT_MUTED)
        surface.blit(sub, sub.get_rect(center=(WIDTH / 2, HEIGHT * 0.32 + 60)))

        lines = [
            "WASD / Arrows — Move       Mouse — Aim       Left Click — Shoot",
            "R — Reload      Shift — Sprint      1-4 — Switch Weapon      ESC — Pause",
            "",
            "Press ENTER to start",
        ]
        for index, line in enumerate(lines):
            color = (255, 235, 150) if index == 3 else TEXT_MUTED
            font = self.font_med if index == 3 else self.font_small
            label = font.render(line, True, color)
            surface.blit(label, label.get_rect(center=(WIDTH / 2, HEIGHT * 0.6 + index * 34)))

    def draw_pause(self, surface):
        label = self.font_big.render("PAUSED", True, TEXT_MAIN)
        surface.blit(label, label.get_rect(center=(WIDTH / 2, HEIGHT / 2 - 20)))
        sub = self.font_small.render("Press ESC to resume", True, TEXT_MUTED)
        surface.blit(sub, sub.get_rect(center=(WIDTH / 2, HEIGHT / 2 + 30)))

    def draw_game_over(self, surface, player, wave):
        label = self.font_title.render("YOU DIED", True, (230, 60, 60))
        surface.blit(label, label.get_rect(center=(WIDTH / 2, HEIGHT * 0.32)))

        stats = [
            f"Waves survived: {wave.wave}",
            f"Zombies killed: {player.kills}",
            f"Final score: {player.score}",
            "",
            "Press ENTER to play again",
        ]
        for index, line in enumerate(stats):
            color = (255, 235, 150) if index == 4 else TEXT_MUTED
            font = self.font_med if index == 4 else self.font_small
            label = font.render(line, True, color)
            surface.blit(label, label.get_rect(center=(WIDTH / 2, HEIGHT * 0.52 + index * 34)))


# ================================= GAME ====================================

MENU, PLAYING, PAUSED, GAME_OVER = "menu", "playing", "paused", "game_over"


class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Zombie Siege")
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()

        self.hud = HUD()
        self.player_light = make_light_surface(260, (255, 225, 180), 235)
        self.small_light = make_light_surface(90, (255, 200, 120), 200)
        self.vignette = make_vignette(WIDTH, HEIGHT, strength=170)

        self.decal_surface = pygame.Surface((WORLD_W, WORLD_H), pygame.SRCALPHA)

        self.sim_time = 0.0
        self.state = MENU
        self.reset_world()

    # --------------------------- world setup ---------------------------

    def reset_world(self):
        self.player = Player((WORLD_W / 2, WORLD_H / 2))
        self.camera = Camera()
        self.camera.offset = self.player.pos - Vector2(WIDTH / 2, HEIGHT / 2)
        self.zombies = []
        self.bullets = []
        self.pickups = []
        self.particles = ParticleSystem()
        self.wave = WaveManager()
        self.pickup_timer = 6.0
        self.decal_surface.fill((0, 0, 0, 0))

    # ----------------------------- spawning -----------------------------

    def spawn_zombie(self, wave_number):
        angle = random.uniform(0, 360)
        dist = random.uniform(760, 980)
        pos = self.player.pos + Vector2(dist, 0).rotate(angle)
        pos.x = clamp(pos.x, 30, WORLD_W - 30)
        pos.y = clamp(pos.y, 30, WORLD_H - 30)
        kind = choose_zombie_kind(wave_number)
        self.zombies.append(Zombie(kind, pos, wave_number))

    def spawn_pickup(self, force=False):
        if not force and len(self.pickups) >= 5:
            return
        angle = random.uniform(0, 360)
        dist = random.uniform(180, 420)
        pos = self.player.pos + Vector2(dist, 0).rotate(angle)
        pos.x = clamp(pos.x, 30, WORLD_W - 30)
        pos.y = clamp(pos.y, 30, WORLD_H - 30)

        weights = [("health", 3), ("ammo", 4)]
        for name in ("smg", "shotgun", "rifle"):
            weights.append((f"weapon_{name}", 1 if self.player.owned.get(name) else 2))
        kinds, w = zip(*weights)
        kind = random.choices(kinds, weights=w, k=1)[0]
        self.pickups.append(Pickup(kind, pos))

    # ------------------------------ update -------------------------------

    def handle_shared_events(self, event):
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    def update_playing(self, dt, keys, mouse_buttons, mouse_world):
        self.sim_time += dt
        self.player.move(keys, dt)
        self.player.aim_dir = (mouse_world - self.player.pos)
        if self.player.aim_dir.length_squared() > 1:
            self.player.aim_dir = self.player.aim_dir.normalize()

        if mouse_buttons[0]:
            bullets = self.player.try_shoot(mouse_world)
            if bullets:
                self.bullets.extend(bullets)
                muzzle_pos = self.player.pos + self.player.aim_dir * (self.player.radius + 14)
                self.particles.burst(muzzle_pos, 5, self.player.weapon.color,
                                     speed_range=(120, 260), life_range=(0.08, 0.18),
                                     size_range=(2, 4))
                self.camera.shake(3, 0.06)

        self.player.update(dt)
        if self.player.health <= 0:
            self.state = GAME_OVER
            return

        self.camera.follow(self.player.pos)
        self.camera.update(dt)

        for bullet in self.bullets:
            bullet.update(dt)
        self.bullets = [b for b in self.bullets if not b.dead]

        for zombie in self.zombies:
            result = zombie.update(dt, self.player, self.zombies, self.sim_time)
            if result == "attacked":
                self.camera.shake(6, 0.15)
                self.particles.burst(self.player.pos, 8, (200, 30, 30),
                                     speed_range=(60, 160), life_range=(0.2, 0.4))

        self.resolve_bullet_hits()

        for zombie in self.zombies:
            if zombie.dead:
                self.on_zombie_killed(zombie)
        self.zombies = [z for z in self.zombies if not z.dead]

        for pickup in self.pickups:
            if (pickup.pos - self.player.pos).length() < pickup.radius + self.player.radius:
                self.player.collect_pickup(pickup.kind)
                self.particles.burst(pickup.pos, 14, PICKUP_COLORS[pickup.kind],
                                     speed_range=(60, 160), life_range=(0.3, 0.5))
                pickup.dead = True
        self.pickups = [p for p in self.pickups if not p.dead]

        self.pickup_timer -= dt
        if self.pickup_timer <= 0:
            self.spawn_pickup()
            self.pickup_timer = random.uniform(7, 12)

        self.wave.update(dt, self)
        self.particles.update(dt)

    def resolve_bullet_hits(self):
        for bullet in self.bullets:
            if bullet.dead:
                continue
            for zombie in self.zombies:
                if zombie.dead:
                    continue
                if (bullet.pos - zombie.pos).length() <= zombie.radius:
                    zombie.take_damage(bullet.damage)
                    bullet.dead = True
                    self.particles.burst(bullet.pos, 6, BLOOD,
                                         speed_range=(40, 150), life_range=(0.2, 0.4))
                    is_crit = random.random() < 0.15
                    text = "CRIT!" if is_crit else str(int(bullet.damage))
                    color = (255, 90, 90) if is_crit else (255, 220, 140)
                    self.particles.floating_text(zombie.pos + Vector2(0, -30), text, color)
                    break
        self.bullets = [b for b in self.bullets if not b.dead]

    def on_zombie_killed(self, zombie):
        self.player.score += zombie.score_value
        self.player.kills += 1
        pygame.draw.circle(self.decal_surface, (*BLOOD, 160),
                           (int(zombie.pos.x), int(zombie.pos.y)),
                           int(zombie.radius * 1.4))
        for _ in range(2):
            offset = Vector2(random.uniform(-14, 14), random.uniform(-14, 14))
            pygame.draw.circle(self.decal_surface, (*BLOOD, 130),
                               (int(zombie.pos.x + offset.x), int(zombie.pos.y + offset.y)),
                               int(zombie.radius * 0.7))
        self.particles.burst(zombie.pos, 18, BLOOD, speed_range=(80, 260),
                             life_range=(0.3, 0.6), size_range=(2, 6))
        if random.random() < 0.12:
            self.pickups.append(Pickup(random.choice(["health", "ammo"]), Vector2(zombie.pos)))

    # ------------------------------ drawing -------------------------------

    def draw_floor(self):
        tile = 72
        start_x = int(self.camera.offset.x // tile) * tile
        start_y = int(self.camera.offset.y // tile) * tile
        for wx in range(start_x - tile, start_x + WIDTH + tile, tile):
            for wy in range(start_y - tile, start_y + HEIGHT + tile, tile):
                variant = (wx // tile + wy // tile) % 2
                color = FLOOR_A if variant == 0 else FLOOR_B
                screen_pos = Vector2(wx, wy) - self.camera.offset
                pygame.draw.rect(self.screen, color, (*screen_pos, tile, tile))

    def draw_lighting(self):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((6, 8, 12, 235))

        player_screen = self.camera.to_screen(self.player.pos)
        light = self.player_light
        overlay.blit(light, (player_screen.x - light.get_width() / 2,
                             player_screen.y - light.get_height() / 2),
                    special_flags=pygame.BLEND_RGBA_SUB)

        # Muzzle flash ka apna chhota light — sirf jab abhi goli chali ho.
        if self.player.fire_cooldown > 0 and self.player.fire_cooldown > \
           (1.0 / self.player.weapon.fire_rate) * 0.6:
            flash_pos = player_screen + self.player.aim_dir * 40
            small = self.small_light
            overlay.blit(small, (flash_pos.x - small.get_width() / 2,
                                 flash_pos.y - small.get_height() / 2),
                        special_flags=pygame.BLEND_RGBA_SUB)

        self.screen.blit(overlay, (0, 0))
        self.screen.blit(self.vignette, (0, 0))

    def draw_playing_frame(self):
        self.screen.fill(DARK_BG)
        self.draw_floor()

        area = pygame.Rect(int(self.camera.offset.x), int(self.camera.offset.y), WIDTH, HEIGHT)
        area.x = clamp(area.x, 0, WORLD_W - WIDTH)
        area.y = clamp(area.y, 0, WORLD_H - HEIGHT)
        self.screen.blit(self.decal_surface, (0, 0), area=area)

        for pickup in self.pickups:
            pickup.draw(self.screen, self.camera, self.sim_time, self.hud.font_small)
        for zombie in self.zombies:
            zombie.draw(self.screen, self.camera, self.sim_time)
        for bullet in self.bullets:
            bullet.draw(self.screen, self.camera)
        self.player.draw(self.screen, self.camera)
        self.particles.draw(self.screen, self.camera, self.hud.font_small)

        self.draw_lighting()
        self.hud.draw_playing(self.screen, self.player, self.wave, self.camera,
                              self.zombies, self.sim_time)

    # ------------------------------- loop ---------------------------------

    def run(self):
        while True:
            dt = self.clock.tick(FPS) / 1000.0
            dt = min(dt, 0.05)   # bara lag spike aane par physics ko phatne se bachao

            keys = pygame.key.get_pressed()
            mouse_buttons = pygame.mouse.get_pressed()
            mouse_world = self.camera.to_world(pygame.mouse.get_pos())

            for event in pygame.event.get():
                self.handle_shared_events(event)
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        if self.state == PLAYING:
                            self.state = PAUSED
                        elif self.state == PAUSED:
                            self.state = PLAYING
                    elif event.key == pygame.K_RETURN:
                        if self.state in (MENU, GAME_OVER):
                            self.reset_world()
                            self.state = PLAYING
                    elif event.key == pygame.K_r and self.state == PLAYING:
                        self.player.start_reload()
                    elif event.key in (pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4) \
                            and self.state == PLAYING:
                        self.player.switch_weapon(event.key - pygame.K_1)

            if self.state == PLAYING:
                self.update_playing(dt, keys, mouse_buttons, mouse_world)

            if self.state == MENU:
                self.sim_time += dt
                self.screen.fill(DARK_BG)
                self.draw_floor_static_bg()
                self.hud.draw_menu(self.screen, self.sim_time)
            elif self.state in (PLAYING, PAUSED):
                self.draw_playing_frame()
                if self.state == PAUSED:
                    dim = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                    dim.fill((0, 0, 0, 150))
                    self.screen.blit(dim, (0, 0))
                    self.hud.draw_pause(self.screen)
            elif self.state == GAME_OVER:
                self.draw_playing_frame()
                dim = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                dim.fill((10, 0, 0, 170))
                self.screen.blit(dim, (0, 0))
                self.hud.draw_game_over(self.screen, self.player, self.wave)

            pygame.display.flip()

    def draw_floor_static_bg(self):
        tile = 72
        for wx in range(0, WIDTH + tile, tile):
            for wy in range(0, HEIGHT + tile, tile):
                variant = (wx // tile + wy // tile) % 2
                color = FLOOR_A if variant == 0 else FLOOR_B
                pygame.draw.rect(self.screen, color, (wx, wy, tile, tile))
        dim = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        dim.fill((6, 8, 12, 200))
        self.screen.blit(dim, (0, 0))


# ================================= MAIN =====================================

def main():
    Game().run()


if __name__ == "__main__":
    main()
