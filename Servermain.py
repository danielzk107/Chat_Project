from os import listdir
from os.path import isfile, join

import Server


if __name__ == '__main__':
    server = Server.Server()
    server.run()

