import pickle
import socket
import _thread as thread
import time
from Server_Client_Data import ServerData
import sys
from cryptography.fernet import Fernet, InvalidToken

def main(server_data):
    try:
        with open('../Server_data.txt') as fi:
            lines = fi.readlines()
        fields = []
    except FileNotFoundError:
        sys.exit('Server_data.txt not found please use script to make file following example')

    for line in lines:
        fields.append(line.strip('\n').split(':')[1])
    try:
        ip, port, key = fields
        fernet = Fernet(key)
        print(f'starting server on: "{ip}" port: {port}')

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:  # bind the socket object to the ip and port
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind(('', int(port)))
        except socket.error as e:
            sys.exit(e)
        s.listen(2)

        print("Waiting for a connection, Server Started")
        # Used to assign ship ids to clients
        while True:  # Main connection loop which listens and creates threads that handle communications with clients
            conn, addr = s.accept()
            print("Connected to:", addr)
            print(f'{len(server_data.bot_positions)+1} bots connected')
            # Start thread to manage player
            thread.start_new_thread(threaded_client, (conn, conn.getpeername(), fernet, server_data))
    except socket.error as e:
        s.close()
        print(e)
    except KeyboardInterrupt:
        print('Closed by user')
        s.close()



def threaded_client(conn, peer_name, fernet: Fernet, server_data: ServerData):
    try:
        # Initial behavior send starting position
        img_packets = []
        with open(server_data.file_name, 'rb') as fi:
            buffer = fi.read(256)
            while buffer:
                img_packets.append(buffer)
                buffer = fi.read(256)
        initial = {'pkt_num': len(img_packets), 'corner': server_data.corner_pos}  # Send number of img packets
        encoded = fernet.encrypt(pickle.dumps(initial, protocol=-1))  # Package data
        conn.send(encoded)  # Send initial packet
        img_sent = True
        try:
            for buffer in img_packets:
                check = fernet.decrypt(conn.recv(2048))
                if int(check):
                    encoded = fernet.encrypt(buffer)
                    conn.send(encoded)
                else:
                    img_sent = False
                    print(f'{peer_name}: Image Sending Failed')
                    break
        except InvalidToken:
            print(f'{peer_name} has wrong key')
            raise KeyboardInterrupt

        # Image Finished sending
        # Process alt_clients
        if int(check) == 1:
            handle_alt_client(conn, fernet, peer_name, server_data, img_sent)
        else:
            handle_cmd_client(conn, fernet, peer_name, server_data, img_sent)
    except KeyboardInterrupt:
        pass
    except socket.error as e:
        print(e)
        pass

    time.sleep(1)
    print(f"Lost connection to:{peer_name}")
    print(f'{len(server_data.bot_positions)} bots remaining')
    conn.close()

def handle_alt_client(conn, fernet, peer_name, server_data, img_sent):
    given_priority_target = False
    low_priority_target = server_data.get_oldest_update()
    server_data.bot_targets[peer_name] = ()
    while img_sent:
        try:
            data = conn.recv(2048)
            if not data:
                if peer_name in server_data.bot_positions:
                    server_data.bot_positions.pop(peer_name)
                break
            data = pickle.loads(fernet.decrypt(data))
            # Use data to update server data and send essential updates back to client
            server_data.bot_positions[peer_name] = data['pos']
            # Takes in a movement command from the server or a reset command
            if server_data.bot_targets[peer_name] and not given_priority_target:
                if server_data.bot_targets[peer_name] == 'r':
                    data['reboot'] = True
                else:  # Means it's a coordinate
                    low_priority_target = server_data.bot_targets[peer_name]
                    server_data.bot_targets[peer_name] = ()

            if data['pos'] == data['target']:  # Target has been reached need new target
                if given_priority_target:
                    given_priority_target = False
                else:
                    # print(f'{peer_name}: {low_priority_target}')  # REMOVE
                    low_priority_target = server_data.get_oldest_update()
            # Logic to assign a priority target (bad pixel) when a bot is ready
            if data['pix_ready'] and not given_priority_target:
                data['target'] = server_data.nearest_bad_block(peer_name)
                given_priority_target = True
                if not data['target']:
                    data['target'] = low_priority_target  # This will make send the bot aimlessly waiting for
                    given_priority_target = False
            elif not given_priority_target:
                data['target'] = low_priority_target  # This will make send the bot aimlessly searching
                given_priority_target = False

            # Look through bad blocks
            if data['bad_blocks']:
                for block in data['bad_blocks']:
                    if block in server_data.update_blocks and block not in server_data.bad_blocks:
                        server_data.bad_blocks.append(block)
            data['bad_blocks'] = []

            encoded = fernet.encrypt(pickle.dumps(data, protocol=-1))
            conn.send(encoded)
        except socket.error as e:
            print(e)
            break


def handle_cmd_client(conn, fernet, peer_name, server_data, img_sent):
    while img_sent:
        try:
            data = conn.recv(5*2048)
            if not data:
                if peer_name in server_data.bot_positions:
                    server_data.bot_positions.pop(peer_name)
                break
            data = pickle.loads(fernet.decrypt(data))
            # Handling
            if data['goto_range']:
                server_data.prioritize_area(data['goto_range'])
            if data['shuffle']:
                server_data.shuffle()
            if data['reboot']:
                server_data.reboot_all()
            if data['moves']:
                for bot in data['moves']:
                    move = data['moves'][bot]
                    server_data.bot_targets[bot] = move

            returning_data = {'bot_pos': server_data.bot_positions,
                              'bad_blocks': server_data.bad_blocks}

            encoded = fernet.encrypt(pickle.dumps(returning_data, protocol=-1))
            print(len(encoded))
            conn.send(encoded)
        except socket.error as e:
            print(e)
            break

