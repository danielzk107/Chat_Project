import select
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
    print(
        "Here are the codewords for certain actions:\n'<all>': send message to everyone\n'<server>': perform action related directly to the server (Connect, Disconnect, get user list, etc)\n<username>': send private message")
    client = Client.Client()
    inputthread = threading.Thread(target=client.deal_with_input)
    inputthread.start()
    recvthread = threading.Thread(target=client.recv_loop)
    recvthread.start()
    for line in sys.stdin:
        client.inputq.put(line)


