import socket
import time
from Bison.logger import Logger


class UdpConnection:

    def __init__(self, url: str):
        """
        :param url: The url to communicate with
        """
        self.timeOutTimer = time.time()
        self.connectionTimedOut = False
        self.timeOut = 3

        self.url = url
        udp_ip = socket.gethostname()
        udp_port = 6969
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # UDP
        self.sock.bind((udp_ip, udp_port))
        self.sock.settimeout(0.01)

    def send(self, data: str) -> None:
        """
        Sends a udp diagram
        :param data: data to send
        :return: None
        """
        self.sock.sendto(data.encode(), (self.url, 9696))

    def receive(self):
        """
        Recevs data and decods it bast on the header
        :return: The body of the data
        """
        data = None
        try:
            header, addr = self.sock.recvfrom(10024)  # buffer size is 10024 bytes
            # Reads the header of the message

            if header.decode() == "alive":
                self.timeOutTimer = time.time()  # Resets the time out timer
                if self.connectionTimedOut:
                    Logger.logg(f"{self.url} has reconnected", Logger.info)
                self.connectionTimedOut = False
            elif header.decode() == "test":
                pass

        except socket.timeout:
            pass

        if time.time() - self.timeOutTimer > self.timeOut:
            self.connectionTimedOut = True
            Logger.logg(f"connetion to {self.url} has timed out")

        return data

    def isAlive(self) -> bool:
        """Return true if the connection is alive, else false"""
        return self.connectionTimedOut


if __name__ == '__main__':
    s = UdpConnection("192.168.137.159")

    while(True):
        f = input(': ')
        s.send(f)
