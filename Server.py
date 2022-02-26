import sys
import socket
import select
from _thread import *

clientlist = []
unamelist = {}
msgs_list = []
server_socket = socket.socket()
server_socket.bind(('127.0.0.1', 55000))
server_socket.listen(15)
while True:
    read_list, write_list, err_list = select.select([server_socket] + clientlist, [], [])
    for curr_sock in read_list:
        if curr_sock is server_socket:
            (new_sock, address) = server_socket.accept()
            clientlist.append(new_sock)
        else:
            # curr_sock.send(bytes("Please enter Username", encoding='utf8'))
            data = curr_sock.recv(1024)
            if data == b'':
                clientlist.remove(curr_sock)  #Connection to client stopped
            else:
                if curr_sock not in unamelist:
                    unamelist[curr_sock] = bytes.decode(data, encoding='utf8')
                    curr_sock.send(bytes("Server: Welcome, " + str(unamelist[curr_sock]) + "!", encoding='utf8'))
                else:
                    msgs_list.append((curr_sock, data))
    for msg in msgs_list:
        (curr_client, data) = msg
        print(unamelist[curr_client] + ": " + bytes.decode(data, encoding='utf8'))
        for sock in clientlist:
            if sock != curr_client:
                newdata = unamelist[curr_client] + " to All: " + bytes.decode(data, encoding='utf8')
                sock.send(bytes(newdata, encoding='utf8'))
                print("Sent response")
            # else:
            #     print(str(sock) + " is equal to " + str(curr_client))
        msgs_list.remove(msg)

