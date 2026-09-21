import pygame
import math
import random

# Initialize
pygame.init()
WIDTH, HEIGHT = 1200, 750
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Procedural Skeleton Lizard 🦎")
clock = pygame.time.Clock()

# Colors - Black and White only
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
DARK_GRAY = (40, 40, 40)

# ============ VERTEBRA (SPINE SEGMENT) ============
class Vertebra:
    def __init__(self, x, y):
        self.pos = pygame.math.Vector2(x, y)
        self.angle = 0
        
    def update(self, target_pos, prev_vert=None, distance=20):
        if prev_vert is None:
            # Head follows mouse
            dx = target_pos[0] - self.pos.x
            dy = target_pos[1] - self.pos.y
            self.angle = math.atan2(dy, dx)
            dist = math.hypot(dx, dy)
            if dist > 5:
                self.pos.x += math.cos(self.angle) * min(dist * 0.1, 8)
                self.pos.y += math.sin(self.angle) * min(dist * 0.1, 8)
        else:
            # Follow previous vertebra
            dx = prev_vert.pos.x - self.pos.x
            dy = prev_vert.pos.y - self.pos.y
            self.angle = math.atan2(dy, dx)
            dist = math.hypot(dx, dy)
            if dist > distance:
                offset = dist - distance
                self.pos.x += math.cos(self.angle) * offset * 0.3
                self.pos.y += math.sin(self.angle) * offset * 0.3

# ============ BONE ============
class Bone:
    def __init__(self, start, end, thickness=3):
        self.start = start
        self.end = end
        self.thickness = thickness
        
    def draw(self, surface):
        pygame.draw.line(surface, WHITE, self.start, self.end, self.thickness)
        # Joint circles
        pygame.draw.circle(surface, WHITE, (int(self.start.x), int(self.start.y)), max(2, self.thickness))
        pygame.draw.circle(surface, WHITE, (int(self.end.x), int(self.end.y)), max(2, self.thickness))

# ============ LEG ============
class Leg:
    def __init__(self, spine_index, side, length=50):
        self.spine_index = spine_index
        self.side = side  # -1 for left, 1 for right
        self.length = length
        self.phase = random.uniform(0, math.pi * 2)
        self.foot_pos = None
        
    def update(self, spine, walk_cycle):
        # Get attachment point on spine
        attach_point = spine[self.spine_index].pos
        
        # Calculate foot position with walking motion
        base_x = attach_point.x + self.side * 40
        base_y = attach_point.y + 20
        
        # Walking animation
        walk_offset = math.sin(walk_cycle + self.phase) * 15
        self.foot_pos = pygame.math.Vector2(base_x + walk_offset, base_y)
        
        return attach_point, self.foot_pos
    
    def draw(self, surface, attach_point, foot_pos):
        if foot_pos:
            # Draw leg bones
            mid_point = (attach_point + foot_pos) / 2
            mid_point.x += self.side * 10
            
            # Upper leg
            pygame.draw.line(surface, WHITE, attach_point, mid_point, 3)
            pygame.draw.circle(surface, WHITE, (int(mid_point.x), int(mid_point.y)), 3)
            
            # Lower leg
            pygame.draw.line(surface, WHITE, mid_point, foot_pos, 2)
            pygame.draw.circle(surface, WHITE, (int(foot_pos.x), int(foot_pos.y)), 2)

# ============ SKULL ============
class Skull:
    def __init__(self):
        self.size = 15
        
    def draw(self, surface, head_pos, head_angle):
        # Skull position
        x = head_pos.x + math.cos(head_angle) * 20
        y = head_pos.y + math.sin(head_angle) * 20
        
        # Main skull (cranium)
        pygame.draw.circle(surface, WHITE, (int(x), int(y)), self.size, 2)
        
        # Snout
        snout_x = x + math.cos(head_angle) * self.size
        snout_y = y + math.sin(head_angle) * self.size
        pygame.draw.circle(surface, WHITE, (int(snout_x), int(snout_y)), 6, 2)
        
        # Eye sockets
        eye_offset = 5
        for side in [-1, 1]:
            ex = x + math.cos(head_angle + 0.3) * 8 * side
            ey = y + math.sin(head_angle + 0.3) * 8 * side
            pygame.draw.circle(surface, WHITE, (int(ex), int(ey)), 3, 1)
        
        # Teeth
        teeth_count = 5
        for i in range(teeth_count):
            angle = head_angle + (i - teeth_count/2) * 0.2
            tx = snout_x + math.cos(angle) * 8
            ty = snout_y + math.sin(angle) * 8
            pygame.draw.line(surface, WHITE, (snout_x, snout_y), (tx, ty), 1)

# ============ RIBS ============
class Ribs:
    def __init__(self, start_idx, end_idx):
        self.start_idx = start_idx
        self.end_idx = end_idx
        
    def draw(self, surface, spine):
        for i in range(self.start_idx, min(self.end_idx, len(spine))):
            vert = spine[i]
            # Draw ribs on both sides
            for side in [-1, 1]:
                rib_angle = vert.angle + math.pi/2 * side
                rib_length = 25 + (i - self.start_idx) * 2
                
                end_x = vert.pos.x + math.cos(rib_angle) * rib_length
                end_y = vert.pos.y + math.sin(rib_angle) * rib_length
                
                pygame.draw.line(surface, WHITE, vert.pos, (end_x, end_y), 2)
                pygame.draw.circle(surface, WHITE, (int(end_x), int(end_y)), 2)

# ============ MAIN LIZARD ============
class SkeletonLizard:
    def __init__(self):
        # Create spine (vertebrae)
        self.spine = [Vertebra(WIDTH//2, HEIGHT//2) for _ in range(22)]
        
        # Create legs (attach to specific vertebrae)
        self.legs = [
            Leg(4, -1),   # Front left
            Leg(4, 1),    # Front right
            Leg(14, -1),  # Back left
            Leg(14, 1),   # Back right
        ]
        
        # Skull
        self.skull = Skull()
        
        # Ribs
        self.ribs = Ribs(3, 12)
        
        # Movement
        self.walk_cycle = 0
        self.speed = 0
        
    def update(self, mouse_pos):
        # Update spine (inverse kinematics)
        for i, vert in enumerate(self.spine):
            if i == 0:
                vert.update(mouse_pos)
            else:
                vert.update(None, self.spine[i-1])
        
        # Calculate speed for walk animation
        head = self.spine[0]
        dx = mouse_pos[0] - head.pos.x
        dy = mouse_pos[1] - head.pos.y
        self.speed = math.hypot(dx, dy) * 0.01
        
        if self.speed > 0.1:
            self.walk_cycle += 0.15 + self.speed
        
        # Update legs
        for leg in self.legs:
            leg.update(self.spine, self.walk_cycle)
    
    def draw(self, surface):
        # Draw ribs first (behind spine)
        self.ribs.draw(surface, self.spine)
        
        # Draw legs
        for leg in self.legs:
            attach, foot = leg.update(self.spine, self.walk_cycle)
            leg.draw(surface, attach, foot)
        
        # Draw spine
        for i in range(len(self.spine) - 1):
            v1 = self.spine[i]
            v2 = self.spine[i + 1]
            thickness = max(2, 5 - i // 5)  # Taper towards tail
            pygame.draw.line(surface, WHITE, v1.pos, v2.pos, thickness)
            # Draw vertebra joint
            pygame.draw.circle(surface, WHITE, (int(v1.pos.x), int(v1.pos.y)), max(3, thickness))
        
        # Draw skull
        self.skull.draw(surface, self.spine[0].pos, self.spine[0].angle)
        
        # Draw tail tip
        tail = self.spine[-1]
        pygame.draw.circle(surface, WHITE, (int(tail.pos.x), int(tail.pos.y)), 4)

# ============ MAIN LOOP ============
def main():
    running = True
    mouse_pos = (WIDTH//2, HEIGHT//2)
    
    lizard = SkeletonLizard()
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEMOTION:
                mouse_pos = event.pos
        
        # Update
        lizard.update(mouse_pos)
        
        # Draw
        screen.fill(BLACK)
        
        # Draw grid (subtle)
        for x in range(0, WIDTH, 100):
            pygame.draw.line(screen, DARK_GRAY, (x, 0), (x, HEIGHT), 1)
        for y in range(0, HEIGHT, 100):
            pygame.draw.line(screen, DARK_GRAY, (0, y), (WIDTH, y), 1)
        
        # Draw lizard
        lizard.draw(screen)
        
        # Instructions
        font = pygame.font.Font(None, 36)
        text = font.render("Move mouse to control skeleton", True, DARK_GRAY)
        screen.blit(text, (10, 10))
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()

if __name__ == "__main__":
    main()