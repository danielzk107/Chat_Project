import sys
import threading
import Client

if __name__ == '__main__':
    print(
        "Here are the codewords for certain actions:\n'<all>': send message to everyone\n'<server>': perform action related directly to the server (Connect, Disconnect, get user list, etc)\n'<username>': send private message\n<help>: list of more actions")
    client = Client.Client()
    inputthread = threading.Thread(target=client.deal_with_input)
    inputthread.start()
    recvthread = threading.Thread(target=client.recv_loop)
    recvthread.start()
    for line in sys.stdin:
        client.inputq.put(line)
