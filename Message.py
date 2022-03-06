import builtins
import select
import socket
import sys
from time import sleep

if __name__ == '__main__':
    sock = socket.socket()
    sock.bind(('127.0.0.1', 55000))
    sock.listen(1)
    clientlist = []
    file = open(".\\Files\\file1.txt", 'r')
    (client, addr) = sock.accept()  #Not blocking anything because it is in a different thread
    print("Sending file")
    data = file.read(1024)
    while data:
        client.send(bytes(data, encoding='utf8'))
        res = client.recv(1024)
        if bytes.decode(res, encoding='utf8') == "received":
            data = file.read(1024)
    client.send(bytes("!@#", encoding='utf8'))
    file.close()
    sock.close()
    print("Sent file")
