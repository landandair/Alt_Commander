from Server import main
from Server_Client_Data import ServerData
import configparser

if __name__ == '__main__':
    config = configparser.ConfigParser()
    config.read('server_config.ini')
    corner_pos = (config.getint('Image', 'corner_x'), config.getint('Image', 'corner_y'))
    ignored_color = (config.getint('Image', 'ignored_color_R'),
                     config.getint('Image', 'ignored_color_G'),
                     config.getint('Image', 'ignored_color_B'))
    file_name = config.get('Image', 'file_name')  # Name of file to be used as reference
    try:
        main(ServerData(file_name, corner_pos, ignored_color=ignored_color))
    except KeyboardInterrupt:
        print('Closing Server...')
