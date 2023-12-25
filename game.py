import pygame as pg
import time, os
from network import Network
from camera import Camera
from math import sqrt, sin, cos, radians, pi
from pygame.math import Vector2 as vec2
from numpy import clip
from random import randint, random
from input import InputBox, FONT
from hollow import textOutline


class FPS:

    def __init__(self):
        self.last = time.time()
        self.fps = 0

    def print(self):
        self.fps += 1
        now = time.time()
        if now - self.last > 1.0:
            self.fps = 0
            self.last = now


class Player:

    def __init__(self, x, y, color, r, name, score):
        self.x = x
        self.y = y
        self.color = color
        self.name = name
        self.score = score

    def update_pos(self, x, y):
        self.x = x
        self.y = y


class Game:

    def start(self):
        # инициализировать PyGame и получения имени
        print('Добро пожаловать!')
        self.pginit()
        self.menu()

        # установить соединение с сервером
        self.network = Network()
        self.network.connect(self.name)

        # инициализировать логику
        print('Загрузка!')
        self.gameinit()

        # старт игры
        print('Начало игры!')
        self.run()

    def get_id(self):
        # возвращает идентификатор пользователя, присвоенный сервером
        return self.network.id

    def menu(self):
        box = InputBox(self.width // 2 - 100, self.height // 2 - 16, 100, 32)
        done, quitting = False, False
        sphere_font = pg.font.SysFont('verdana', 100)
        nick_font = pg.font.SysFont('verdana', 50)
        sphere_text = sphere_font.render('SPHERE', True, pg.Color('chartreuse'))
        nick_text = nick_font.render('Введите имя:', True, pg.Color('chartreuse'))

        while not done:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    quitting = True
                if (name := box.handle_event(event)):
                    if len(name) > 20:
                        print('Имя слишком  длинное !')
                    else:
                        done = True

            keys = pg.key.get_pressed()
            if keys[pg.K_ESCAPE]:
                quitting = True

            if quitting:
                print('Выход из игры!')
                pg.quit()
                quit()

            box.update()

            self.win.fill((160, 160, 255))

            box.draw(self.win)
            self.win.blit(sphere_text, (self.width // 2 - sphere_text.get_width() // 2, 200))
            self.win.blit(nick_text, (150, self.height // 2 - nick_text.get_height() // 2))

            pg.display.flip()
            self.clock.tick(30)

        self.name = name

    def pginit(self):
        self.width, self.height = 1280, 720
        pg.init()
        os.environ['SDL_VIDEO_CENTERED'] = '1'
        self.win = pg.display.set_mode((self.width, self.height))
        pg.display.set_caption('SPHERE')
        self.clock = pg.time.Clock()

        self.lwidth, self.lheight = 200, 250
        self.lstart_x, self.lstart_y = self.width - self.lwidth - 20, 20
        self.lsurf = pg.Surface((self.lwidth, self.lheight))
        self.lsurf.set_alpha(100)
        self.lsurf.fill((0, 0, 0))

        self.swidth, self.sheight = 100, 50
        self.ssurf = pg.Surface((self.swidth, self.sheight))
        self.ssurf.set_alpha(100)
        self.lsurf.fill((0, 0, 0))

    def gameinit(self):
        self.fps = FPS()

        self.orb_radius = 10
        self.player_radius = 30
        self.scale = 5
        center = (self.width // 2 * self.scale, self.height // 2 * self.scale)

        self.pos = center
        self.vel = vec2(0, 0)
        self.speed = 200

        self.camera = Camera(self.width, self.height)
        self.camera.set_pos(center)

        pg.mouse.set_pos(self.width // 2, self.height // 2)

        self.name_font = pg.font.SysFont('verdana', 50)
        self.leader_font = pg.font.SysFont('verdana', 35)
        self.ui_font = pg.font.SysFont('verdana', 25)

        self.elapsed = 0

    def run(self):
        self.run = True

        while self.run:
            self.handle_events()
            self.update()
            self.draw()
            self.fps.print()
        self.end()
    def handle_events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.run = False

        keys = pg.key.get_pressed()
        if keys[pg.K_ESCAPE]:
            self.run = False

        mouse_pos = vec2(pg.mouse.get_pos())
        des_vel = (mouse_pos - vec2(self.camera.transform(*self.pos)))
        if des_vel.length() != 0:
            mult = min(des_vel.length(), 200) / 100
            des_vel = mult * des_vel.normalize()
        self.vel = self.vel.lerp(des_vel, 0.2)

    def update(self):
        # обновление время
        self.delta_time = self.clock.tick(120) * 0.001
        self.elapsed += self.delta_time

        # обновление позиции
        self.pos += self.vel * self.delta_time * self.speed
        self.pos.x = clip(self.pos.x, 0, self.width * self.scale)
        self.pos.y = clip(self.pos.y, 0, self.height * self.scale)
        pos = (int(self.pos.x), int(self.pos.y))

        # отправление позиции
        self.orbs, self.players, died, self.score = self.send_update(pos)
        player = self.players[self.get_id()]

        # обновление скорости
        factor = self.player_radius / player.r
        self.speed = sqrt(sqrt(factor)) * 200

        # если умер, сброс положения
        if died:
            self.pos = vec2(player.x, player.y)

        # обновление масштаба и положения камеры
        self.camera.set_pos(pos)
        scale = 1.5 * sqrt(self.player_radius / player.r)
        self.camera.set_scale(scale)

    def draw(self):
        self.win.fill((255, 255, 255))
        # рисование шаров
        for x, y, color in self.orbs:
            x, y = self.camera.transform(x, y)
            r = self.camera.getr(self.orb_radius)
            pg.draw.circle(self.win, color, (int(x), int(y)), int(r))

        # цвета
        white = 255, 255, 255
        black = 180, 180, 180

        # рисование игрока
        for p in sorted(self.players.values(), key=lambda p: p.r):
            x, y = self.camera.transform(p.x, p.y)
            r = self.camera.getr(p.r)
            pg.draw.polygon(self.win, self.darken(p.color), self.get_circle(x, y, r))
            pg.draw.polygon(self.win, p.color, self.get_circle(x, y, r - 10))
            text = textOutline(self.name_font, p.name, white, black)
            self.win.blit(text, (x - text.get_width() // 2, y - text.get_height() // 2))

        # таблица лидеров
        self.win.blit(self.lsurf, (self.lstart_x, self.lstart_y))

        text = self.leader_font.render('ЛИДЕРЫ', True, white)
        self.win.blit(text, (self.lstart_x + self.lwidth // 2 - text.get_width() // 2, self.lstart_y + 10))

        board_len = min(len(self.players), 5)
        for i, p in enumerate(sorted(self.players.values(), key=lambda p: -p.score)[:board_len]):
            text = self.ui_font.render(f'{i + 1}. {p.name}', True, white)
            self.win.blit(text, (self.lstart_x + self.lwidth // 10, self.lstart_y + 50 + i * 20))

        # счёт
        text = self.ui_font.render(f'Счёт: {self.score}', True, white)
        size_x, size_y = text.get_size()
        sstart_x, sstart_y = 20, self.height - size_y - 20

        dx, score = 75, self.score
        while score >= 100:
            dx += 10
            score //= 10

        size = self.ssurf.get_size()
        if size[0] != dx + 10:
            self.ssurf = pg.transform.scale(self.ssurf, (dx + 60, size_y + 10))

        self.win.blit(self.ssurf, (sstart_x, sstart_y))
        self.win.blit(text, (sstart_x + 5, sstart_y + 5))

        pg.display.flip()

    def get_circle(self, xoff, yoff, r, dalfa=5):
        angle, delta = 0, radians(dalfa)
        points, seed = [], self.elapsed * 2
        while angle < 2 * pi:
            x, y = cos(angle), sin(angle)
            rad = r + (r ** (3 / 4)) * 0.1
            points.append((int(x * rad + xoff), int(y * rad + yoff)))
            angle += delta
        return points

    def darken(self, color):
        r, g, b = color
        mult = 0.85
        return (int(mult * r), int(mult * g), int(mult * b))

    def send_update(self, pos):
        # отправка местоположения на сервер
        return self.network.send(pos)

    def end(self):
        print('Выход из игры!')
        pg.quit()
        self.network.disconnect()


game = Game()
game.start()