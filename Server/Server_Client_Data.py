from PIL import Image
import random
import numpy as np

class ServerData:
    def __init__(self, file_name, corner_pos, ignored_color=(125, 230, 242)):
        """Class which holds all of the data that the server needs to keep track of in order to pass data from
        one client to the other
        contents:
            -"""
        self.ignored_color = ignored_color
        self.keep_alive = True
        self.corner_pos = corner_pos
        self.bad_blocks = []
        self.update_blocks = []
        self.bot_positions = {}
        self.bot_targets = {}
        self.file_name = file_name
        img = Image.open(file_name)
        self.get_image_coordinates(img, ignored_color)
        self.shuffle()

    def nearest_bad_block(self, bot_name):
        bot_pos = self.bot_positions[bot_name]
        if self.bad_blocks:
            nearest_block = 0
            min_dist = 100_0000
            for i, bad in enumerate(self.bad_blocks):
                diff = (bot_pos[0]-bad[0], bot_pos[1]-bad[1])
                dist = np.sqrt((diff[0])**2 + (diff[1])**2)
                if dist < min_dist:
                    min_dist = dist
                    nearest_block = i
            return self.bad_blocks.pop(nearest_block)
        else:
            return ()

    def get_oldest_update(self):
        """Gets Oldest block updated in queue and assigns it before moving it to the back of the line"""
        pos = self.update_blocks.pop(0)
        self.update_blocks.append(pos)
        return pos

    def get_image_coordinates(self, img, ignored):
        """Identifies Pixels that need to be checked"""
        size = img.size
        x_size, y_size = size
        for x in range(x_size):
            for y in range(y_size):
                color = img.getpixel((x, y))
                if color != ignored:
                    self.update_blocks.append((x+self.corner_pos[0], y+self.corner_pos[1]))

    def shuffle(self):
        random.shuffle(self.update_blocks)

    def prioritize_area(self, pos_range):
        tl, br = pos_range
        for x in range(round(tl[0]), round(br[0])):
            for y in range(round(tl[1]), round(br[1])):
                pos = (x, y)
                if pos in self.update_blocks:
                    self.update_blocks.remove(pos)
                    self.update_blocks.insert(0, pos)

    def reboot_all(self):
        for key in self.bot_targets:
            self.bot_targets[key] = 'r'  # for reboot

