import pygame, time, random
from ..utils.colors import HUD_TEXT, WHITE, NEON_PINK, NEON_YELLOW

TIPS = [
    "Breathe in...",
    "Watch it grow...",
    "Gentle moves. Soft light.",
    "Let the current guide you.",
    "Flow with the sound.",
]

class HUD:
    def __init__(self, font):
        self.font = font
        self.small = pygame.font.Font(None, 22)
        self.tip_time = 0
        self.tip = random.choice(TIPS)

    def draw_glass(self, surf, rect, alpha=32):
        glass = pygame.Surface(rect.size, pygame.SRCALPHA)
        glass.fill((255,255,255,alpha))
        blur = pygame.Surface((rect.width+8, rect.height+8), pygame.SRCALPHA)
        blur.fill((255,255,255,10))
        surf.blit(blur, (rect.x-4, rect.y-4))
        surf.blit(glass, rect)

    def draw(self, surf, score, best, session, paused=False):
        w,h = surf.get_size()
        # Top HUD
        panel = pygame.Rect(16, 12, 300, 64)
        self.draw_glass(surf, panel, alpha=26)
        t1 = self.font.render(f"Size: {score:.1f}", True, HUD_TEXT)
        t2 = self.small.render(f"Best: {best:.1f}  Session: {session}", True, HUD_TEXT)
        surf.blit(t1, (panel.x+12, panel.y+8))
        surf.blit(t2, (panel.x+12, panel.y+36))

        now = time.time()
        if now - self.tip_time > 6:
            self.tip_time = now
            self.tip = random.choice(TIPS)
        tip_text = self.font.render(self.tip, True, NEON_YELLOW if paused else HUD_TEXT)
        surf.blit(tip_text, (w//2 - tip_text.get_width()//2, h-40))

        # Controls hint (fade)
        hint = self.small.render("LMB: wave • R: restart • M: mute • Esc: menu", True, (180,200,200))
        surf.blit(hint, (w - hint.get_width() - 16, 16))
