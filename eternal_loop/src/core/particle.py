import random, math
import pygame
from dataclasses import dataclass, field
from typing import Tuple, List
from .easing import damp
from ..utils.colors import NEON_CYAN, NEON_PINK, NEON_YELLOW

def lerp(a,b,t): return a + (b-a)*t

@dataclass
class Particle:
    pos: pygame.Vector2
    vel: pygame.Vector2
    radius: float
    color: Tuple[int,int,int]
    phase: float = field(default_factory=lambda: random.random()*math.tau)

    def update(self, dt, flow_t=0.0):
        # gentle flow field
        self.phase += dt * 0.2
        flow = pygame.Vector2(math.cos(self.phase+flow_t), math.sin(self.phase*0.5+flow_t*0.7)) * 12
        self.vel += flow * dt * 0.2
        self.vel *= 0.995
        self.pos += self.vel * dt

    def draw(self, surf: pygame.Surface):
        # glow by layered circles
        for i,alpha in enumerate((40, 25, 14, 7)):
            rr = int(self.radius + i*4)
            glow = pygame.Surface((rr*2+2, rr*2+2), pygame.SRCALPHA)
            pygame.draw.circle(glow, (*self.color, alpha), (rr, rr), rr)
            surf.blit(glow, (self.pos.x-rr, self.pos.y-rr), special_flags=pygame.BLEND_PREMULTIPLIED)
        pygame.draw.circle(surf, self.color, self.pos, int(self.radius))

class Orb:
    def __init__(self, pos: Tuple[float,float], color=NEON_CYAN):
        self.pos = pygame.Vector2(pos)
        self.vel = pygame.Vector2(0,0)
        self.radius = 16
        self.color = color
        self.trail: List[pygame.Vector2] = []
        self.trail_max = 32
        self.breath = 0.0

    def update(self, dt, cursor: pygame.Vector2):
        # soft follow toward cursor
        self.pos = pygame.Vector2(damp(self.pos.x, cursor.x, 4.0, dt),
                                  damp(self.pos.y, cursor.y, 4.0, dt))
        # velocity (for trail)
        self.vel = (self.vel*0.9) + (cursor - self.pos) * 0.1
        # trail
        self.trail.append(self.pos.copy())
        if len(self.trail) > self.trail_max: self.trail.pop(0)
        # breathing
        self.breath += dt*0.6

    def grow(self, amount): self.radius = min(self.radius + amount, 240)
    def shrink(self, amount): self.radius = max(self.radius - amount, 6)

    def draw(self, surf: pygame.Surface):
        # trail
        for i,p in enumerate(self.trail[:-1]):
            t = i / (len(self.trail)-1 + 1e-5)
            a = int(120 * (1-t))
            r = int(lerp(self.radius*0.2, self.radius*0.6, t))
            pygame.draw.circle(surf, (*self.color, a), (int(p.x), int(p.y)), max(1,r), 0)
        # glow + breathing
        pulse = (math.sin(self.breath*2) + 1)/2 * 0.08
        base_r = self.radius*(1+pulse)
        for i,alpha in enumerate((50, 30, 18, 10, 6)):
            rr = int(base_r + i*6)
            glow = pygame.Surface((rr*2+2, rr*2+2), pygame.SRCALPHA)
            pygame.draw.circle(glow, (*self.color, alpha), (rr, rr), rr)
            surf.blit(glow, (self.pos.x-rr, self.pos.y-rr), special_flags=pygame.BLEND_PREMULTIPLIED)
        pygame.draw.circle(surf, self.color, (int(self.pos.x), int(self.pos.y)), int(base_r))
