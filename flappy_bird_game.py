import pygame
import random
import math
import os
import sys

pygame.init()

# ---------- Screen setup ----------
W, H = 400, 600
screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("Flappy Bird - Advanced")
clock = pygame.time.Clock()
FONT      = pygame.font.SysFont("arial", 32, bold=True)
SMALL     = pygame.font.SysFont("arial", 20)
BIG       = pygame.font.SysFont("arial", 42, bold=True)

# ---------- Colors ----------
SKY_TOP    = (110, 180, 230)
SKY_BOT    = (200, 230, 255)
PIPE_GREEN = (100, 180, 80)
PIPE_DARK  = (60, 120, 50)
PIPE_LIGHT = (140, 210, 110)
GROUND_TOP = (220, 180, 100)
GROUND_BOT = (180, 140, 70)

# ---------- Constants ----------
GRAVITY      = 0.45
FLAP_VEL     = -7.8
MAX_FALL     = 11
PIPE_W       = 60
PIPE_GAP     = 155
PIPE_SPACING = 230
PIPE_SPEED   = 2.6
GROUND_H     = 80

# ---------- States ----------
MENU, PLAY, DEAD = 0, 1, 2
state = MENU
score = 0

# Best score save file (script ke folder me)
BEST_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "flappy_best.txt")
try:
    with open(BEST_FILE) as f: best = int(f.read())
except: best = 0

def save_best():
    try:
        with open(BEST_FILE, 'w') as f: f.write(str(best))
    except: pass

# ---------- Bird ----------
bird = {'x': 110, 'y': H//2, 'vy': 0, 'rot': 0, 'wing': 0}

# ---------- World ----------
pipes = []
particles = []
clouds = []
for _ in range(7):
    clouds.append({
        'x': random.randint(0, W),
        'y': random.randint(40, 220),
        's': random.uniform(0.5, 1.2),
        'speed': random.uniform(0.2, 0.5)
    })

ground_offset = 0
shake = 0
flash = 0
dead_timer = 0
pipe_timer = 0

# ---------- Background gradient (cached) ----------
def make_gradient(w, h, top, bot):
    surf = pygame.Surface((w, h))
    for y in range(h):
        t = y / h
        r = int(top[0] + (bot[0]-top[0])*t)
        g = int(top[1] + (bot[1]-top[1])*t)
        b = int(top[2] + (bot[2]-top[2])*t)
        pygame.draw.line(surf, (r,g,b), (0,y), (w,y))
    return surf

bg_surface = make_gradient(W, H, SKY_TOP, SKY_BOT)

# ---------- Reset ----------
def reset():
    global pipes, particles, score, ground_offset, shake, flash, dead_timer, pipe_timer, state
    bird['x'], bird['y'], bird['vy'], bird['rot'] = 110, H//2, 0, 0
    pipes, particles = [], []
    score = 0
    ground_offset = 0
    shake = 0
    flash = 0
    dead_timer = 0
    pipe_timer = 0
    state = PLAY

# ---------- Particles ----------
def emit(x, y, n, color, spread=3, life=30):
    for _ in range(n):
        particles.append({
            'x': x, 'y': y,
            'vx': random.uniform(-spread, spread),
            'vy': random.uniform(-spread, spread) - 1,
            'life': life, 'max': life,
            'color': color,
            'size': random.uniform(2, 4)
        })

# ---------- Drawing helpers ----------
def draw_cloud(x, y, s):
    surf = pygame.Surface((int(80*s), int(40*s)), pygame.SRCALPHA)
    c = (255, 255, 255, 200)
    pygame.draw.ellipse(surf, c, (0, int(10*s), int(40*s), int(30*s)))
    pygame.draw.ellipse(surf, c, (int(20*s), 0, int(40*s), int(40*s)))
    pygame.draw.ellipse(surf, c, (int(40*s), int(10*s), int(40*s), int(30*s)))
    screen.blit(surf, (int(x), int(y)))

def draw_hills(offset, color, y_base, amplitude, freq):
    surf = pygame.Surface((W, H), pygame.SRCALPHA)
    points = [(0, H)]
    for x in range(0, W+10, 10):
        y = y_base + math.sin((x + offset) * freq) * amplitude
        points.append((x, int(y)))
    points.append((W, H))
    pygame.draw.polygon(surf, color, points)
    screen.blit(surf, (0, 0))

def draw_pipe(x, top_h):
    # Top pipe body
    pygame.draw.rect(screen, PIPE_GREEN, (x, 0, PIPE_W, top_h))
    pygame.draw.rect(screen, PIPE_DARK,  (x, 0, 6, top_h))
    pygame.draw.rect(screen, PIPE_LIGHT, (x+PIPE_W-8, 0, 8, top_h))
    # Top cap
    pygame.draw.rect(screen, PIPE_GREEN, (x-4, top_h-26, PIPE_W+8, 26))
    pygame.draw.rect(screen, PIPE_DARK,  (x-4, top_h-26, 6, 26))
    pygame.draw.rect(screen, PIPE_LIGHT, (x+PIPE_W-2, top_h-26, 6, 26))
    pygame.draw.rect(screen, (40,80,30), (x-4, top_h-26, PIPE_W+8, 26), 2)
    # Bottom pipe
    bot_y = top_h + PIPE_GAP
    bot_h = H - GROUND_H - bot_y
    pygame.draw.rect(screen, PIPE_GREEN, (x, bot_y, PIPE_W, bot_h))
    pygame.draw.rect(screen, PIPE_DARK,  (x, bot_y, 6, bot_h))
    pygame.draw.rect(screen, PIPE_LIGHT, (x+PIPE_W-8, bot_y, 8, bot_h))
    # Bottom cap
    pygame.draw.rect(screen, PIPE_GREEN, (x-4, bot_y, PIPE_W+8, 26))
    pygame.draw.rect(screen, PIPE_DARK,  (x-4, bot_y, 6, 26))
    pygame.draw.rect(screen, PIPE_LIGHT, (x+PIPE_W-2, bot_y, 6, 26))
    pygame.draw.rect(screen, (40,80,30), (x-4, bot_y, PIPE_W+8, 26), 2)

def draw_bird(x, y, rot, wing_phase):
    surf = pygame.Surface((50, 40), pygame.SRCALPHA)
    cx, cy = 25, 20
    # Body
    pygame.draw.ellipse(surf, (255, 220, 80), (cx-16, cy-12, 32, 24))
    pygame.draw.ellipse(surf, (255, 240, 150), (cx-12, cy-10, 20, 14))
    # Wing (animated)
    wing_y = cy - 2 + math.sin(wing_phase) * 4
    pygame.draw.ellipse(surf, (230, 180, 50), (cx-10, int(wing_y)-5, 18, 12))
    # Eye
    pygame.draw.circle(surf, (255,255,255), (cx+6, cy-4), 5)
    pygame.draw.circle(surf, (0,0,0), (cx+8, cy-4), 2)
    # Beak
    pygame.draw.polygon(surf, (255, 140, 40),
        [(cx+12, cy), (cx+22, cy-2), (cx+22, cy+4), (cx+12, cy+4)])
    pygame.draw.polygon(surf, (200, 90, 20),
        [(cx+12, cy+2), (cx+22, cy+2), (cx+22, cy+4), (cx+12, cy+4)])
    rotated = pygame.transform.rotate(surf, -rot)
    rect = rotated.get_rect(center=(int(x), int(y)))
    screen.blit(rotated, rect)

def draw_ground():
    pygame.draw.rect(screen, GROUND_TOP, (0, H-GROUND_H, W, 8))
    pygame.draw.rect(screen, GROUND_BOT, (0, H-GROUND_H+8, W, GROUND_H-8))
    for x in range(-24, W+24, 24):
        xx = int((x - ground_offset) % W)
        pygame.draw.line(screen, (140, 100, 50), (xx, H-GROUND_H+12),
                         (xx+12, H-GROUND_H+24), 2)

def draw_text_shadow(text, font, color, pos, shadow=(0,0,0)):
    s = font.render(text, True, shadow)
    r = s.get_rect(center=(pos[0]+2, pos[1]+2))
    screen.blit(s, r)
    s = font.render(text, True, color)
    r = s.get_rect(center=pos)
    screen.blit(s, r)

def get_medal(s):
    if s >= 40: return ("P", (180, 220, 255))  # Platinum
    if s >= 25: return ("G", (255, 215, 0))    # Gold
    if s >= 15: return ("S", (200, 200, 210))  # Silver
    if s >= 5:  return ("B", (205, 127, 50))   # Bronze
    return None

# ---------- Main loop ----------
running = True
while running:
    clock.tick(60)

    # Events
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            running = False
        if e.type == pygame.KEYDOWN:
            if e.key == pygame.K_SPACE:
                if state == MENU: reset()
                elif state == PLAY:
                    bird['vy'] = FLAP_VEL
                    emit(bird['x']-8, bird['y']+4, 5, (255,255,255))
                elif state == DEAD and dead_timer > 30:
                    state = MENU
            if e.key == pygame.K_r:
                state = MENU
        if e.type == pygame.MOUSEBUTTONDOWN:
            if state == MENU: reset()
            elif state == PLAY:
                bird['vy'] = FLAP_VEL
                emit(bird['x']-8, bird['y']+4, 5, (255,255,255))
            elif state == DEAD and dead_timer > 30:
                state = MENU

    # ---------- Update ----------
    if state == PLAY:
        bird['vy'] = min(bird['vy'] + GRAVITY, MAX_FALL)
        bird['y'] += bird['vy']
        bird['rot'] = max(-25, min(80, bird['vy'] * 6))
        bird['wing'] += 0.4

        pipe_timer += 1
        if pipe_timer > PIPE_SPACING / PIPE_SPEED:
            pipe_timer = 0
            margin = 70
            top_h = random.randint(margin, H - GROUND_H - PIPE_GAP - margin)
            pipes.append({'x': W+10, 'top': top_h, 'passed': False})

        for p in pipes:
            p['x'] -= PIPE_SPEED
            if not p['passed'] and p['x'] + PIPE_W < bird['x']:
                p['passed'] = True
                score += 1
        pipes = [p for p in pipes if p['x'] > -PIPE_W-10]

        # Collision
        hit = False
        if bird['y'] + 14 > H - GROUND_H:
            bird['y'] = H - GROUND_H - 14
            hit = True
        if bird['y'] - 14 < 0:
            bird['y'] = 14
            bird['vy'] = 0
        for p in pipes:
            if bird['x']+12 > p['x'] and bird['x']-12 < p['x']+PIPE_W:
                if bird['y']-12 < p['top'] or bird['y']+12 > p['top']+PIPE_GAP:
                    hit = True
        if hit:
            state = DEAD
            shake = 15
            flash = 1.0
            emit(bird['x'], bird['y'], 25, (255,200,80), 5, 50)
            if score > best:
                best = score
                save_best()
            dead_timer = 0

    elif state == DEAD:
        bird['vy'] = min(bird['vy'] + GRAVITY, MAX_FALL)
        bird['y'] += bird['vy']
        bird['rot'] = min(90, bird['rot'] + 4)
        if bird['y'] + 14 > H - GROUND_H:
            bird['y'] = H - GROUND_H - 14
            bird['vy'] = 0
        dead_timer += 1

    else:  # MENU
        bird['y'] = H//2 + math.sin(pygame.time.get_ticks()/300) * 10
        bird['wing'] += 0.3
        bird['rot'] = 0

    # Particles
    for p in particles:
        p['x'] += p['vx']
        p['y'] += p['vy']
        p['vy'] += 0.2
        p['life'] -= 1
    particles = [p for p in particles if p['life'] > 0]

    # Clouds
    for c in clouds:
        c['x'] -= c['speed']
        if c['x'] < -100: c['x'] = W + 50

    ground_offset = (ground_offset + (PIPE_SPEED if state==PLAY else 1.5)) % 24
    if shake > 0: shake -= 1
    if flash > 0: flash -= 0.05

    # ---------- Draw ----------
    sx = random.randint(-shake, shake) if shake > 0 else 0
    sy = random.randint(-shake, shake) if shake > 0 else 0

    screen.blit(bg_surface, (sx, sy))

    t = pygame.time.get_ticks() / 1000
    draw_hills(t*20, (120, 170, 100, 180), H-GROUND_H-40, 20, 0.02)
    draw_hills(t*40, (90, 140, 80, 220), H-GROUND_H-10, 15, 0.03)

    for c in clouds:
        draw_cloud(c['x']+sx, c['y']+sy, c['s'])

    for p in pipes:
        draw_pipe(int(p['x']+sx), int(p['top']+sy))

    draw_ground()
    draw_bird(bird['x']+sx, bird['y']+sy, bird['rot'], bird['wing'])

    # Particles draw
    for p in particles:
        alpha = int(255 * p['life']/p['max'])
        sz = int(p['size'])
        s = pygame.Surface((sz*2, sz*2), pygame.SRCALPHA)
        pygame.draw.circle(s, (*p['color'], alpha), (sz, sz), sz)
        screen.blit(s, (int(p['x']-sz+sx), int(p['y']-sz+sy)))

    # Flash
    if flash > 0:
        f = pygame.Surface((W, H), pygame.SRCALPHA)
        f.fill((255,255,255, int(flash*255)))
        screen.blit(f, (0,0))

    # ---------- UI ----------
    if state == PLAY:
        draw_text_shadow(str(score), FONT, (255,255,255), (W//2, 50))
    elif state == MENU:
        draw_text_shadow("FLAPPY BIRD", BIG, (255,240,100), (W//2, 150))
        draw_text_shadow("Press SPACE or Click", SMALL, (255,255,255), (W//2, 380))
        draw_text_shadow(f"Best: {best}", SMALL, (255,220,100), (W//2, 420))
    elif state == DEAD and dead_timer > 20:
        panel = pygame.Surface((260, 200), pygame.SRCALPHA)
        pygame.draw.rect(panel, (220, 180, 100, 240), (0,0,260,200), border_radius=12)
        pygame.draw.rect(panel, (140, 100, 50), (0,0,260,200), 4, border_radius=12)
        screen.blit(panel, (W//2-130, 180))
        draw_text_shadow("GAME OVER", pygame.font.SysFont("arial", 28, bold=True),
                         (255,80,80), (W//2, 210))
        draw_text_shadow(f"Score: {score}", FONT, (255,255,255), (W//2+30, 270))
        draw_text_shadow(f"Best: {best}", FONT, (255,220,100), (W//2+30, 310))
        medal = get_medal(score)
        if medal:
            pygame.draw.circle(screen, medal[1], (W//2-70, 290), 22)
            pygame.draw.circle(screen, (255,255,255), (W//2-70, 290), 22, 3)
            draw_text_shadow(medal[0], SMALL, (255,255,255), (W//2-70, 290))
        if dead_timer > 30:
            draw_text_shadow("SPACE to continue", SMALL, (255,255,255), (W//2, 420))

    pygame.display.flip()

pygame.quit()
sys.exit()