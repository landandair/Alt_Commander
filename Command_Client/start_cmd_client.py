import socket
import sys
import time
from threading import Thread
import configparser
import pygame

from command_client import start_cmd_client
import pygame_gui
import pygame as pg
import cmd_client_data


def main():
    config = configparser.ConfigParser()
    config.read('cmd_config.ini')
    local = config.getboolean('Settings', 'local')
    show_bad = config.getboolean('Settings', 'display_bad')
    cmd_data = cmd_client_data.CmdData(local_mode=local)
    cmd_data.show_bad = show_bad
    try:
        # Start connection to server on other thread
        arg = [cmd_data]
        server_connection_thread = Thread(target=start_cmd_client, args=arg)
        server_connection_thread.start()
        while not cmd_data.booted and cmd_data.running:
            time.sleep(.5)
        time.sleep(1)
        # Start up gui
        if cmd_data.running:
            window = pygame_gui.Window(cmd_data)
            while cmd_data.running:
                window.update()
        pg.quit()
        sys.exit('No connection to server')
    except KeyboardInterrupt:
        cmd_data.running = False
        pg.quit()
        sys.exit('User interrupted')
    except socket.error as e:
        cmd_data.running = False
        pg.quit()
        sys.exit(e)
    except pygame.error as e:
        cmd_data.running = False
        pg.quit()
        sys.exit(e)


if __name__ == '__main__':
    main()
