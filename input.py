import pygame as pg

pg.init()
COLOR_INACTIVE = pg.Color('deeppink')
COLOR_ACTIVE = pg.Color('deeppink')
FONT = pg.font.Font(None, 32)

# ввод имени
class InputBox:

    def __init__(self, x, y, w, h, text=''):
        self.rect = pg.Rect(x, y, w, h)
        self.color = pg.Color('deeppink')
        self.text = text
        self.txt_surface = FONT.render(text, True, self.color)

    def handle_event(self, event):
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_RETURN:
                name = self.text
                self.text = ''
                return name
            elif event.key == pg.K_BACKSPACE:
                self.text = self.text[:-1]
            else:
                self.text += event.unicode
            self.txt_surface = FONT.render(self.text, True, self.color)

        return False

    def update(self):
        # размер поля в соответствии  с именем
        width = max(200, self.txt_surface.get_width()+10)
        self.rect.w = width

    def draw(self, screen):
        screen.blit(self.txt_surface, (self.rect.x+5, self.rect.y+5))
        pg.draw.rect(screen, self.color, self.rect, 2)