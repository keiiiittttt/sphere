import socket
import _pickle as pickle


class Network:
    BUFFER = 16 * 2048

    def __init__(self):
        self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.port = 5555
        # self.host = ''
        self.host = socket.gethostbyname(socket.gethostname())

    def connect(self, name):
        self.conn.connect((self.host, self.port))
        print('Соединение с сервером!')
        self.id = self.send(name)

    def disconnect(self):
        self.conn.close()

    def send(self, data):
        self.conn.send(pickle.dumps(data))
        return pickle.loads(self.conn.recv(Network.BUFFER))

    def receive(self, count):
        return pickle.loads(self.conn.recv(count))