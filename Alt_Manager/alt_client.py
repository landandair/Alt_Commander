import time
import socket
import pickle
import sys

import cryptography.fernet
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

        # Get reference image from server
        data = self.connect()
        self.corner_pos = data['corner']
        self.ignore = data['ignore']
        print(f'Image being received with a top left corner of: {self.corner_pos}')
        num_packets = data['pkt_num']
        with open('template_img.png', 'wb') as fi:
            for _ in range(num_packets):
                self.client.send(self.fernet.encrypt(b'1'))
                data = self.client.recv(2048)
                fi.write(self.fernet.decrypt(data))

    def connect(self):
        try:
            print(f'Trying to connect to {self.addr}')
            self.client.connect(self.addr)
            data = pickle.loads(self.fernet.decrypt(self.client.recv(2048)))
            print('Success')
            return data
        except socket.error as e:
            print(e)
            sys.exit('Could not connect to server')

    def send(self, data):
        try:
            self.client.send(self.fernet.encrypt(pickle.dumps(data, protocol=-1)))
            data = self.client.recv(2048)
            if data:
                return pickle.loads(self.fernet.decrypt(data))
            else:
                print('Lost Connection to server')
                sys.exit()
        except socket.error as e:
            print(e)
        except cryptography.fernet.InvalidToken:
            sys.exit('Invalid key from server (Server Closed)')


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
