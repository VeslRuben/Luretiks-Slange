import socket
import time


class UdpConnection:

    def __init__(self, url: str):
        """
        :param url: The url to communicate with
        """
        self.timeOutTimer = time.time()
        self.connectionTimedOut = False
        self.timeOut = 3

        self.url = url
        udp_ip = "192.168.137.1"
        udp_port = 6969
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # UDP
        self.socket.bind((udp_ip, udp_port))
        self.socket.settimeout(0.01)

    def send(self, data: str) -> None:
        """
        Sends a udp diagram \n
        :param data: data to send
        :return: None
        """
        self.socket.sendto(data.encode(), (self.url, 9696))

    def receive(self):
        """
        Recevs data and decodes it based on the header \n
        :return: The body of the data
        """
        data = None
        try:
            data, addr = self.socket.recvfrom(10024)  # buffer size is 10024 bytes
            data = data.decode()

        except socket.timeout:
            pass

        return data

if __name__ == '__main__':
    s = UdpConnection("192.168.137.167")

    while True:
        f = input(': ')
        time.sleep(0.1)
        print(s.receive())
        s.send(f)

