# import sys
# import time
#
# import Message
#
#
# class Client:
#
#     def __init__(self, name, address):
#         self.name = name
#         self.address = address
#
#     def Sendto(self, contents, dest):
#         message = Message.Message(self.address, contents, dest, time.localtime())
import select
from time import sleep
from socket import *


# def sendmsgto():
#
def getmsg(sock):
    response = sock.recv(1024)
    if not response:
        print("ERROR")
        return
    # print(response)
    return response


sock = socket(AF_INET, SOCK_STREAM)
sock.connect(('127.0.0.1', 55000))
uname = input("Your Username: ")
socket_list = [sock]
connected = False
print(
    "Here are the codewords for certain actions:\n'<all>': send message to everyone\n'<server>': perform action related directly to the server (Disconnect, get user list, etc)\n<username>': send private message")

while True:
    # sleep(0.5)

    if not connected:
        sock.send(bytes(uname, encoding='utf8'))
        connected = True
    else:
        action = input("Please select action: ")
        if action == "<server>":
            print("Server actions")
        else:
            msg = input("Type message: ")
            sock.send(bytes(action + ": " + msg, encoding='utf8'))
    read_list, _, _ = select.select(socket_list, [], [], 5)
    for curr_sock in read_list:
        response = getmsg(curr_sock)
        print(bytes.decode(response, encoding='utf8'))
# sock.close()
