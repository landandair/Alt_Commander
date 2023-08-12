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

        corner = self.cmd_data.corner_pos
        pixel_size = self.w/self.image.size[0]
        x_start = (self.monitor_size[0] - self.w)/2 + pixel_size/2
        y_start = (self.monitor_size[1] - self.h)/2 + pixel_size/2
        self.abs_to_pos = lambda pos: ((pos[0]-corner[0])*pixel_size + x_start, (pos[1]-corner[1])*pixel_size + y_start)
        self.pos_to_abs = lambda abs: ((abs[0] - x_start)/pixel_size + corner[0],
                                       (abs[1] - y_start)/pixel_size + corner[1])

        self.screen = pg.display.set_mode((0, 0), pg.FULLSCREEN)
        # Sprite Groups
        self.background = pg.sprite.Group()
        self.make_tiles()

        # Objects
        self.bot_group = pg.sprite.Group()
        self.bot_dict = {}
        self.check_for_new_bots()

        # Ui
        self.ui_elements = pg.sprite.Group()
        self.selection_boxes = pg.sprite.Group()

        # Misc Vars
        self.clock = pg.time.Clock()

    def update(self):
        self.manage_events()
        # UI
        self.check_for_new_bots()
        self.bot_group.update(self.bot_dict, self.cmd_data.bot_positions)
        self.ui_elements.update()
        self.selection_boxes.update()
        # display layer from bottom to top
        self.screen.fill((40, 40, 40))
        self.background.draw(self.screen)
        # Ui
        self.bot_group.draw(self.screen)
        self.ui_elements.draw(self.screen)
        self.selection_boxes.draw(self.screen)
        pg.display.flip()
        self.clock.tick(60)

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
                if event.key == pg.K_r:  # Shuffle movement queue
                    self.cmd_data.shuffle = True
                if event.key == pg.K_SPACE: # Command selected bots to area
                    self.command_selected()

            if event.type == pg.MOUSEBUTTONDOWN:
                if event.button == 1:
                    box = Pygame_Objects.SelectionBox(pg.mouse.get_pos(), color='grey')
                    self.selection_boxes.add(box)
                elif event.button == 3:
                    box = Pygame_Objects.SelectionBox(pg.mouse.get_pos(), color='red')
                    self.selection_boxes.add(box)
            if event.type == pg.MOUSEBUTTONUP:
                if event.button == 1:
                    self.select_bots()
                if event.button == 3:
                    self.select_area()

    def make_tiles(self):
        center = (self.monitor_size[0]/2, self.monitor_size[1]/2)
        bg = Pygame_Objects.Background('template_img.png', self.w, self.h, center)
        self.background.add(bg)

    def check_for_new_bots(self):
        for id in self.cmd_data.bot_positions:
            if id not in self.bot_dict:
                pos = self.cmd_data.bot_positions[id]
                bot = Pygame_Objects.BotPosIndicator(id, pos, self.abs_to_pos, 20)
                self.bot_dict[id] = False  # Selected
                self.bot_group.add(bot)

    def select_bots(self):
        # Collide the box surface with the bot sprites to get the selected bots, add them to a list
        for bot in self.bot_dict:  # Deselect everything
            self.bot_dict[bot] = False
        for box in self.selection_boxes:
            collisions = pg.sprite.spritecollide(box, self.bot_group, dokill=False)
            for bot in collisions:  # Select collided sprites
                self.bot_dict[bot.id] = True
        self.selection_boxes.empty()

    def command_selected(self):
        pos = pg.mouse.get_pos()
        abs_pos = self.pos_to_abs(pos)
        abs_pos = (round(abs_pos[0]), round(abs_pos[1]))
        for id in self.bot_dict:
            if self.bot_dict[id]: # is the bot selected
                self.cmd_data.moves[id] = abs_pos

    def select_area(self):
        # Set bounds of box to be the move area for the bots moved to the front of the line
        for box in self.selection_boxes:
            self.cmd_data.goto_range = (self.pos_to_abs(box.rect.topleft), self.pos_to_abs(box.rect.bottomright))
        self.selection_boxes.empty()
