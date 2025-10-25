import pygame
from ..utils.colors import DARK_BG, NEON_CYAN, NEON_PINK, NEON_YELLOW, WHITE
from ..core.game import GameCore

class MenuScene:
    def __init__(self, game):
        self.game = game
        self.title = pygame.font.Font(None, 96).render("ORB GROWER", True, NEON_CYAN)
        self.font = pygame.font.Font(None, 36)
        self.t = 0.0

    def handle_event(self, e):
        if e.type == pygame.KEYDOWN:
            if e.key == pygame.K_1 or e.key == pygame.K_RETURN:
                return 'gameplay'
            if e.key == pygame.K_2:
                return 'relax'
            if e.key == pygame.K_m:
                self.game.core.sound.toggle()
        if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
            return 'gameplay'

    def update(self, dt):
        self.t += dt

    def draw(self, screen):
        w,h = screen.get_size()
        screen.fill(DARK_BG)
        # subtle background pulses
        glow = pygame.Surface((w,h), pygame.SRCALPHA)
        import math
        for r,c in [(140, NEON_CYAN), (220, NEON_PINK)]:
            a = 40 + int(10*math.sin(self.t*0.7+r*0.01))
            pygame.draw.circle(glow, (*c,a), (w//2, h//2), r, 0)
        screen.blit(glow, (0,0))

        screen.blit(self.title, (w//2 - self.title.get_width()//2, h//3-40))
        t1 = self.font.render("1 — Play", True, WHITE)
        t2 = self.font.render("2 — Relax Mode", True, WHITE)
        t3 = self.font.render("M — Toggle sound", True, WHITE)
        screen.blit(t1, (w//2 - t1.get_width()//2, h//2))
        screen.blit(t2, (w//2 - t2.get_width()//2, h//2 + 42))
        screen.blit(t3, (w//2 - t3.get_width()//2, h//2 + 84))
