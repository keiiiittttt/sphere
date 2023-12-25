import socket
import _pickle as pickle
import time
from random import *
from math import sqrt, sin
from threading import Thread
from numpy import clip

class Player:

        def __init__(self, x, y, color, r, name, score):
                self.x = x
                self.y = y
                self.color = color
                self.r = r
                self.name = name
                self.score = score


        def update_pos(self, x, y):
                self.x = x
                self.y = y



class Server:

        HEADER = 10

        def __init__(self):
                self.serv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.host_name = socket.gethostname()
                self.port = 5555
                #  self.ip_addr = ''
                self.ip_addr = socket.gethostbyname(self.host_name)
                #  self.ip_addr = ''

        def start(self):
        # инициализирование сервера
                try:
                        self.serv.bind((self.ip_addr, self.port))

                except socket.error as e:
                        print(e)
                        print('Ошибка запуска')
                        quit()

                self.serv.listen()
                print(f'Сервер запущен с  {self.ip_addr}!')

                # логика игры
                print('Загрузка игры!')
                self.gameinit()

                # начало игры
                print('Приятной игры!')
                self.run()


        def gameinit(self):
                self.client_id = 0
                self.width, self.height = 1280, 720
                self.scale = 5
                self.colors = [(191, 255, 0), (255, 20, 147), (191, 0, 255), (135, 206, 250), (255, 53, 94), (32, 178, 170), (160,160,255),(209, 226, 49)]
                self.orb_radius = 10
                self.player_radius = 30
                self.orbs = []
                self.generate_orbs(randint(700, 700))
                self.players = {}


        def generate_orbs(self, count):
                for i in range(count):
                        x, y = self.rand_location()
                        color = self.pick_color()
                        self.orbs.append((x, y, color))


        def rand_location(self):
                return (randint(0, self.width * self.scale), randint(0, self.height * self.scale))


        def pick_color(self):
        # рандомный цвет
                return choice(self.colors)


        def pick_location(self):
        # рандомная позиция игрока
                good = False
                while not good:
                        good = True
                        x, y = self.rand_location()
                        for p in self.players.values():
                                if self.collide(x, y, self.player_radius, p.x, p.y, p.r):
                                        good = False
                                        break
                return x, y


        def collide(self, x1, y1, r1, x2, y2, r2):
                return (x1 - x2) ** 2 + (y1 - y2) ** 2 <= (r1 + r2) ** 2


        def run(self):
                print('Ожидание подключения!')

                try:
                        while True:
                        # сервер ожидает подключения
                                conn, addr = self.serv.accept()
                                print(f'Установленно соединение с {addr} !')
                                Thread(target=self.handle_client, args=(conn,)).start()

                except KeyboardInterrupt:
                        pass

                print('Завершение работы сервера!')
                self.serv.close()


        def send(self, conn, data):
                conn.send(pickle.dumps(data))


        def receive(self, conn):
                recv = conn.recv(40)
                if not recv:
                        return False
                return pickle.loads(recv)


        def eat_orbs(self, p):
                for i, orb in enumerate(self.orbs):
                        x, y = orb[0], orb[1]
                        if self.collide(x, y, self.orb_radius, p.x, p.y, p.r * 0.9):
                        # если столкновение с шаром то увеление счёта
                                p.score += 1

                                mini = int(p.r)
                                maxix = max(3 * int(p.r), self.width)
                                maxiy = max(3 * int(p.r), self.height)

                                xoff = randint(mini, maxix)
                                if randint(0, 1) == 1:
                                        xoff *= -1
                                yoff = randint(mini, maxiy)
                                if randint(0, 1) == 1:
                                        yoff *= -1

                                x, y = clip(x + xoff, 0, self.width * self.scale),\
                                           clip(y + yoff, 0, self.height * self.scale)

                                self.orbs[i] = (x, y, orb[2])
                                break


                r = self.player_radius + (p.score - 10) ** (3/4) * 2
                p.r += (r - p.r) * 0.1


        def check_collisions(self, p):
        #проверка был ли игрок съедене
                for player in self.players.values():
                        if not p is player:
                                diff = player.r - p.r
                                if diff > 0.1 * p.r and self.collide(p.x, p.y, 0, player.x, player.y, diff):
                                        print('(', player.name, 'съел', p.name)
                                        player.score += p.score + 10
                                        p.score = 10
                                        p.update_pos(*self.pick_location())
                                        return True
                return False


        def cool_location(self):
                return self.width * self.scale - randint(100, 200), self.height * self.scale - randint(100, 200)


        def handle_client(self, conn):
                name = self.receive(conn)
                print(f'Клиент \"{name}\" подключился')
                id = self.client_id

                self.send(conn, self.client_id)
                self.client_id += 1

                x, y = self.width // 2 * self.scale, self.height // 2 * self.scale
                color = self.pick_color()
                player = Player(x, y, color, self.player_radius, name, 10)
                self.players[id] = player

                while True:
                        if not (data := self.receive(conn)):
                                break
                        # обновление позиции игрока
                        player.update_pos(data[0], data[1])
                        # проверка съеден ли шар
                        self.eat_orbs(player)
                        # проверка умер ли игрок
                        died = self.check_collisions(player)
                        self.send_gameinfo(conn, died, player.score)

                conn.close()
                print(f'Клиент \"{name}\" отключился!')
                del self.players[id]


        def send_gameinfo(self, conn, died, score):
                self.send(conn, (self.orbs, self.players, died, score))


server = Server()
server.start()
