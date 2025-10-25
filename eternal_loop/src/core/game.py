import json, os, random, math
import pygame
from .particle import Particle, Orb
from .sound import SoundManager
from ..utils.colors import DARK_BG, NEON_CYAN, NEON_PINK, NEON_YELLOW, PALETTE
from ..ui.hud import HUD

SAVE_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "..", "save.json")

def load_save():
    try:
        with open(SAVE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"best_size": 0, "sessions": 0, "achievements": []}

def save_game(data):
    try:
        with open(SAVE_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    except Exception:
        pass

class GameCore:
    def __init__(self, screen, clock):
        self.screen = screen
        self.clock = clock
        self.w, self.h = self.screen.get_size()
        self.surf = pygame.Surface((self.w, self.h), pygame.SRCALPHA)
        self.overlay = pygame.Surface((self.w, self.h), pygame.SRCALPHA)
        self.sound = SoundManager()
        self.font = pygame.font.Font(None, 28)
        self.bigfont = pygame.font.Font(None, 64)
        self.hud = HUD(self.font)

        self.reset()
        self.sound.loop_ambient()

    def reset(self):
        self.time = 0.0
        self.flow_t = random.random()*10
        self.player = Orb((self.w/2, self.h/2), color=random.choice(PALETTE))
        self.food = []
        self.hazard = []
        self.waves = []
        self.spawn_timer = 0.0
        self.paused = False
        self.session_score = 0.0
        self.save = load_save()
        self.save['sessions'] += 1
        save_game(self.save)

    def toggle_pause(self):
        self.paused = not self.paused

    def emit_wave(self, pos):
        self.waves.append([pygame.Vector2(pos), 0.0, random.choice(PALETTE)])
        self.sound.play('woosh')

    def spawn_particles(self):
        # Procedural: density scales with size, keep balance of food/hazard
        if len(self.food) < 120:
            for _ in range(2):
                r = random.uniform(3, max(5, 10 - self.player.radius*0.02))
                p = Particle(pygame.Vector2(random.randrange(0,self.w), random.randrange(0,self.h)),
                             pygame.Vector2(random.uniform(-20,20), random.uniform(-20,20)),
                             r, random.choice((NEON_CYAN, NEON_YELLOW)))
                self.food.append(p)
        if len(self.hazard) < 18:
            r = random.uniform(self.player.radius*1.1, self.player.radius*1.6 + 18)
            p = Particle(pygame.Vector2(random.randrange(0,self.w), random.randrange(0,self.h)),
                         pygame.Vector2(random.uniform(-10,10), random.uniform(-10,10)),
                         r, NEON_PINK)
            self.hazard.append(p)

    def wrap(self, p):
        if p.pos.x < -50: p.pos.x = self.w+50
        if p.pos.x > self.w+50: p.pos.x = -50
        if p.pos.y < -50: p.pos.y = self.h+50
        if p.pos.y > self.h+50: p.pos.y = -50

    def update(self, dt):
        if self.paused: return

        self.time += dt
        self.flow_t += dt*0.2
        self.spawn_timer += dt
        cursor = pygame.Vector2(pygame.mouse.get_pos())

        self.player.update(dt, cursor)

        if self.spawn_timer > 0.15:
            self.spawn_particles()
            self.spawn_timer = 0.0

        # Update particles
        for p in self.food:
            p.update(dt, self.flow_t)
            self.wrap(p)
        for p in self.hazard:
            p.update(dt, self.flow_t*0.7)
            self.wrap(p)

        # Collisions
        pr = self.player.radius
        ppos = self.player.pos
        ate = []
        for p in self.food:
            if p.pos.distance_to(ppos) < (p.radius + pr*0.8):
                ate.append(p)
                self.player.grow(p.radius*0.15)
                self.session_score = max(self.session_score, self.player.radius)
                self.sound.play('eat')
        self.food = [p for p in self.food if p not in ate]

        for p in self.hazard:
            if p.pos.distance_to(ppos) < (p.radius - pr*0.5):
                # too big -> shrink
                self.player.shrink((p.radius - pr)*0.12)
                self.sound.play('bloom')

        # Achievements
        if self.player.radius >= 100 and 'Gleam 100' not in self.save['achievements']:
            self.save['achievements'].append('Gleam 100')
            save_game(self.save)

        # waves expand
        for w in self.waves:
            w[1] += dt*180
        self.waves = [w for w in self.waves if w[1] < max(self.w,self.h)*1.2]

    def draw_background(self):
        # Motion blur: slightly fade previous frame
        self.overlay.fill((0,0,0,12))
        self.surf.blit(self.overlay, (0,0))

        # slow color shift
        t = (math.sin(self.time*0.05)+1)/2
        bg = (int(6+10*t), int(8+14*t), int(12+20*t))
        self.screen.fill(bg)

        # soft vignette
        vignette = pygame.Surface((self.w, self.h), pygame.SRCALPHA)
        pygame.draw.rect(vignette, (0,0,0,40), (0,0,self.w,self.h), border_radius=0)
        self.screen.blit(vignette, (0,0))

    def draw(self):
        self.draw_background()

        # waves
        for pos, radius, color in self.waves:
            pygame.draw.circle(self.surf, (*color, 40), (int(pos.x), int(pos.y)), int(radius), width=2)

        # particles
        for p in self.food: p.draw(self.surf)
        for p in self.hazard: p.draw(self.surf)

        # player
        self.player.draw(self.surf)

        # compose
        self.screen.blit(self.surf, (0,0))

        # HUD
        best = max(self.save.get('best_size', 0), self.session_score)
        self.hud.draw(self.screen, self.player.radius, best, self.save.get('sessions', 1), paused=self.paused)

    def end_session(self):
        self.save['best_size'] = max(self.save.get('best_size', 0), self.player.radius)
        save_game(self.save)
