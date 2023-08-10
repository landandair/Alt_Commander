import socket
import sys
import time
from threading import Thread
from command_client import start_cmd_client
import pygame_gui
import cmd_client_data


def main():
    local = True
    cmd_data = cmd_client_data.CmdData(local_mode=local)
    try:
        # Start connection to server on other thread
        arg = [cmd_data]
        server_connection_thread = Thread(target=start_cmd_client, args=arg)
        server_connection_thread.start()
        # Start up gui
        window = pygame_gui.Window(cmd_data)
        for x in range(10):
            if cmd_data.booted:
                break
            time.sleep(1)
        while cmd_data.running:
            window.update()
    except KeyboardInterrupt:
        cmd_data.running = False
        sys.exit('User interrupted')
    except socket.error as e:
        cmd_data.running = False
        sys.exit(e)


if __name__ == '__main__':
    main()
