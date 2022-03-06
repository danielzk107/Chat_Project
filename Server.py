import builtins
import datetime
import socket
import select
import threading
from os import *
from os.path import *
from time import sleep


class Server:

    def __init__(self):
        self.clientlist = []
        self.unamelist = {}
        self.num_of_udpsockets_open = 0
        self.num_of_tcpsockets_open = 0
        # self.downloads_per_client = {}
        self.file_port = 0
        # self.alltimeunamelist = {}
        self.msgs_list = []
        self.server_socket = socket.socket()
        self.server_socket.bind(('127.0.0.1', 55000))
        if self.server_socket:
            print("Server running")
        self.server_socket.listen(15)

    def run(self):
        while True:
            read_list, _, _ = select.select([self.server_socket] + self.clientlist, [], [])
            for curr_sock in read_list:
                if curr_sock is self.server_socket:
                    (new_sock, address) = self.server_socket.accept()
                    self.clientlist.append(new_sock)
                else:
                    try:
                        data = curr_sock.recv(1024)
                        data = bytes.decode(data, encoding='utf8')
                        if data == "":
                            self.clientlist.remove(curr_sock)  #Connection to client stopped
                        else:
                            if curr_sock not in self.unamelist:
                                if data[0] == "<":
                                    curr_sock.send(bytes("Server: That username is invalid", encoding='utf8'))
                                else:
                                    name_taken = False
                                    for sock in self.unamelist:
                                        if self.unamelist[sock] == data.strip():
                                            name_taken = True
                                    if name_taken:
                                        curr_sock.send(bytes("Server: Sorry, that username is already taken", encoding='utf8'))
                                    else:
                                        self.unamelist[curr_sock] = data.strip()
                                        # self.alltimeunamelist[curr_sock] = data.strip()
                                        curr_sock.send(bytes("Server: Welcome, " + str(self.unamelist[curr_sock]) + "!", encoding='utf8'))
                                        print("Connected " + str(self.unamelist[curr_sock]))
                                        # self.downloads_per_client[curr_sock] = 0
                            else:
                                try:
                                    if data[:4] == "port":
                                        self.file_port = int(data[4:])
                                    else:
                                        action = data.split(">")[0]
                                        msg = data.split(">")[1]
                                        if data[0] != "<" or action == "<all":
                                            self.msgs_list.append((curr_sock, msg, "all"))
                                        elif action == "<server":
                                            self.msgs_list.append((curr_sock, msg, "server"))
                                        elif action == "<download":
                                            self.msgs_list.append((curr_sock, msg, "download"))
                                        elif action == "<send":
                                            uname = msg[1:]
                                            filename = (data.split(">")[2]).strip()
                                            other_sock = None
                                            for sock in self.unamelist:
                                                if uname == self.unamelist[sock]:
                                                    other_sock = sock
                                            if other_sock is None:
                                                curr_sock.send(bytes("Server: Username not available", encoding='utf8'))
                                            else:
                                                send_thread = threading.Thread(target=self.send_file, args=(filename, curr_sock, other_sock))
                                                send_thread.start()
                                        else:
                                            sendto = None
                                            uname = action.split("<")[1]
                                            for sock in self.unamelist:
                                                if uname == self.unamelist[sock]:
                                                    sendto = sock
                                            if sendto is None:
                                                curr_sock.send(bytes("Server: Please choose a valid action/Username", encoding='utf8'))
                                            else:
                                                self.msgs_list.append((curr_sock, msg, sendto))
                                except ValueError:
                                    curr_sock.send(bytes("server: You cannot send an empty message. Please try again.", encoding='utf8'))
                    except ConnectionResetError:
                        print(self.unamelist[curr_sock] + " forcibly disconnected.")
                        self.clientlist.remove(curr_sock)
                        del self.unamelist[curr_sock]
                        # del self.downloads_per_client[curr_sock]
            for msg in self.msgs_list:
                (curr_client, data, sendto) = msg
                if sendto == "all":
                    for sock in self.clientlist:
                        if sock != curr_client:
                            newdata = self.unamelist[curr_client] + " to All: " + data
                            sock.send(bytes(str(datetime.datetime.now().time().replace(microsecond=0)) + " " + newdata, encoding='utf8'))
                    print(self.unamelist[curr_client] + " to All: " + data.strip())
                elif sendto == "server":
                    if data.strip() == "disconnect" or data.strip() == "Disconnect":
                        # if self.downloads_per_client[curr_client] != 0:
                        #     curr_client.send(bytes("You cannot disconnect while downloading a file.", encoding='utf8'))
                        # else:
                        curr_client.send(bytes("server: Goodbye", encoding='utf8'))
                        curr_client.close()
                        print("Disconnected " + self.unamelist[curr_client])
                        self.clientlist.remove(curr_client)
                        del self.unamelist[curr_client]
                            # del self.downloads_per_client[curr_client]
                    elif data.strip() == "clist" or data.strip() == "Clist":
                        usernames = list()
                        for sock in self.unamelist:
                            usernames.append(self.unamelist[sock])
                        curr_client.send(bytes("Active clients: " + str(usernames), encoding='utf8'))
                    elif data.strip() == "flist" or data.strip() == "Flist":
                        filelist = [file for file in listdir(".\\Files") if isfile(join(".\\Files", file))]
                        curr_client.send(bytes("Available files: " + str(filelist), encoding='utf8'))
                elif sendto == "download":
                    send_thread = threading.Thread(target=self.down_file, args=(data.strip(), curr_client), daemon=True)
                    send_thread.start()
                elif sendto is not None:  #Could be simply else, but is elif just in case of an unexpected issue
                    try:
                        sendto.send(bytes(str(datetime.datetime.now().time().replace(microsecond=0)) + " " + self.unamelist[curr_client] + ": " + data, encoding='utf8'))
                        print(self.unamelist[curr_client] + " to " + self.unamelist[sendto] + ": " + data.strip())
                    except Exception:
                        curr_client.send(bytes("ERROR", encoding='utf8'))
                        print("Unknown error occurred")
                self.msgs_list.remove(msg)

    def down_file(self, filename: str, sock: socket.socket):
        port = 55001 + self.num_of_tcpsockets_open
        self.num_of_tcpsockets_open += 1
        sock.send(bytes("port" + str(port), encoding='utf8'))
        serv_sock = socket.socket()
        serv_sock.bind(('127.0.0.1', port))
        serv_sock.listen(1)
        file = builtins.open(".\\Files\\" + filename, 'r')
        (client, addr) = serv_sock.accept()  # Not blocking anything because it is in a different thread
        pack_num = 0
        while True:
            client.send(bytes(filename, encoding='utf8'))
            res = client.recv(1024)
            if bytes.decode(res, encoding='utf8') != "Connection faulty":
                break
        print("Sending file")
        data = file.read(1024)
        lastbyte = "None"
        while data:
            client.send(bytes(data, encoding='utf8'))
            sleep(0.002)
            client.send(bytes("packet" + str(pack_num), encoding='utf8'))
            res = client.recv(1024)
            if bytes.decode(res, encoding='utf8') == "received" + str(pack_num):  # Wait for the correct response before sending another packet
                data = file.read(1024)
                pack_num += 1
            try:
                lastbyte = data[len(data)-1]
            except IndexError:
                pass
        client.send(bytes("!@#$%^&*()", encoding='utf8'))
        file.close()
        serv_sock.close()
        sock.send(bytes("Server: finished downloading file. last byte was " + str(lastbyte), encoding='utf8'))
        print("Sent file to " + self.unamelist[sock])

    def send_file(self, filename, src_sock: socket.socket, dest_sock: socket.socket):
        dest_sock.send(bytes("Server: " + self.unamelist[src_sock] + " is sending you a file...", encoding='utf8'))
        recv_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        recv_sock.bind(('127.0.0.1', 0))
        src_sock.send(bytes("port" + str(recv_sock.getsockname()[1]), encoding='utf8'))
        msg, recv_addr = recv_sock.recvfrom(1024)
        if bytes.decode(msg, encoding='utf8').strip() != filename:  # This condition will never realistically be true, yet it is just in case of an extremely weird error
            print(bytes.decode(msg, encoding='utf8').strip() + ", " + filename)
            print("Filenames do not match, yet the transfer will most likely be successful")
        send_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sleep(0.002)
        dest_sock.send(bytes("<recv>" + filename, encoding='utf8'))
        sleep(0.02)  # Giving the client time to open a new connection and send back the port
        send_sock.sendto(bytes(filename, encoding='utf8'), ('127.0.0.1', self.file_port))
        res, send_addr = send_sock.recvfrom(1024)
        if bytes.decode(res, encoding='utf8') == "Connected":
            recv_sock.sendto(bytes("Connected", encoding='utf8'), recv_addr)
        else:
            print("Failed to connect")
            dest_sock.send(bytes("Server: File transfer failed", encoding='utf8'))
            src_sock.send(bytes("Server: File transfer failed", encoding='utf8'))
            send_sock.close()
            recv_sock.close()
            return
        pack_num = 0
        lastbyte = "None"
        while True:
            data, recv_addr = recv_sock.recvfrom(1024)
            if bytes.decode(data, 'utf8') == "!@#$%^&*()":
                send_sock.sendto(data, send_addr)
                print("Sent file from " + self.unamelist[src_sock] + " to " + self.unamelist[dest_sock])
                dest_sock.send(bytes("Server: downloaded file sent by " + self.unamelist[src_sock] + " as " + filename + ". Last byte was " + str(lastbyte), encoding='utf8'))
                src_sock.send(bytes("Server: sent file successfully to " + self.unamelist[dest_sock] + ". Last byte was " + str(lastbyte), encoding='utf8'))
                send_sock.close()
                recv_sock.close()
                return
            sleep(0.002)
            res, recv_addr = recv_sock.recvfrom(1024)
            if bytes.decode(res, encoding='utf8') == "packet" + str(pack_num):
                send_sock.sendto(data, send_addr)
                sleep(0.002)
                send_sock.sendto(bytes("packet" + str(pack_num), encoding='utf8'), send_addr)
                res, addr = send_sock.recvfrom(1024)
                if bytes.decode(res, encoding='utf8') == "packet" + str(pack_num):
                    recv_sock.sendto(bytes("packet" + str(pack_num), encoding='utf8'), recv_addr)
                    pack_num += 1
            elif int(bytes.decode(res, encoding='utf8')[6:]) != pack_num:
                print("packet " + str(pack_num) + " lost")
            try:
                lastbyte = data[len(data)-1]
            except IndexError:
                pass


