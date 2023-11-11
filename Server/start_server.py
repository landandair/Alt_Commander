from Server import main
from Server_Client_Data import ServerData


if __name__ == '__main__':
    corner_pos = (50, 50)  # Top left corner(assume square)
    ignored_color = (51, 54, 56)
    file_name = 'Templates/HillofSwords2023.png' # Name of file to be used as reference
    try:
        main(ServerData(file_name, corner_pos, ignored_color=ignored_color))
    except KeyboardInterrupt:
        print('Closing Server...')
