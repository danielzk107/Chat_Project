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
        self.downloading_file = False
        self.connected = False
        self.disconnected = False
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
                    if first10 == "<download>":
                        if self.downloading_file:
                            print("You cannot download to files at once.")
                        else:
                            self.sock.send(bytes(action, encoding='utf8'))
                            sleep(0.1)
                            down_thread = threading.Thread(target=self.recv_file(action[10:].strip()))
                            down_thread.start()
                    elif action.strip() == "<help>" or action.strip() == "<Help>":
                        print("Here are the codewords for certain actions:\n'<all>': send message to everyone\n'<server>': perform action related directly to the server (Disconnect, get user list, etc)\n'<username>': send private message\nAll server actions (type one of these after '<server>':\ndisconnect - ask the server to disconnect. will shut down the program.\nclist - ask the server to send the list of active clients\nflist - ask the server to send the list of all available file names\n\nIn order to download a file, type <download> filename")
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
                else:
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

    def recv_file(self, filename):
        udp_sock = socket(AF_INET, SOCK_DGRAM)
        udp_sock.connect(('127.0.0.1', self.file_port))
        udp_sock.sendto(bytes("Connected", encoding='utf8'), ('127.0.0.1', self.file_port))
        print("Connected to file socket")
        file = open(filename, 'w')
        while True:
            read_list, _, _ = select.select([udp_sock], [], [], 5)
            if read_list.__sizeof__() > 0 and read_list[0]:
                data = bytes.decode(self.getmsg(read_list[0]), encoding='utf8')
                file.write(data)
            else:
                print("File downloaded and saved as " + str(filename))
                file.close()
                break
        udp_sock.close()
        # UDP_IP = "127.0.0.1"
        # IN_PORT = 5005
        # timeout = 3
        #
        # sock = socket(AF_INET, SOCK_DGRAM)
        # sock.bind((UDP_IP, IN_PORT))
        #
        # while True:
        #     data, addr = sock.recvfrom(1024)
        #     if data:
        #         print("File name:", data)
        #         file_name = data.strip()
        #     f = open(filename, 'wb')
        #     while True:
        #         ready = select.select([sock], [], [], timeout)
        #         if ready[0]:
        #             data, addr = sock.recvfrom(1024)
        #             f.write(data)
        #         else:
        #             print("%s Finish!" % filename)
        #             f.close()
        #             break

    def getmsg(self, sock):
        try:
            res = sock.recv(1024)
            if not res:
                print("ERROR")
                return bytes("ERROR", encoding='utf8')
        except ConnectionResetError:
            return bytes("ERROR", encoding='utf8')
        return res



