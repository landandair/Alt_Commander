import sys
import time

import bot_interface
import alt_client
import _thread as thread

def main():
    local = True
    with open('Account_Info.txt') as fi:
        line = fi.readline()
        while line:
            if line[0] != '#':
                user, pwd = line.split(' ')
                thread.start_new_thread(manage_individual_client, (user, pwd, local))
                time.sleep(.1)
            line = fi.readline()
    while True:
        time.sleep(100)





def manage_individual_client(username, password, local=False):
    net_client = alt_client.Network(local)
    while True:
        try:
            net_client.send({'pos': (0, 0), 'target': (0, 1), 'bad_blocks': [], 'pix_ready': False, 'reboot': False})
        except BrokenPipeError:
            print('Lost Connection to Server')
            break
        except KeyboardInterrupt:
            sys.exit('Client interrupted by user')
    # bot_interface.SwarmPlaceBot(username, password)


if __name__ == '__main__':
    main()
