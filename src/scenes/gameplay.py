import pygame
from ..core.game import GameCore
from ..utils.colors import WHITE

class GameplayScene:
    def __init__(self, game):
        self.game = game
        self.core = game.core

    def handle_event(self, e):
        if e.type == pygame.KEYDOWN:
            if e.key == pygame.K_ESCAPE:
                self.core.end_session()
                return 'menu'
            if e.key == pygame.K_r:
                self.core.end_session()
                self.core.reset()
            if e.key == pygame.K_SPACE:
                self.core.toggle_pause()
            if e.key == pygame.K_m:
                self.core.sound.toggle()
        if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
            self.core.emit_wave(pygame.mouse.get_pos())

    def update(self, dt):
        self.core.update(dt)

    def draw(self, screen):
        self.core.draw()
        if self.core.paused:
            w,h = screen.get_size()
            pause = self.game.bigfont.render("PAUSED", True, WHITE)
            screen.blit(pause, (w//2 - pause.get_width()//2, h//2 - 40))
