import sys
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
        while True:
            window.update()
    except KeyboardInterrupt:
        cmd_data.running = False
        sys.exit('User interrupted')


if __name__ == '__main__':
    main()