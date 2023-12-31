import sys
import time
import os
from PIL import Image
import bot_interface
import alt_client
from threading import Thread
import configparser

def main():
    config = configparser.ConfigParser()
    config.read('Alt_config.ini')
    local = config.getboolean('Settings', 'local')
    if local:
        print('Alert: Running in local mode cannot join a server please change if undesired')
    fake_client = config.getboolean('Settings', 'fake_client')
    account_info = config.get('Settings', 'account_info')
    if fake_client:
        image = Image.open(os.getcwd() + '/screenshots/game_board.png')
    info = [True]
    allowed_fails = config.getint('Settings', 'allowed_fails')
    processes = []
    try:
        with open(account_info) as fi:
            for line in fi:
                if line[0] != '#' and line != '\n':
                    print('Starting')
                    user, pwd = line.strip('\n').split(' ')
                    if fake_client:
                        pwd = image
                    inputs = (user, pwd, info, local, fake_client)
                    process = Thread(target=manage_individual_client, args=inputs)
                    process.start()
                    processes.append([process, inputs, allowed_fails])
                    time.sleep(.5)

        while True:
            time.sleep(1)
            for i, process_list in enumerate(processes):
                process, inputs, health = process_list
                if not process.is_alive() and health != 0:
                    time.sleep(5)
                    health -= 1
                    print(f'Restarting {inputs[0]}: {health} restarts remaining')
                    process = Thread(target=manage_individual_client, args=inputs)
                    process.start()
                    processes[i] = [process, inputs, health]
                elif not process.is_alive() and health == 0:
                    info[0] = False
                    sys.exit(f'{inputs[0]} Ran out of restarts, something wend wrong')

    except KeyboardInterrupt:
        info[0] = False
        print('Closed by user')


def manage_individual_client(username, password, info, local=False, fake_client=False):
    net_client = alt_client.Network(local)
    if fake_client:
        bot_obj = bot_interface.FakeSwarmPlaceBot
    else:
        bot_obj = bot_interface.SwarmPlaceBot
    alt_interface = bot_obj(username, password, net_client)
    while info[0]:
        try:
            time.sleep(3)  # Waiting till client is ready for next move
            alt_interface.update()
            if alt_interface.client_dat['reboot']:
                print('Server-Triggered Reboot')
                sys.exit()
        except BrokenPipeError:
            print(f'{username} Lost Connection to Server')
            break
        except KeyboardInterrupt:
            sys.exit(f'{username} interrupted by user')
    # bot_interface.SwarmPlaceBot(username, password)


if __name__ == '__main__':
    main()
