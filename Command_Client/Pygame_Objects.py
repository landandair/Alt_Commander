import pygame as pg

class ImgTile(pg.sprite.Sprite):
    def __init__(self, abs_pos, pos_to_screen, size, color=(200, 200, 200)):
        super().__init__()
        self.pos = abs_pos
        self.image = pg.surface.Surface([size, size])
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.center = pos_to_screen(abs_pos)

class SelectionBox(pg.sprite.Sprite):
    def __init__(self, corner, color=(200, 200, 200)):
        super().__init__()
        self.pos = corner
        self.color = color
        self.image = pg.surface.Surface([100, 1])
        self.image.set_alpha(100)
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.center = corner

    def update(self):
        new_corner = pg.mouse.get_pos()
        size = [self.pos[0]-new_corner[0], self.pos[1]-new_corner[1]]
        center = ((self.pos[0] + new_corner[0])/2, (self.pos[1] + new_corner[1])/2)
        self.image = pg.transform.scale(self.image, (abs(size[0]), abs(size[1])))
        self.image.fill(self.color)
        self.rect = self.image.get_rect()
        self.rect.center = center

class Background(pg.sprite.Sprite):
    def __init__(self, image, width, height, center):
        super().__init__()
        self.image = pg.image.load(image)
        self.image = pg.transform.scale(self.image, (int(width), int(height))).convert()
        self.rect = self.image.get_rect()
        self.rect.center = center


class BotPosIndicator(pg.sprite.Sprite):
    def __init__(self, id, pos, offset_to_pos, size, color=(0, 255, 0)):
        super().__init__()
        self.color = color
        self.id = id
        self.size = size
        self.offset_to_pos = offset_to_pos
        self.image = pg.surface.Surface([size, size], pg.SRCALPHA)
        pg.draw.circle(self.image, (color[0]/2, color[1]/2, color[2]/2), center=(size/2, size/2), radius=size/2)
        pg.draw.circle(self.image, color, center=(size/2, size/2), radius=size/3)
        self.image.convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.center = offset_to_pos(pos)

    def update(self, bot_dict, bot_pos):
        color = self.color
        size = self.size
        if self.id in bot_pos:  # bot is in server
            if not bot_dict[self.id]:  # Bot is not selected
                pg.draw.circle(self.image, (color[0]/2, color[1]/2, color[2]/2), center=(size/2, size/2), radius=size/2)
                pg.draw.circle(self.image, color, center=(size/2, size/2), radius=size/3)
            else:
                pg.draw.circle(self.image, (color[0]/2, color[1]/2, color[2]/2), center=(size/2, size/2), radius=size/2)
            self.image.convert_alpha()
            self.rect.center = self.offset_to_pos(bot_pos[self.id])
        else:  # Something went wrong
            bot_dict.pop(self.id)
            self.kill()


class BadBlockIndicator(pg.sprite.Sprite):
    def __init__(self, pos, offset_to_pos, size, color=(255, 0, 0)):
        super().__init__()
        self.color = color
        self.id = pos
        self.size = size
        self.offset_to_pos = offset_to_pos
        self.image = pg.surface.Surface([size, size], pg.SRCALPHA)
        pg.draw.circle(self.image, (color[0]/2, color[1]/2, color[2]/2), center=(size/2, size/2), radius=size/2)
        pg.draw.circle(self.image, color, center=(size/2, size/2), radius=size/3)
        self.image.convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.center = offset_to_pos(pos)

    def update(self, list_accounted, bad_list):
        color = self.color
        size = self.size
        if self.id in bad_list:  # bot is in server
            # Bot is not selected
            pg.draw.circle(self.image, (color[0]/2, color[1]/2, color[2]/2), center=(size/2, size/2), radius=size/2)
            pg.draw.circle(self.image, color, center=(size/2, size/2), radius=size/3)
            self.image.convert_alpha()
            self.rect.center = self.offset_to_pos(self.id)
        else:  # Something went wrong
            list_accounted.remove(self.id)
            self.kill()


