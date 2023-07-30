import time
import socket
import pickle
import sys
from cryptography.fernet import Fernet


class Network:
    def __init__(self, local_mode=False):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            with open('../Server_data.txt') as fi:
                lines = fi.readlines()
                fields = []
        except FileNotFoundError:
            sys.exit('Server_data.txt not found please use script to make file following example')
        for line in lines:
            fields.append(line.strip('\n').split(':')[1])

        ip, port, key = fields
        self.fernet = Fernet(key)
        if local_mode:
            self.addr = (socket.gethostname(), int(port))  # Change to IP
        else:
            self.addr = (ip, int(port))  # Change to IP
        self.start = self.connect()

    def connect(self):
        try:
            print(f'Trying to connect to {self.addr}')
            self.client.connect(self.addr)
            data = pickle.loads(self.fernet.decrypt(self.client.recv(5 * 2048)))
            return data
        except socket.error as e:
            print(e)
            sys.exit('Could not connect to server')

    def send(self, data):
        try:
            self.client.send(self.fernet.encrypt(pickle.dumps(data, protocol=-1)))
            data = self.client.recv(2048)
            return pickle.loads(self.fernet.decrypt(data))
        except socket.error as e:
            print(e)


if __name__ == '__main__':
    # debug code which sends working data and was used to develop com protocol
    network = Network(local_mode=True)
    while True:
        time.sleep(1)
        data = {'pos': (0, 0),
                'target': (0, 1),
                'bad_blocks': [],
                'pix_ready': False,
                'reboot': False}
        print(network.send(data))
