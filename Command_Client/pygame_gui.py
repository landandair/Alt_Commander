import sys
import pygame as pg
import numpy as np
from PIL import Image
import Pygame_Objects

class Window:
    def __init__(self, cmd_data):
        self.cmd_data = cmd_data
        pg.init()
        self.image = Image.open('template_img.png')
        self.h_w = self.image.size[1]/self.image.size[0]  # height to width Ratio
        self.monitor_size = np.array((pg.display.Info().current_w, pg.display.Info().current_h))
        if self.monitor_size[0] * self.h_w > self.monitor_size[1]:
            self.w = self.monitor_size[1]/self.h_w
        else:
            self.w = self.monitor_size[0]
        self.h = self.w * self.h_w

        self.screen = pg.display.set_mode((0, 0), pg.FULLSCREEN)
        # Sprite Groups
        self.background = pg.sprite.Group()
        self.make_tiles()

        # Objects
        self.bot_group = pg.sprite.Group()
        # Ui
        self.ui_elements = pg.sprite.Group()
        self.selection_boxes = pg.sprite.Group()

        # Misc Vars
        self.clock = pg.time.Clock()
        corner = self.cmd_data.corner_pos
        pixel_size = self.w/self.image.size[0]
        x_start = (self.monitor_size[0] - self.w)/2 + pixel_size/2
        y_start = (self.monitor_size[1] - self.h)/2 + pixel_size/2
        self.abs_to_pos = lambda pos: ((pos[0]-corner[0])*pixel_size + x_start, (pos[1]-corner[1])*pixel_size + y_start)

    def update(self):
        self.manage_events()
        # UI
        self.ui_elements.update()
        self.selection_boxes.update()
        # display layer from bottom to top
        self.screen.fill((20, 20, 20))
        self.background.draw(self.screen)
        # Ui
        self.ui_elements.draw(self.screen)
        self.selection_boxes.draw(self.screen)
        pg.display.flip()
        self.clock.tick(120)

    def manage_events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.cmd_data.running = False
                pg.quit()
                sys.exit()
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    self.cmd_data.running = False
                    pg.quit()
                    sys.exit()
            if event.type == pg.MOUSEBUTTONDOWN:
                if event.button == 1:
                    box = Pygame_Objects.SelectionBox(pg.mouse.get_pos(), color='grey')
                    self.selection_boxes.add(box)
                elif event.button == 3:
                    box = Pygame_Objects.SelectionBox(pg.mouse.get_pos(), color='red')
                    self.selection_boxes.add(box)
            if event.type == pg.MOUSEBUTTONUP:
                if event.button == 1:
                    self.select_area()
                if event.button == 3:
                    self.select_area()

    def make_tiles(self):
        center = (self.monitor_size[0]/2, self.monitor_size[1]/2)
        bg = Pygame_Objects.Background('template_img.png', self.w, self.h, center)
        self.background.add(bg)


    def select_area(self):
        # Collide the box surface with the bot sprites to get the selected bots, add them to a list
        self.selection_boxes.empty()
