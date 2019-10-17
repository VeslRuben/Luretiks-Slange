import socket
import time
import select
import numpy as np


class Server:

    def __init__(self):
        self.host = socket.gethostname()
        self.port = 6969

        self.server_socet = socket.socket()
        self.server_socet.bind((self.host, self.port))
        self.server_socet.listen(2)

        self.conn, self.addr = self.server_socet.accept()
        print(self.addr)
        self.conn.settimeout(0.001)

    def reconnect(self):
        self.conn, self.addr = self.server_socet.accept()
        print(self.addr)
        self.conn.settimeout(0.001)

    def send(self, data: str):
        self.conn.send(data.encode("utf-8"))

    def test(self):
        message = ""
        while True:
            data = self.receive()
            if data.strip() != "":
                message += data
            if message.__contains__("fin"):
                break
        print(message)

    def receive(self):
        message = ""
        try:
            # receive data stream. it won't accept data packet greater than 1024 bytes
            data = self.conn.recv(1024).decode()
            message += data
        except Exception as e:
            pass
        return message

    def close(self):
        self.conn.close()


if __name__ == '__main__':
    s = Server()
    s.test()
