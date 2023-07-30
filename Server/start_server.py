from Server import main
from Decicion_Maker import ServerData


if __name__ == '__main__':
    corner_pos = (100, 100)
    file_name = 'Templates/template.png'
    main(ServerData(file_name, corner_pos))
