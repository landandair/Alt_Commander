import pickle
import socket
import _thread as thread
import time
from Server_Client_Data import ServerData
import sys
from cryptography.fernet import Fernet

def main(server_data):
    try:
        with open('../Server_data.txt') as fi:
            lines = fi.readlines()
        fields = []
    except FileNotFoundError:
        sys.exit('Server_data.txt not found please use script to make file following example')

    for line in lines:
        fields.append(line.strip('\n').split(':')[1])

    ip, port, key = fields
    fernet = Fernet(key)
    print(f'starting server on: "{ip}" port: {port}')

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:  # bind the socket object to the ip and port
        s.bind(('', int(port)))
    except socket.error as e:
        sys.exit(e)
    s.listen(2)

    print("Waiting for a connection, Server Started")
    # Used to assign ship ids to clients
    while True:  # Main connection loop which listens and creates threads that handle communications with clients
        conn, addr = s.accept()
        print("Connected to:", addr)
        # Start thread to manage player
        thread.start_new_thread(threaded_client, (conn, conn.getpeername(), fernet, server_data))


def threaded_client(conn, peer_name, fernet: Fernet, server_data: ServerData):
    try:
        given_priority_target = False
        low_priority_target = server_data.get_oldest_update()
        # Initial behavior send starting position
        img_packets = []
        with open(server_data.file_name, 'rb') as fi:
            buffer = fi.read(1024)
            while buffer:
                img_packets.append(buffer)
                buffer = fi.read(1024)
        initial = {'pkt_num': len(img_packets), 'corner': server_data.corner_pos}  # Send number of img packets
        encoded = fernet.encrypt(pickle.dumps(initial, protocol=-1))  # Package data
        conn.send(encoded)  # Send initial packet
        img_sent = True
        for buffer in img_packets:
            check = fernet.decrypt(conn.recv(2048))
            if int(check):
                encoded = fernet.encrypt(buffer)
                conn.send(encoded)
            else:
                img_sent = False
                print(f'{peer_name}: Image Sending Failed')
                break
        # Image Finished sending

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
                if data['pos'] == data['target']:  # Target has been reached need new target
                    if given_priority_target:
                        given_priority_target = False
                    else:
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


                encoded = fernet.encrypt(pickle.dumps(data, protocol=-1))
                conn.send(encoded)
                # print("Sent : ", data, player)
            except socket.error as e:
                print(e)
                break
    except KeyboardInterrupt:
        pass

    time.sleep(1)
    print(f"Lost connection to:{peer_name}")
    conn.close()


