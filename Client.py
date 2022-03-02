import os
import queue
import select
import signal
import socket
import sys
import threading
import pygame
from time import sleep
from socket import *


class Client:

    def __init__(self):
        self.sock = socket(AF_INET, SOCK_STREAM)
        self.sock.connect(('127.0.0.1', 55000))
        self.uname = input("Your Username: ")
        self.socket_list = [self.sock]
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
                    self.sock.send(bytes(action, encoding='utf8'))
                except queue.Empty:
                    self.sock.send(bytes("<server>disconnect", encoding='utf8'))
                    self.disconnected = True
                    break
        # self.sock.close()

    def recv_loop(self):
        while True:
            read_list, _, _ = select.select(self.socket_list, [], [], 5)
            for curr_sock in read_list:
                response = bytes.decode(self.getmsg(curr_sock), encoding='utf8')
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
        read_list, _, _ = select.select(self.socket_list, [], [], 5)
        srvsock = read_list[0]
        PORT = bytes.decode(self.getmsg(srvsock), encoding='utf8')
        udp_sock = socket(AF_INET, SOCK_DGRAM)
        udp_sock.connect(('127.0.0.1', PORT))
        file = open(filename, 'w')
        while True:
            read_list, _, _ = select.select([udp_sock], [], [], 5)
            if read_list[0]:
                data = bytes.decode(self.getmsg(read_list[0]), encoding='utf8')
                file.write(data)
            else:
                print("File downloaded and save as " + str(filename))
                file.close()
                break
        udp_sock.close()

    def getmsg(self, sock):
        try:
            res = sock.recv(1024)
            if not res:
                print("ERROR")
                return bytes("ERROR", encoding='utf8')
        except ConnectionResetError:
            return bytes("ERROR", encoding='utf8')
        return res



