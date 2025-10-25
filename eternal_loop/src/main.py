import pygame, sys, time
from core.game import GameCore
from scenes.menu import MenuScene
from scenes.gameplay import GameplayScene
from scenes.relax_mode import RelaxScene

WIDTH, HEIGHT = 1280, 720
FPS = 90

class App:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Orb Grower — Eternal Loop")
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.SRCALPHA)
        self.clock = pygame.time.Clock()
        self.core = GameCore(self.screen, self.clock)
        self.font = pygame.font.Font(None, 28)
        self.bigfont = pygame.font.Font(None, 64)

        self.scene_name = 'menu'
        self.scenes = {
            'menu': MenuScene(self),
            'gameplay': GameplayScene(self),
            'relax': RelaxScene(self),
        }

    def switch(self, name):
        if name == 'relax':
            self.scenes['relax'] = RelaxScene(self)  # reinit to clear hazards
        self.scene_name = name

    def run(self):
        last_time = time.perf_counter()
        while True:
            now = time.perf_counter()
            dt = now - last_time
            last_time = now
            # clamp dt to avoid huge steps
            dt = min(dt, 1/30)

            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    self.core.end_session()
                    pygame.quit(); sys.exit(0)
                res = self.scenes[self.scene_name].handle_event(e)
                if isinstance(res, str):
                    self.switch(res)

            self.scenes[self.scene_name].update(dt)
            self.scenes[self.scene_name].draw(self.screen)

            pygame.display.flip()
            self.clock.tick(FPS)

if __name__ == '__main__':
    App().run()
