import sys
import socket
import select
from _thread import *


class Server:

    def __init__(self):
        self.clientlist = []
        self.unamelist = {}
        self.msgs_list = []
        self.server_socket = socket.socket()
        self.server_socket.bind(('127.0.0.1', 55000))
        self.server_socket.listen(15)

    def run(self):
        while True:
            read_list, write_list, err_list = select.select([self.server_socket] + self.clientlist, [], [])
            for curr_sock in read_list:
                if curr_sock is self.server_socket:
                    (new_sock, address) = self.server_socket.accept()
                    self.clientlist.append(new_sock)
                else:
                    # curr_sock.send(bytes("Please enter Username", encoding='utf8'))
                    data = curr_sock.recv(1024)
                    data = bytes.decode(data, encoding='utf8')
                    if data == "":
                        self.clientlist.remove(curr_sock)  #Connection to client stopped
                    else:
                        if curr_sock not in self.unamelist:
                            name_taken = False
                            for sock in self.unamelist:
                                if self.unamelist[sock] == data.strip():
                                    name_taken = True
                            if name_taken:
                                curr_sock.send(bytes("Server: Sorry, that username is already taken", encoding='utf8'))
                            else:
                                self.unamelist[curr_sock] = data.strip()
                                curr_sock.send(bytes("Server: Welcome, " + str(self.unamelist[curr_sock]) + "!", encoding='utf8'))
                                print("Connected " + str(self.unamelist[curr_sock]))
                        else:
                            try:
                                (action, msg) = data.split(">")
                                if data[0] != "<" or action == "<all":
                                    self.msgs_list.append((curr_sock, msg, "all"))
                                elif action == "<server":
                                    self.msgs_list.append((curr_sock, msg, "server"))
                                else:
                                    sendto = None
                                    uname = action.split("<")[1]
                                    for sock in self.unamelist:
                                        if uname == self.unamelist[sock]:
                                            sendto = sock
                                    if sendto is None:
                                        curr_sock.send(bytes("Please choose a valid action/Username", encoding='utf8'))
                                    else:
                                        self.msgs_list.append((curr_sock, msg, sendto))
                            except ValueError:
                                curr_sock.send(bytes("server: You cannot send an empty message. Please try again.", encoding='utf8'))
            for msg in self.msgs_list:
                (curr_client, data, sendto) = msg
                if sendto == "all":
                    for sock in self.clientlist:
                        if sock != curr_client:
                            newdata = self.unamelist[curr_client] + " to All: " + data
                            sock.send(bytes(newdata, encoding='utf8'))
                            print("Sent response")
                if sendto == "server":
                    if data.strip() == "disconnect" or data.strip() == "Disconnect":
                        curr_client.send(bytes("server: Goodbye", encoding='utf8'))
                        curr_client.close()
                        print("Disconnected " + self.unamelist[curr_client])
                        self.clientlist.remove(curr_client)
                        self.unamelist.pop(curr_client)
                    if data.strip() == "clist" or data.strip() == "Clist":
                        usernames = list()
                        for sock in self.unamelist:
                            usernames.append(self.unamelist[sock])
                        curr_client.send(bytes("Active clients: " + str(usernames), encoding='utf8'))
                elif sendto is not None:  #Could be simply else, but is elif just in case of an unexpected issue
                    try:
                        sendto.send(bytes(self.unamelist[curr_client] + ": " + data, encoding='utf8'))
                        print(self.unamelist[curr_client] + " to " + self.unamelist[sendto] + ": " + data.strip())
                    except Exception:
                        curr_client.send(bytes("ERROR", encoding='utf8'))
                        print("Unknown error occurred")
                self.msgs_list.remove(msg)

