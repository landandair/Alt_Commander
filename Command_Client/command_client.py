import time
import socket
import pickle
import sys
from cryptography.fernet import Fernet, InvalidToken


class CmdNetwork:
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
        print(f'Image being received with a top left corner of: {self.corner_pos}')
        num_packets = data['pkt_num']
        with open('template_img.png', 'wb') as fi:
            for _ in range(num_packets):
                self.client.send(self.fernet.encrypt(b'2'))
                data = self.client.recv(2048)
                fi.write(self.fernet.decrypt(data))

    def connect(self):
        try:
            print(f'Trying to connect to {self.addr}')
            self.client.connect(self.addr)
            data = pickle.loads(self.fernet.decrypt(self.client.recv(2048)))
            return data
        except socket.error as e:
            print(e)
            raise e

    def send(self, data):
        try:
            self.client.send(self.fernet.encrypt(pickle.dumps(data, protocol=-1)))
            data = self.client.recv(1048576)
            return pickle.loads(self.fernet.decrypt(data))
        except socket.error as e:
            print(e)
        except InvalidToken:
            print('Partial or incomplete data received')
            return


def start_cmd_client(cmd_client_data):
    try:
        connection = CmdNetwork(local_mode=cmd_client_data.local)
        cmd_client_data.booted = True
        cmd_client_data.corner_pos = connection.corner_pos
        while cmd_client_data.running:
            time.sleep(.5)
            data = {'goto_range': (),
                    'shuffle': False,
                    'moves': {},
                    'reboot': False}
            if cmd_client_data.goto_range:
                data['goto_range'] = cmd_client_data.goto_range
                cmd_client_data.goto_range = ()
            if cmd_client_data.shuffle:
                data['shuffle'] = cmd_client_data.shuffle
                cmd_client_data.shuffle = False
            if cmd_client_data.moves:
                data['moves'] = cmd_client_data.moves
                cmd_client_data.moves = {}
            if cmd_client_data.reboot:
                data['reboot'] = cmd_client_data.reboot
                cmd_client_data.reboot = False
            returned = connection.send(data)
            if returned:
                cmd_client_data.bot_positions = returned['bot_pos']
                cmd_client_data.new_blocks = returned['new_bad_blocks']
                cmd_client_data.remove_blocks = returned['removed_bad_blocks']
            else:
                raise socket.error
    except socket.error as e:
        print(e)
        cmd_client_data.running = False
        sys.exit(e)


if __name__ == '__main__':
    # debug code which sends working data and was used to develop com protocol
    network = CmdNetwork(local_mode=True)
    while True:
        time.sleep(1)
        data = {'goto_range': (),
                'shuffle': False,
                'moves': {},
                'reboot': False}
        print(network.send(data))