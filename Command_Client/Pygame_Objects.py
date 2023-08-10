import pygame as pg

class ImgTile(pg.sprite.Sprite):
    def __init__(self, abs_pos,pos_to_screen, size, color=(200, 200, 200)):
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





