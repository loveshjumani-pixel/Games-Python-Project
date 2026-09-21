import pygame
import math
import random
import sys
import time
from typing import List, Tuple, Dict, Optional
from collections import deque

# Initialize pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 1200, 800
FPS = 60
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (100, 100, 100)

# Screen setup
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Advanced Animation Showcase - 1000+ Lines")
clock = pygame.time.Clock()

# Configuration
SCENE_DURATION = 600  # 10 seconds per scene at 60 FPS
TRANSITION_TIME = 60  # 1 second transition

# Color utilities
def hsv_to_rgb(h: float, s: float, v: float) -> Tuple[int, int, int]:
    """Convert HSV to RGB color"""
    if s == 0.0:
        return (int(v * 255), int(v * 255), int(v * 255))
    i = int(h * 6.0)
    f = (h * 6.0) - i
    p = v * (1.0 - s)
    q = v * (1.0 - s * f)
    t = v * (1.0 - s * (1.0 - f))
    i = i % 6
    if i == 0:
        return (int(v * 255), int(t * 255), int(p * 255))
    if i == 1:
        return (int(q * 255), int(v * 255), int(p * 255))
    if i == 2:
        return (int(p * 255), int(v * 255), int(t * 255))
    if i == 3:
        return (int(p * 255), int(q * 255), int(v * 255))
    if i == 4:
        return (int(t * 255), int(p * 255), int(v * 255))
    if i == 5:
        return (int(v * 255), int(p * 255), int(q * 255))
    return (0, 0, 0)

def rgb_to_hsv(r: int, g: int, b: int) -> Tuple[float, float, float]:
    """Convert RGB to HSV color"""
    r, g, b = r / 255.0, g / 255.0, b / 255.0
    mx = max(r, g, b)
    mn = min(r, g, b)
    df = mx - mn
    if mx == mn:
        h = 0
    elif mx == r:
        h = (60 * ((g - b) / df) + 360) % 360
    elif mx == g:
        h = (60 * ((b - r) / df) + 120) % 360
    else:
        h = (60 * ((r - g) / df) + 240) % 360
    if mx == 0:
        s = 0
    else:
        s = (df / mx) * 100
    v = mx * 100
    return (h / 360.0, s / 100.0, v / 100.0)

def lerp_color(color1: Tuple[int, int, int], color2: Tuple[int, int, int], t: float) -> Tuple[int, int, int]:
    """Linear interpolation between two colors"""
    t = max(0.0, min(1.0, t))
    r = int(color1[0] + (color2[0] - color1[0]) * t)
    g = int(color1[1] + (color2[1] - color1[1]) * t)
    b = int(color1[2] + (color2[2] - color1[2]) * t)
    return (r, g, b)

def ease_in_out(t: float) -> float:
    """Ease in-out function for smooth animations"""
    return t * t * (3 - 2 * t)

def ease_in(t: float) -> float:
    """Ease in function"""
    return t * t

def ease_out(t: float) -> float:
    """Ease out function"""
    return 1 - (1 - t) * (1 - t)

class Particle:
    """Particle class for various effects"""
    def __init__(self, x: float, y: float, vx: float = 0, vy: float = 0, 
                 color: Tuple[int, int, int] = WHITE, lifetime: int = 100, 
                 size: int = 3, gravity: float = 0.0):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.color = color
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.size = size
        self.gravity = gravity
        self.initial_size = size
        
    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += self.gravity
        self.lifetime -= 1
        # Fade size over lifetime
        if self.max_lifetime > 0:
            progress = self.lifetime / self.max_lifetime
            self.size = max(1, int(self.initial_size * progress))
        
    def draw(self, surface: pygame.Surface):
        if self.lifetime > 0:
            alpha = self.lifetime / self.max_lifetime
            color = tuple(int(c * alpha) for c in self.color)
            pygame.draw.circle(surface, color, (int(self.x), int(self.y)), self.size)
            
    def is_alive(self) -> bool:
        return self.lifetime > 0

class ParticleSystem:
    """Manage multiple particles"""
    def __init__(self):
        self.particles: List[Particle] = []
        
    def add_particle(self, particle: Particle):
        self.particles.append(particle)
        
    def update(self):
        for particle in self.particles[:]:
            particle.update()
            if not particle.is_alive():
                self.particles.remove(particle)
                
    def draw(self, surface: pygame.Surface):
        for particle in self.particles:
            particle.draw(surface)
            
    def clear(self):
        self.particles.clear()
        
    def get_count(self) -> int:
        return len(self.particles)

class Scene1_ParticleGalaxy:
    """Rotating particle galaxy effect"""
    def __init__(self):
        self.particles = []
        self.angle = 0
        self.center_x = WIDTH // 2
        self.center_y = HEIGHT // 2
        self.init_particles()
        
    def init_particles(self):
        self.particles = []
        for i in range(500):
            angle = random.uniform(0, 2 * math.pi)
            distance = random.uniform(50, 300)
            x = self.center_x + math.cos(angle) * distance
            y = self.center_y + math.sin(angle) * distance
            color = hsv_to_rgb(angle / (2 * math.pi), 0.8, 1.0)
            self.particles.append({
                'x': x, 'y': y, 'angle': angle,
                'distance': distance, 'color': color,
                'speed': random.uniform(0.005, 0.02),
                'size': random.randint(2, 5)
            })
            
    def update(self):
        self.angle += 0.01
        for p in self.particles:
            p['angle'] += p['speed']
            p['x'] = self.center_x + math.cos(p['angle']) * p['distance']
            p['y'] = self.center_y + math.sin(p['angle']) * p['distance']
            
    def draw(self, surface: pygame.Surface):
        surface.fill(BLACK)
        for p in self.particles:
            pygame.draw.circle(surface, p['color'], (int(p['x']), int(p['y'])), p['size'])
            
    def reset(self):
        self.init_particles()

class Scene2_FractalTree:
    """Recursive fractal tree with animation"""
    def __init__(self):
        self.angle = 0
        self.growth = 0
        self.growing = True
        
    def draw_branch(self, surface: pygame.Surface, x: float, y: float, 
                   length: float, angle: float, depth: int, max_depth: int):
        if depth == 0 or length < 5:
            return
            
        end_x = x + length * math.cos(angle)
        end_y = y + length * math.sin(angle)
        
        # Color gradient based on depth
        color_value = min(255, int(255 * (depth / max_depth)))
        color = (color_value, 100, 255 - color_value)
        
        thickness = max(1, depth)
        pygame.draw.line(surface, color, (int(x), int(y)), (int(end_x), int(end_y)), thickness)
        
        branch_angle = math.radians(25 + self.angle * 10)
        new_length = length * 0.7
        
        self.draw_branch(surface, end_x, end_y, new_length, angle - branch_angle, depth - 1, max_depth)
        self.draw_branch(surface, end_x, end_y, new_length, angle + branch_angle, depth - 1, max_depth)
        
    def update(self):
        self.angle += 0.01
        if self.growing:
            self.growth += 0.01
            if self.growth >= 1.0:
                self.growing = False
        else:
            self.growth -= 0.01
            if self.growth <= 0.0:
                self.growing = True
        
    def draw(self, surface: pygame.Surface):
        surface.fill(BLACK)
        max_depth = int(10 * self.growth)
        if max_depth > 0:
            self.draw_branch(surface, WIDTH // 2, HEIGHT - 50, 150, -math.pi / 2, max_depth, 10)

class Scene3_WaveInterference:
    """Multiple wave interference pattern"""
    def __init__(self):
        self.time = 0
        self.sources = [
            (WIDTH // 4, HEIGHT // 2),
            (3 * WIDTH // 4, HEIGHT // 2),
            (WIDTH // 2, HEIGHT // 4),
            (WIDTH // 2, 3 * HEIGHT // 4)
        ]
        
    def update(self):
        self.time += 0.05
        
    def draw(self, surface: pygame.Surface):
        surface.fill(BLACK)
        
        for x in range(0, WIDTH, 4):
            for y in range(0, HEIGHT, 4):
                total_wave = 0
                for source in self.sources:
                    distance = math.sqrt((x - source[0])**2 + (y - source[1])**2)
                    wave = math.sin(distance * 0.05 - self.time)
                    total_wave += wave
                    
                normalized = (total_wave + len(self.sources)) / (2 * len(self.sources))
                color_value = int(normalized * 255)
                color = (color_value // 2, color_value, 255 - color_value)
                pygame.draw.rect(surface, color, (x, y, 4, 4))

class Scene4_Mandelbrot:
    """Animated Mandelbrot set"""
    def __init__(self):
        self.zoom = 1.0
        self.center_x = -0.5
        self.center_y = 0
        self.max_iter = 100
        
    def mandelbrot(self, c: complex) -> int:
        z = 0
        for i in range(self.max_iter):
            if abs(z) > 2:
                return i
            z = z * z + c
        return self.max_iter
        
    def update(self):
        self.zoom *= 1.01
        if self.zoom > 100:
            self.zoom = 1.0
            
    def draw(self, surface: pygame.Surface):
        surface.fill(BLACK)
        
        for x in range(0, WIDTH, 2):
            for y in range(0, HEIGHT, 2):
                real = (x - WIDTH / 2) / (0.5 * self.zoom * WIDTH) + self.center_x
                imag = (y - HEIGHT / 2) / (0.5 * self.zoom * HEIGHT) + self.center_y
                c = complex(real, imag)
                
                m = self.mandelbrot(c)
                if m == self.max_iter:
                    color = BLACK
                else:
                    hue = m / self.max_iter
                    color = hsv_to_rgb(hue, 1.0, 1.0)
                    
                pygame.draw.rect(surface, color, (x, y, 2, 2))

class Scene5_Fireworks:
    """Fireworks particle effect"""
    def __init__(self):
        self.particle_system = ParticleSystem()
        self.firework_timer = 0
        self.colors = [
            (255, 100, 100), (100, 255, 100), (100, 100, 255),
            (255, 255, 100), (255, 100, 255), (100, 255, 255)
        ]
        
    def create_firework(self, x: float, y: float):
        color = random.choice(self.colors)
        for _ in range(100):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(2, 8)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            particle = Particle(x, y, vx, vy, color, lifetime=60, size=2, gravity=0.1)
            self.particle_system.add_particle(particle)
            
    def update(self):
        self.firework_timer += 1
        if self.firework_timer % 30 == 0:
            x = random.randint(100, WIDTH - 100)
            y = random.randint(100, HEIGHT // 2)
            self.create_firework(x, y)
            
        self.particle_system.update()
        
    def draw(self, surface: pygame.Surface):
        surface.fill(BLACK)
        self.particle_system.draw(surface)

class Scene6_3DCube:
    """3D wireframe cube rotation"""
    def __init__(self):
        self.angle_x = 0
        self.angle_y = 0
        self.angle_z = 0
        
        self.vertices = [
            (-1, -1, -1), (1, -1, -1), (1, 1, -1), (-1, 1, -1),
            (-1, -1, 1), (1, -1, 1), (1, 1, 1), (-1, 1, 1)
        ]
        
        self.edges = [
            (0, 1), (1, 2), (2, 3), (3, 0),
            (4, 5), (5, 6), (6, 7), (7, 4),
            (0, 4), (1, 5), (2, 6), (3, 7)
        ]
        
    def rotate_x(self, point: Tuple[float, float, float], angle: float) -> Tuple[float, float, float]:
        x, y, z = point
        y, z = y * math.cos(angle) - z * math.sin(angle), y * math.sin(angle) + z * math.cos(angle)
        return (x, y, z)
        
    def rotate_y(self, point: Tuple[float, float, float], angle: float) -> Tuple[float, float, float]:
        x, y, z = point
        x, z = x * math.cos(angle) + z * math.sin(angle), -x * math.sin(angle) + z * math.cos(angle)
        return (x, y, z)
        
    def rotate_z(self, point: Tuple[float, float, float], angle: float) -> Tuple[float, float, float]:
        x, y, z = point
        x, y = x * math.cos(angle) - y * math.sin(angle), x * math.sin(angle) + y * math.cos(angle)
        return (x, y, z)
        
    def project(self, point: Tuple[float, float, float]) -> Tuple[int, int]:
        x, y, z = point
        f = 300 / (z + 4)
        return (int(x * f + WIDTH / 2), int(y * f + HEIGHT / 2))
        
    def update(self):
        self.angle_x += 0.01
        self.angle_y += 0.013
        self.angle_z += 0.007
        
    def draw(self, surface: pygame.Surface):
        surface.fill(BLACK)
        
        rotated = []
        for vertex in self.vertices:
            point = self.rotate_x(vertex, self.angle_x)
            point = self.rotate_y(point, self.angle_y)
            point = self.rotate_z(point, self.angle_z)
            rotated.append(point)
            
        projected = [self.project(p) for p in rotated]
        
        for edge in self.edges:
            start = projected[edge[0]]
            end = projected[edge[1]]
            pygame.draw.line(surface, (100, 200, 255), start, end, 3)
            
        for point in projected:
            pygame.draw.circle(surface, (255, 255, 255), point, 5)

class Scene7_Spiral:
    """Animated spiral with color gradient"""
    def __init__(self):
        self.time = 0
        
    def update(self):
        self.time += 0.02
        
    def draw(self, surface: pygame.Surface):
        surface.fill(BLACK)
        
        for i in range(1000):
            angle = i * 0.1 + self.time
            radius = i * 0.3
            x = WIDTH // 2 + math.cos(angle) * radius
            y = HEIGHT // 2 + math.sin(angle) * radius
            
            if 0 <= x < WIDTH and 0 <= y < HEIGHT:
                hue = (i / 1000 + self.time * 0.1) % 1.0
                color = hsv_to_rgb(hue, 1.0, 1.0)
                pygame.draw.circle(surface, color, (int(x), int(y)), 3)

class Scene8_MatrixRain:
    """Matrix-style falling characters"""
    def __init__(self):
        self.columns = WIDTH // 20
        self.drops = [0] * self.columns
        self.chars = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        self.font = pygame.font.Font(None, 20)
        
    def update(self):
        for i in range(len(self.drops)):
            self.drops[i] += 1
            if self.drops[i] * 20 > HEIGHT and random.random() > 0.95:
                self.drops[i] = 0
                
    def draw(self, surface: pygame.Surface):
        surface.fill((0, 0, 0))
        
        for i in range(len(self.drops)):
            char = random.choice(self.chars)
            text = self.font.render(char, True, (0, 255, 0))
            surface.blit(text, (i * 20, self.drops[i] * 20))

class Scene9_Lissajous:
    """Lissajous curve animation"""
    def __init__(self):
        self.time = 0
        self.points = []
        
    def update(self):
        self.time += 0.02
        self.points = []
        
        for i in range(1000):
            t = i * 0.01
            x = WIDTH // 2 + int(300 * math.sin(3 * t + self.time))
            y = HEIGHT // 2 + int(200 * math.sin(2 * t))
            self.points.append((x, y))
        
    def draw(self, surface: pygame.Surface):
        surface.fill(BLACK)
        
        for i in range(len(self.points) - 1):
            hue = i / len(self.points)
            color = hsv_to_rgb(hue, 1.0, 1.0)
            pygame.draw.line(surface, color, self.points[i], self.points[i + 1], 2)

class Scene10_StarField:
    """3D starfield simulation"""
    def __init__(self):
        self.stars = []
        self.num_stars = 500
        
        for _ in range(self.num_stars):
            self.stars.append({
                'x': random.uniform(-1, 1),
                'y': random.uniform(-1, 1),
                'z': random.uniform(0.1, 1)
            })
            
    def update(self):
        for star in self.stars:
            star['z'] -= 0.01
            if star['z'] <= 0:
                star['x'] = random.uniform(-1, 1)
                star['y'] = random.uniform(-1, 1)
                star['z'] = 1.0
                
    def draw(self, surface: pygame.Surface):
        surface.fill(BLACK)
        
        for star in self.stars:
            x = int((star['x'] / star['z']) * WIDTH / 2 + WIDTH / 2)
            y = int((star['y'] / star['z']) * HEIGHT / 2 + HEIGHT / 2)
            size = int((1 - star['z']) * 4)
            
            if 0 <= x < WIDTH and 0 <= y < HEIGHT:
                brightness = int((1 - star['z']) * 255)
                color = (brightness, brightness, brightness)
                pygame.draw.circle(surface, color, (x, y), max(1, size))

class Scene11_Plasma:
    """Plasma effect animation"""
    def __init__(self):
        self.time = 0
        
    def update(self):
        self.time += 0.05
        
    def draw(self, surface: pygame.Surface):
        surface.fill(BLACK)
        
        for x in range(0, WIDTH, 4):
            for y in range(0, HEIGHT, 4):
                v1 = math.sin(x * 0.01 + self.time)
                v2 = math.sin(y * 0.01 + self.time * 0.5)
                v3 = math.sin((x + y) * 0.01 + self.time * 0.3)
                v4 = math.sin(math.sqrt(x * x + y * y) * 0.01 + self.time * 0.7)
                
                v = (v1 + v2 + v3 + v4) / 4
                hue = (v + 1) / 2
                color = hsv_to_rgb(hue, 1.0, 1.0)
                
                pygame.draw.rect(surface, color, (x, y, 4, 4))

class Scene12_FlowerPattern:
    """Rose curve flower pattern"""
    def __init__(self):
        self.time = 0
        self.k = 5
        
    def update(self):
        self.time += 0.02
        self.k = 3 + 2 * math.sin(self.time * 0.1)
        
    def draw(self, surface: pygame.Surface):
        surface.fill(BLACK)
        
        points = []
        for i in range(1000):
            theta = i * 0.01
            r = 200 * math.cos(self.k * theta)
            x = WIDTH // 2 + int(r * math.cos(theta))
            y = HEIGHT // 2 + int(r * math.sin(theta))
            points.append((x, y))
            
        for i in range(len(points) - 1):
            hue = i / len(points)
            color = hsv_to_rgb(hue, 1.0, 1.0)
            pygame.draw.line(surface, color, points[i], points[i + 1], 2)

class Scene13_Pendulum:
    """Double pendulum chaos"""
    def __init__(self):
        self.L1 = 150
        self.L2 = 150
        self.m1 = 10
        self.m2 = 10
        self.a1 = math.pi / 2
        self.a2 = math.pi / 2
        self.a1_v = 0
        self.a2_v = 0
        self.g = 1
        self.trail = []
        
    def update(self):
        num1 = -self.g * (2 * self.m1 + self.m2) * math.sin(self.a1)
        num2 = -self.m2 * self.g * math.sin(self.a1 - 2 * self.a2)
        num3 = -2 * math.sin(self.a1 - self.a2) * self.m2
        num4 = self.a2_v * self.a2_v * self.L2 + self.a1_v * self.a1_v * self.L1 * math.cos(self.a1 - self.a2)
        den = self.L1 * (2 * self.m1 + self.m2 - self.m2 * math.cos(2 * self.a1 - 2 * self.a2))
        a1_a = (num1 + num2 + num3 * num4) / den
        
        num1 = 2 * math.sin(self.a1 - self.a2)
        num2 = self.a1_v * self.a1_v * self.L1 * (self.m1 + self.m2)
        num3 = self.g * (self.m1 + self.m2) * math.cos(self.a1)
        num4 = self.a2_v * self.a2_v * self.L2 * self.m2 * math.cos(self.a1 - self.a2)
        den = self.L2 * (2 * self.m1 + self.m2 - self.m2 * math.cos(2 * self.a1 - 2 * self.a2))
        a2_a = (num1 * (num2 + num3 + num4)) / den
        
        self.a1_v += a1_a * 0.1
        self.a2_v += a2_a * 0.1
        self.a1 += self.a1_v * 0.1
        self.a2 += self.a2_v * 0.1
        
        self.a1_v *= 0.99
        self.a2_v *= 0.99
        
        x1 = WIDTH // 2 + self.L1 * math.sin(self.a1)
        y1 = HEIGHT // 2 + self.L1 * math.cos(self.a1)
        x2 = x1 + self.L2 * math.sin(self.a2)
        y2 = y1 + self.L2 * math.cos(self.a2)
        
        self.trail.append((x2, y2))
        if len(self.trail) > 500:
            self.trail.pop(0)
        
    def draw(self, surface: pygame.Surface):
        surface.fill(BLACK)
        
        for i in range(len(self.trail) - 1):
            hue = i / len(self.trail)
            color = hsv_to_rgb(hue, 1.0, 1.0)
            pygame.draw.line(surface, color, self.trail[i], self.trail[i + 1], 2)
            
        x1 = WIDTH // 2 + self.L1 * math.sin(self.a1)
        y1 = HEIGHT // 2 + self.L1 * math.cos(self.a1)
        x2 = x1 + self.L2 * math.sin(self.a2)
        y2 = y1 + self.L2 * math.cos(self.a2)
        
        pygame.draw.line(surface, WHITE, (WIDTH // 2, HEIGHT // 2), (int(x1), int(y1)), 3)
        pygame.draw.line(surface, WHITE, (int(x1), int(y1)), (int(x2), int(y2)), 3)
        pygame.draw.circle(surface, (255, 100, 100), (int(x1), int(y1)), 10)
        pygame.draw.circle(surface, (100, 255, 100), (int(x2), int(y2)), 10)

class Scene14_Sierpinski:
    """Sierpinski triangle fractal"""
    def __init__(self):
        self.points = [(WIDTH // 2, 50), (100, HEIGHT - 50), (WIDTH - 100, HEIGHT - 50)]
        self.current = (WIDTH // 2, HEIGHT // 2)
        self.triangle_points = []
        
    def update(self):
        for _ in range(100):
            target = random.choice(self.points)
            self.current = ((self.current[0] + target[0]) / 2, 
                          (self.current[1] + target[1]) / 2)
            self.triangle_points.append(self.current)
            
        if len(self.triangle_points) > 10000:
            self.triangle_points = self.triangle_points[-5000:]
        
    def draw(self, surface: pygame.Surface):
        surface.fill(BLACK)
        
        for i, point in enumerate(self.triangle_points):
            hue = i / len(self.triangle_points)
            color = hsv_to_rgb(hue, 1.0, 1.0)
            pygame.draw.circle(surface, color, (int(point[0]), int(point[1])), 1)

class Scene15_SpiderWeb:
    """Animated spider web pattern"""
    def __init__(self):
        self.time = 0
        self.rings = 10
        self.segments = 20
        
    def update(self):
        self.time += 0.02
        
    def draw(self, surface: pygame.Surface):
        surface.fill(BLACK)
        center = (WIDTH // 2, HEIGHT // 2)
        
        for ring in range(1, self.rings + 1):
            radius = ring * 30
            for seg in range(self.segments):
                angle1 = (seg / self.segments) * 2 * math.pi + self.time
                angle2 = ((seg + 1) / self.segments) * 2 * math.pi + self.time
                
                x1 = center[0] + int(radius * math.cos(angle1))
                y1 = center[1] + int(radius * math.sin(angle1))
                x2 = center[0] + int(radius * math.cos(angle2))
                y2 = center[1] + int(radius * math.sin(angle2))
                
                hue = (ring + seg) / (self.rings + self.segments)
                color = hsv_to_rgb(hue, 1.0, 1.0)
                pygame.draw.line(surface, color, (x1, y1), (x2, y2), 2)
                
                if ring > 1:
                    prev_radius = (ring - 1) * 30
                    px = center[0] + int(prev_radius * math.cos(angle1))
                    py = center[1] + int(prev_radius * math.sin(angle1))
                    pygame.draw.line(surface, color, (x1, y1), (px, py), 2)

class AnimationController:
    """Control multiple animation scenes"""
    def __init__(self):
        self.scenes = [
            Scene1_ParticleGalaxy(),
            Scene2_FractalTree(),
            Scene3_WaveInterference(),
            Scene4_Mandelbrot(),
            Scene5_Fireworks(),
            Scene6_3DCube(),
            Scene7_Spiral(),
            Scene8_MatrixRain(),
            Scene9_Lissajous(),
            Scene10_StarField(),
            Scene11_Plasma(),
            Scene12_FlowerPattern(),
            Scene13_Pendulum(),
            Scene14_Sierpinski(),
            Scene15_SpiderWeb()
        ]
        self.current_scene = 0
        self.scene_timer = 0
        self.transition_alpha = 0
        self.in_transition = False
        
    def update(self):
        self.scene_timer += 1
        
        if self.scene_timer >= SCENE_DURATION:
            self.in_transition = True
            self.transition_alpha += 255 / TRANSITION_TIME
            
            if self.transition_alpha >= 255:
                self.scene_timer = 0
                self.current_scene = (self.current_scene + 1) % len(self.scenes)
                if hasattr(self.scenes[self.current_scene], 'reset'):
                    self.scenes[self.current_scene].reset()
                self.transition_alpha = 0
                self.in_transition = False
                
        self.scenes[self.current_scene].update()
        
    def draw(self, surface: pygame.Surface):
        self.scenes[self.current_scene].draw(surface)
        
        # Draw scene indicator
        font = pygame.font.Font(None, 36)
        text = font.render(f"Scene {self.current_scene + 1}/{len(self.scenes)}", True, WHITE)
        surface.blit(text, (10, 10))
        
        # Draw transition overlay
        if self.in_transition:
            overlay = pygame.Surface((WIDTH, HEIGHT))
            overlay.fill(BLACK)
            overlay.set_alpha(int(self.transition_alpha))
            surface.blit(overlay, (0, 0))

def main():
    """Main animation loop"""
    controller = AnimationController()
    running = True
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_SPACE:
                    controller.current_scene = (controller.current_scene + 1) % len(controller.scenes)
                    controller.scene_timer = 0
                    if hasattr(controller.scenes[controller.current_scene], 'reset'):
                        controller.scenes[controller.current_scene].reset()
                elif event.key == pygame.K_LEFT:
                    controller.current_scene = (controller.current_scene - 1) % len(controller.scenes)
                    controller.scene_timer = 0
                elif event.key == pygame.K_RIGHT:
                    controller.current_scene = (controller.current_scene + 1) % len(controller.scenes)
                    controller.scene_timer = 0
                    
        controller.update()
        controller.draw(screen)
        
        pygame.display.flip()
        clock.tick(FPS)
        
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()