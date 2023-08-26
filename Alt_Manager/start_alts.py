import sys
import time

import bot_interface
import alt_client
from threading import Thread
def main():
    local = True
    if local:
        print('Alert: Running in local mode cannot join a server please change if undesired')
    fake_client = True
    account_info = 'Account_Info.txt'
    if fake_client:
        account_info = 'Example_Account_Info.txt'
    info = [True]
    allowed_fails = 10  # -1 means infinite restarts (Not recommended)
    processes = []
    try:
        with open(account_info) as fi:
            for line in fi:
                if line[0] != '#' and line != '\n':
                    print('Starting')
                    user, pwd = line.strip('\n').split(' ')
                    inputs = (user, pwd, info, local, fake_client)
                    process = Thread(target=manage_individual_client, args=inputs)
                    process.start()
                    processes.append([process, inputs, allowed_fails])
                    time.sleep(.5)
                    break

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
