import os
import queue
import select
import signal
import socket
import threading
from time import sleep
from socket import *


class Client:

    def __init__(self):
        self.sock = socket(AF_INET, SOCK_STREAM)
        self.sock.connect(('127.0.0.1', 55000))
        self.uname = input("Your Username: ")
        self.socket_list = [self.sock]
        self.file_port = 0  #Will change every time we download a file to fit the actual port
        self.Sending_File = False
        self.connected = False
        self.disconnected = False
        self.oktosend = True  # Will change to false only if the username provided does not exist
        self.inputq = queue.Queue()

    def deal_with_input(self):
        while True:
            if self.disconnected:
                break
            if not self.connected:
                self.sock.send(bytes(self.uname, encoding='utf8'))
                self.connected = True
            else:
                try:
                    action = self.inputq.get(timeout=3600)
                    first10 = action[0:10]
                    first6 = action[0:6]
                    if first6 == "<send>":
                        if self.Sending_File:
                            print("You cannot send two files at once.")
                        else:
                            (username, filename) = action[7:].split(">")
                            filefound = True
                            try:
                                file = open(filename.strip(), 'r')
                                file.close()
                            except FileNotFoundError:
                                print("File not found.")
                                filefound = False
                            if filefound:
                                self.sock.send(bytes(action, encoding='utf8'))
                                sleep(0.1)  # wait for the server to open the new connection before trying to receive from it
                                send_thread = threading.Thread(target=self.send_file_UDP, args=(filename.strip(), username))
                                send_thread.start()
                    elif first10 == "<download>":
                        self.sock.send(bytes(action, encoding='utf8'))
                        sleep(0.1)  # wait for the server to open the new connection before trying to receive from it
                        down_thread = threading.Thread(target=self.recv_file_TCP, args=(action[10:].strip(),), daemon=True)
                        down_thread.run()
                    elif action.strip() == "<help>" or action.strip() == "<Help>":
                        print("Here are the codewords for certain actions:\n'<all>': send message to everyone\n'<server>': perform action related directly to the server (Disconnect, get user list, etc)\n'<username>': send private message\nAll server actions (type one of these after '<server>':\ndisconnect - ask the server to disconnect. will shut down the program.\nclist - ask the server to send the list of active clients\nflist - ask the server to send the list of all available file names\n\nIn order to download a file from the server, type <download> filename\nIn order to send a file to another user, type <send><username>filename")
                    else:
                        self.sock.send(bytes(action, encoding='utf8'))
                except queue.Empty:
                    self.sock.send(bytes("<server>disconnect", encoding='utf8'))
                    self.disconnected = True
                    break

    def recv_loop(self):
        while True:
            read_list, _, _ = select.select(self.socket_list, [], [], 5)
            for curr_sock in read_list:
                response = bytes.decode(self.getmsg(curr_sock), encoding='utf8')
                if response[0:4] == "port":
                    # print(response[4:].strip())
                    self.file_port = int(response[4:].strip())
                elif response[0:6] == "<recv>":
                    recv_thread = threading.Thread(target=self.recv_file_UDP, args=(response[6:].strip(), ))
                    recv_thread.start()

                else:
                    if response == "Server: Username not available":
                        self.oktosend =False
                    if response == "server: Goodbye":
                        self.disconnected = True
                    if response == "ERROR":
                        response = "Unknown Server error"
                        try:
                            self.sock.send(bytes("<server>disconnect", encoding='utf8'))
                        except ConnectionResetError:
                            response = "Server is down. Goodbye!"
                        print(response)
                        self.sock.close()
                        os.kill(os.getpid(), signal.SIGINT)
                        exit()
                    print(response.strip())
            if self.disconnected:
                self.sock.close()
                os.kill(os.getpid(), signal.SIGINT)
                exit()

    def recv_file_TCP(self, filename):
        sock = socket(AF_INET, SOCK_STREAM)
        sock.connect(('127.0.0.1', int(self.file_port)))
        pack_num = 0
        while True:
            data = sock.recv(1024)
            if data:
                print("Now downloading", bytes.decode(data, encoding='utf8'))
                sock.send(bytes("Response", encoding='utf8'))
            else:
                sock.send(bytes("Connection faulty", encoding='utf8'))
            nametaken = True
            i = 1
            while nametaken:  # Making sure not to override existing files
                try:
                    file = open(filename, 'r')
                    # try:
                    #     filename = filename.split("(")[0] + "(" + str(i) + ")" + filename.split(")")[1]
                    # except ValueError:
                    filename = filename.split(".")[0] + "(" + str(i) + ")." + filename.split(".")[1]
                    i += 1
                except FileNotFoundError:
                    nametaken = False
            file = open(filename, 'wb')
            while True:
                data = sock.recv(1024)
                if bytes.decode(data, 'utf8') == "!@#$%^&*()":
                    print("Downloaded and saved file as " + filename)
                    sock.close()
                    return
                sleep(0.002)
                pack_res = sock.recv(1024)
                if bytes.decode(pack_res, encoding='utf8') == "packet" + str(pack_num):
                    file.write(data)
                    sock.send(bytes("received" + str(pack_num), encoding='utf8'))
                    pack_num += 1
                elif int(bytes.decode(pack_res, encoding='utf8')[6:]) != pack_num:
                    print("packet " + str(pack_num) + " lost")

    def send_file_UDP(self, filename: str, username: str):
        sleep(0.02)
        if not self.oktosend:
            self.oktosend = True
            return
        serv_sock = socket(AF_INET, SOCK_DGRAM)
        serv_sock.sendto(bytes(filename, encoding='utf8'), ('127.0.0.1', self.file_port))
        res, addr = serv_sock.recvfrom(1024)
        if bytes.decode(res, encoding='utf8') == "Connected":
            print("Sending file to " + username)
        else:
            print("Action Failed")
            serv_sock.close()
            return
        file = open(filename, 'r')
        data = file.read(1024)
        pack_num = 0
        while data:
            serv_sock.sendto(bytes(data, encoding='utf8'), addr)
            sleep(0.002)
            serv_sock.sendto(bytes("packet" + str(pack_num), encoding='utf8'), addr)
            res, addr = serv_sock.recvfrom(1024)
            if bytes.decode(res, encoding='utf8') == "packet" + str(pack_num):
                data = file.read(1024)
                pack_num += 1
        serv_sock.sendto(bytes("!@#$%^&*()", encoding='utf8'), addr)
        file.close()
        serv_sock.close()
        print("Sent file to " + username)

    def recv_file_UDP(self, filename):
        sock = socket(AF_INET, SOCK_DGRAM)
        sock.bind(("127.0.0.1", 0))
        self.sock.send(bytes("port" + str(sock.getsockname()[1]), encoding='utf8'))
        msg, addr = sock.recvfrom(1024)
        if bytes.decode(msg, encoding='utf8') != filename:
            print("Filenames do not match, yet the transfer will most likely be successful")
        sock.sendto(bytes("Connected", encoding='utf8'), addr)
        nametaken = True
        i = 1
        while nametaken:  # Making sure not to override existing files
            try:
                file = open(filename, 'r')
                # try:
                #     filename = filename.split("(")[0] + "(" + str(i) + ")" + filename.split(")")[1]
                # except ValueError:
                filename = filename.split(".")[0] + "(" + str(i) + ")." + filename.split(".")[1]
                i += 1
            except FileNotFoundError:
                nametaken = False
        file = open(filename, 'wb')
        pack_num = 0
        while True:
            data, addr = sock.recvfrom(1024)
            if bytes.decode(data, 'utf8') == "!@#$%^&*()":
                print("File Downloaded and saved as " + filename)
                sock.close()
                return
            sleep(0.002)
            res, addr = sock.recvfrom(1024)
            if bytes.decode(res, encoding='utf8') == "packet" + str(pack_num):
                file.write(data)
                sock.sendto(bytes("packet" + str(pack_num), encoding='utf8'), addr)
                pack_num += 1
            elif int(bytes.decode(res, encoding='utf8')[6:]) != pack_num:
                print("packet " + str(pack_num) + " lost")

    def getmsg(self, sock):
        try:
            res = sock.recv(1024)
            if not res:
                print("ERROR")
                return bytes("ERROR", encoding='utf8')
        except ConnectionResetError:
            return bytes("ERROR", encoding='utf8')
        return res



