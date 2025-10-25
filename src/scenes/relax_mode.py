import pygame, random
from ..core.game import GameCore
from ..utils.colors import NEON_CYAN, NEON_PINK, NEON_YELLOW

class RelaxScene:
    def __init__(self, game):
        self.game = game
        self.core = game.core
        # In relax mode we reset with fewer hazards
        self.core.reset()
        self.core.hazard.clear()

    def handle_event(self, e):
        if e.type == pygame.KEYDOWN:
            if e.key == pygame.K_ESCAPE:
                self.core.end_session()
                return 'menu'
            if e.key == pygame.K_m:
                self.core.sound.toggle()
        if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
            self.core.emit_wave(pygame.mouse.get_pos())

    def update(self, dt):
        # Keep hazards off
        self.core.hazard.clear()
        self.core.update(dt)

    def draw(self, screen):
        self.core.draw()
