import builtins
import select
import socket
import sys
from time import sleep

if __name__ == '__main__':
    # serv_sock = socket.socket()
    # serv_sock.bind(('127.0.0.1', 5005))
    # serv_sock.listen(15)
    # while True:
    #     file = builtins.open(".\\Files\\file1.txt", 'r')
    #     read_list, _, _ = select.select([serv_sock], [], [], 2)
    #     for curr_sock in read_list:
    #         curr_sock.send(bytes("file1.txt", encoding='utf8'))
    #         data = file.read(1024)
    #         while data:
    #             print(data)
    #             curr_sock.send(bytes("file1.txt", encoding='utf8'))
    #             data = file.read(1024)
    #         serv_sock.close()
    #         exit()

    UDP_IP = "127.0.0.1"
    UDP_PORT = 5005
    buf = 1024
    file_name = "file1.txt"

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    while True:
        ready = select.select([sock], [], [], 3)
        for curr_sock in ready:
            try:
                sock.sendto(bytes("file1.txt", encoding='utf8'), (UDP_IP, UDP_PORT))
                print("Sending %s ..." % file_name)
                f = open(".\\Files\\file1.txt", "r")
                data = f.read(buf)
                res, addr = sock.recvfrom(1024)
                while data:
                    if res:
                        if sock.sendto(bytes(data, encoding='utf8'), addr):
                            data = f.read(buf)
                            # print(res)
                    else:
                        sock.sendto(bytes(data, encoding='utf8'), addr)
                    sleep(0.02)
                    res, addr = sock.recvfrom(1024)
                sock.close()
                f.close()
            except OSError:
                print("Finished sending file.")
                breakcon = True
                exit()