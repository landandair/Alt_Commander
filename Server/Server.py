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
    given_priority_target = False
    low_priority_target = server_data.get_oldest_update()
    # Initial behavior send starting position
    initial = {'pos': (server_data.get_oldest_update())}  # Send starting position
    encoded = fernet.encrypt(pickle.dumps(initial, protocol=-1))  # Package data
    conn.send(encoded)  # Send initial packet


    while True:
        try:
            data = conn.recv(2048)
            if not data:
                print(f"Player {peer_name} Disconnected")
                server_data.bot_positions.pop(peer_name)
                break
            data = pickle.loads(fernet.decrypt(data))
            # Use data to update server data and send essential updates back to client
            server_data.bot_positions[peer_name] = data['pos']
            if data['pos'] == low_priority_target:  # Target has been reached need new target
                low_priority_target = server_data.get_oldest_update()

            # Logic to assign a priority target (bad pixel) when a bot is ready
            if data['pix_ready'] and not given_priority_target:
                data['target'] = server_data.nearest_bad_block(peer_name)
                given_priority_target = True
                if not data['target']:
                    data['target'] = low_priority_target  # This will make send the bot aimlessly waiting for
                    given_priority_target = False
            else:
                data['target'] = low_priority_target  # This will make send the bot aimlessly searching
                given_priority_target = False

            # Look through bad blocks


            encoded = fernet.encrypt(pickle.dumps(data, protocol=-1))
            conn.send(encoded)
            # print("Sent : ", data, player)
        except socket.error as e:
            print(e)
            break
    time.sleep(5)
    print(f"Lost connection to:{peer_name}")
    conn.close()


