import pygame as pg

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
        self.target = offset_to_pos(pos)
        self.f_dpos = lambda dxy: 1/10 * dxy
        self.image = pg.surface.Surface([size, size], pg.SRCALPHA)
        pg.draw.circle(self.image, (color[0]/2, color[1]/2, color[2]/2), center=(size/2, size/2), radius=size/2)
        pg.draw.circle(self.image, color, center=(size/2, size/2), radius=size/3)
        self.image.convert_alpha()
        self.rect = self.image.get_rect()
        self.pos = list(offset_to_pos(pos))
        self.rect.center = self.pos

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
            self.target = self.offset_to_pos(bot_pos[self.id])
            self.pos[0] += self.f_dpos(self.target[0]-self.pos[0])
            self.pos[1] += self.f_dpos(self.target[1]-self.pos[1])
            self.rect.center = self.pos
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

    def update(self, list_accounted):
        if self.id not in list_accounted:  # bot is in server
            self.kill()

class ActiveText(pg.sprite.Sprite):
    """Display text to screen and notify user if the number drops below a certain number specified"""
    def __init__(self, pos, tcolor='white', font='freesansbold.ttf'):
        super().__init__()
        self.pos = pos
        self.color = tcolor
        self.health = 100
        self.font = pg.font.Font(font, 32)
        self.image = self.font.render(f'{self.health}%', True, tcolor)
        self.rect = self.image.get_rect()
        self.rect.topleft = pos

    def update(self, health_Missing):
        new_health = 100-health_Missing
        if self.health != new_health:
            self.image = self.font.render(f'{new_health}%', True, self.color)
            self.rect = self.image.get_rect()
            self.rect.topleft = self.pos
