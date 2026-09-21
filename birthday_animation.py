import tkinter as tk
import random
import math
import colorsys

# ============ CONFIGURATION ============
WIDTH, HEIGHT = 1200, 750
NAME = " Happy Birthday! "
FPS = 120

# ============ HELPER: HSV to HEX ============
def hsv_to_hex(h, s=1.0, v=1.0):
    """Convert HSV (0-360, 0-1, 0-1) to hex color"""
    r, g, b = colorsys.hsv_to_rgb(h/360.0, s, v)
    return f'#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}'

# ============ PARTICLE CLASS ============
class Particle:
    def __init__(self, x, y, color, vx=0, vy=0, life=60, size=3, gravity=0.05, fade=True):
        self.x, self.y = x, y
        self.vx, self.vy = vx, vy
        self.color = color
        self.life = life
        self.max_life = life
        self.size = size
        self.gravity = gravity
        self.fade = fade

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += self.gravity
        self.life -= 1

    def draw(self, canvas):
        alpha = self.life / self.max_life if self.fade else 1
        if alpha <= 0: return
        r = self.size * (0.5 + alpha * 0.5)
        canvas.create_oval(self.x - r, self.y - r, self.x + r, self.y + r,
                           fill=self.color, outline='')

    def alive(self):
        return self.life > 0

# ============ HEART SHAPE ============
class HeartParticle:
    def __init__(self, cx, cy, color, scale=1):
        self.cx, self.cy = cx, cy
        self.color = color
        self.scale = scale
        self.angle = random.uniform(0, 2 * math.pi)
        self.speed = random.uniform(0.8, 2.5)
        self.life = 80
        self.max_life = 80

    def update(self):
        t = self.angle
        x = 16 * (math.sin(t) ** 3)
        y = -(13 * math.cos(t) - 5 * math.cos(2*t) - 2 * math.cos(3*t) - math.cos(4*t))
        self.x = self.cx + x * self.scale * (1 - self.life/self.max_life)
        self.y = self.cy + y * self.scale * (1 - self.life/self.max_life)
        self.life -= 1

    def draw(self, canvas):
        alpha = self.life / self.max_life
        r = 3 * alpha
        canvas.create_oval(self.x - r, self.y - r, self.x + r, self.y + r,
                           fill=self.color, outline='')

    def alive(self):
        return self.life > 0

# ============ SHOOTING STAR ============
class ShootingStar:
    def __init__(self):
        self.reset()

    def reset(self):
        self.x = random.randint(-100, WIDTH)
        self.y = random.randint(-50, HEIGHT // 2)
        self.vx = random.uniform(8, 14)
        self.vy = random.uniform(3, 6)
        self.trail = []
        self.life = 80

    def update(self):
        self.trail.append((self.x, self.y))
        if len(self.trail) > 25:
            self.trail.pop(0)
        self.x += self.vx
        self.y += self.vy
        self.life -= 1
        if self.x > WIDTH + 50 or self.y > HEIGHT + 50 or self.life <= 0:
            self.reset()

    def draw(self, canvas):
        for i, (px, py) in enumerate(self.trail):
            alpha = (i + 1) / len(self.trail)
            r = 2 * alpha
            canvas.create_oval(px - r, py - r, px + r, py + r,
                               fill='#FFFFFF', outline='')

# ============ BACKGROUND STAR ============
class Star:
    def __init__(self):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(0, HEIGHT)
        self.size = random.uniform(0.5, 2.2)
        self.phase = random.uniform(0, math.pi * 2)
        self.speed = random.uniform(0.03, 0.1)

    def update(self, t):
        self.brightness = 0.4 + 0.6 * abs(math.sin(self.phase + t * self.speed))

    def draw(self, canvas):
        r = self.size * self.brightness
        c = int(255 * self.brightness)
        color = f'#{c:02x}{c:02x}{int(c*0.9):02x}'
        canvas.create_oval(self.x - r, self.y - r, self.x + r, self.y + r,
                           fill=color, outline='')

# ============ FIREWORK ============
def create_firework(x, y, particles):
    colors = ['#FF1493', '#FFD700', '#00FFFF', '#FF4500', '#7FFF00',
              '#FF69B4', '#1E90FF', '#FF6347', '#ADFF2F', '#BA55D3']
    color = random.choice(colors)
    count = random.randint(60, 110)
    for _ in range(count):
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(2, 8)
        vx = math.cos(angle) * speed
        vy = math.sin(angle) * speed
        life = random.randint(50, 90)
        size = random.uniform(2, 4)
        particles.append(Particle(x, y, color, vx, vy, life, size, gravity=0.08))

    for _ in range(15):
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(0.5, 2)
        particles.append(Particle(x, y, '#FFFFFF',
                                  math.cos(angle)*speed, math.sin(angle)*speed,
                                  30, 2, gravity=0.02))

# ============ MAIN APP ============
class LoveshAnimation:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title(f"✨ {NAME} - A Celebration ✨")
        self.root.resizable(False, False)

        self.canvas = tk.Canvas(self.root, width=WIDTH, height=HEIGHT,
                                bg='black', highlightthickness=0)
        self.canvas.pack()

        self.particles = []
        self.hearts = []
        self.stars = [Star() for _ in range(180)]
        self.shooting_stars = [ShootingStar() for _ in range(3)]

        self.t = 0
        self.frame = 0
        self.hue = 0

        self.canvas.bind('<Button-1>', self.on_click)
        self.canvas.bind('<Motion>', self.on_motion)

        self.info = tk.Label(self.root, text="🖱️ Click anywhere for fireworks | Move mouse for sparkles",
                             bg='black', fg='gold', font=('Segoe UI', 11))
        self.info.pack(side='bottom', fill='x', pady=4)

        self.animate()
        self.root.mainloop()

    def on_click(self, event):
        create_firework(event.x, event.y, self.particles)
        for _ in range(25):
            self.hearts.append(HeartParticle(event.x, event.y,
                             random.choice(['#FF1493', '#FF69B4', '#FF6347', '#FFD700'])))

    def on_motion(self, event):
        if self.frame % 3 == 0:
            # ✅ FIXED: Use hsv_to_hex function
            color = hsv_to_hex(self.hue, 1.0, 1.0)
            self.particles.append(Particle(
                event.x, event.y,
                color,
                random.uniform(-1, 1), random.uniform(-1, 1),
                30, random.uniform(1.5, 3), gravity=0, fade=True
            ))

    def draw_background(self):
        steps = 30
        for i in range(steps):
            ratio = i / steps
            r = int(5 + ratio * 25)
            g = int(0 + ratio * 5)
            b = int(20 + ratio * 50)
            y1 = i * (HEIGHT / steps)
            y2 = (i + 1) * (HEIGHT / steps)
            self.canvas.create_rectangle(0, y1, WIDTH, y2,
                                         fill=f'#{r:02x}{g:02x}{b:02x}', outline='')

    def draw_name(self):
        pulse = 1 + 0.08 * math.sin(self.t * 0.1)
        font_size = int(110 * pulse)

        glow_colors = ['#FF1493', '#FF69B4', '#FFD700', '#FFFFFF']
        glow_offsets = [8, 5, 3, 0]

        for color, offset in zip(glow_colors, glow_offsets):
            self.canvas.create_text(WIDTH // 2, HEIGHT // 2 - 40,
                                    text=NAME,
                                    font=('Segoe UI Bold', font_size),
                                    fill=color)

        letters = list(NAME)
        total_width = font_size * len(letters) * 0.6
        start_x = WIDTH // 2 - total_width / 2 + font_size * 0.3

        for i, letter in enumerate(letters):
            # ✅ FIXED: Use hsv_to_hex function
            letter_hue = (self.hue + i * 30) % 360
            wave_y = math.sin(self.t * 0.15 + i * 0.5) * 12
            color = hsv_to_hex(letter_hue, 1.0, 1.0)

            self.canvas.create_text(start_x + i * font_size * 0.6,
                                    HEIGHT // 2 - 40 + wave_y,
                                    text=letter,
                                    font=('Segoe UI Bold', font_size),
                                    fill=color)

        subtitle_colors = ['#FFD700', '#FF69B4', '#00FFFF', '#FF4500']
        sub_color = subtitle_colors[int(self.t * 0.1) % len(subtitle_colors)]
        self.canvas.create_text(WIDTH // 2, HEIGHT // 2 + 60,
                                text="★ ✨ A Name That Shines ✨ ★",
                                font=('Segoe UI', 22, 'italic'),
                                fill=sub_color)

    def auto_fireworks(self):
        if self.frame % 70 == 0:
            x = random.randint(150, WIDTH - 150)
            y = random.randint(100, HEIGHT // 2)
            create_firework(x, y, self.particles)

        if self.frame % 180 == 0:
            cx = random.randint(200, WIDTH - 200)
            cy = random.randint(200, HEIGHT - 200)
            color = random.choice(['#FF1493', '#FF69B4', '#FFD700', '#FF6347'])
            for _ in range(40):
                self.hearts.append(HeartParticle(cx, cy, color, scale=random.uniform(3, 6)))

    def animate(self):
        self.canvas.delete('all')
        self.t += 1
        self.frame += 1
        self.hue = (self.hue + 1.5) % 360

        self.draw_background()

        for star in self.stars:
            star.update(self.t)
            star.draw(self.canvas)

        for ss in self.shooting_stars:
            ss.update()
            ss.draw(self.canvas)

        self.auto_fireworks()

        self.particles = [p for p in self.particles if p.alive()]
        for p in self.particles:
            p.update()
            p.draw(self.canvas)

        self.hearts = [h for h in self.hearts if h.alive()]
        for h in self.hearts:
            h.update()
            h.draw(self.canvas)

        self.draw_name()

        self.root.after(1000 // FPS, self.animate)

# ============ RUN ============
if __name__ == '__main__':
    LoveshAnimation()