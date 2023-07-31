from Server import main
from Server_Client_Data import ServerData


if __name__ == '__main__':
    corner_pos = (100, 100)
    file_name = 'Templates/template.png'
    try:
        main(ServerData(file_name, corner_pos))
    except KeyboardInterrupt:
        print('Closing Server...')
