import builtins
import select
import socket
import sys
import threading
from socket import *
from time import sleep

#
# def getmsg(sock):
#     response = sock.recv(1024)
#     if not response:
#         print("ERROR")
#         return
#     return response
#
#
# sock = socket(AF_INET, SOCK_STREAM)
# sock.connect(('127.0.0.1', 55000))
# msg = 'Robert'
# socket_list = [sock]
# connected = False
# while True:
#     if not connected:
#         sock.send(bytes(msg, encoding='utf8'))
#         connected = True
#     else:
#         sock.send(bytes("<daniel>" + msg, encoding='utf8'))
#         sleep(5)
#     # sock.send(bytes(msg, encoding='utf8'))
#     read_list, _, _ = select.select(socket_list, [], [], 5)
#     for curr_sock in read_list:
#         response = getmsg(curr_sock)
#         print(bytes.decode(response, encoding='utf8'))
import Client

if __name__ == '__main__':
    # print(
    #     "Here are the codewords for certain actions:\n'<all>': send message to everyone\n'<server>': perform action related directly to the server (Connect, Disconnect, get user list, etc)\n<username>': send private message")
    # client = Client.Client()
    # inputthread = threading.Thread(target=client.deal_with_input)
    # inputthread.start()
    # recvthread = threading.Thread(target=client.recv_loop)
    # recvthread.start()
    # for line in sys.stdin:
    #     client.inputq.put(line)


    # sock = socket(AF_INET, SOCK_DGRAM)
    # sock.connect(('127.0.0.1', 5005))
    # while True:
    #     read_list, _, _ = select.select([sock], [], [], 3)
    #     for curr_sock in read_list:
    #         filename = curr_sock.recv(1024)
    #         file = builtins.open(filename.strip(), 'w')
    #         data = curr_sock.recv(1024)
    #         while data:
    #             print(data)
    #             file.write(str(bytes(data, encoding='utf8')))
    #             data = curr_sock.recv(1024)
    #         sock.close()
    #         exit()

    UDP_IP = "127.0.0.1"
    IN_PORT = 5005
    timeout = 3

    sock = socket(AF_INET, SOCK_DGRAM)
    sock.bind((UDP_IP, IN_PORT))

    while True:
        data, addr = sock.recvfrom(1024)
        if data:
            print("File name:", data)
            file_name = data.strip()
            sock.sendto(bytes("Response", encoding='utf8'), addr)
            f = open(file_name, 'wb')

        while True:
            ready = select.select([sock], [], [], timeout)
            if ready[0]:
                data, addr = sock.recvfrom(1024)
                if data:
                    f.write(data)
                    sock.sendto(bytes("Response", encoding='utf8'), addr)
            else:
                print("%s Finish!" % file_name)
                f.close()
                break
