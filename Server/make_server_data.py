from cryptography.fernet import Fernet
from requests import get

def main():
    ip = input('Enter a valid public ip or proxy(or hit enter for default): ')
    if not ip:
        ip = get('https://api.ipify.org').content.decode('utf8')
    lines = ['server_ip:'+ip]
    port = input('enter desired port number or hit enter for default:')
    if not port:
        port = 7135
    lines.append('port:' + str(port))
    key = Fernet.generate_key()
    lines.append('key:'+key.decode('utf-8'))
    with open('../Server_data.txt', 'w') as fi:
        for line in lines:
            fi.write(line + '\n')


if __name__ == '__main__':
    main()
