import socket
import time


class CorruptedDataError(RuntimeError):
    pass


class Server:

    def __init__(self):
        self.corruptedDataCounter = 0
        self.startTime = time.time()
        self.startTime2 = time.time()

        udp_ip = socket.gethostname()
        udp_port = 6969
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # UDP
        self.sock.bind((udp_ip, udp_port))
        self.sock.settimeout(0.01)

    def checkConection(self):
        if self.corruptedDataCounter > 19:
            raise ConnectionError("20 or more instance's of corrupted data has been recorded")

        if time.time() - self.startTime > 10:
            self.corruptedDataCounter = 0
            self.startTime = time.time()

    def receive(self) -> list:
        data = None
        try:
            messageType, addr = self.sock.recvfrom(10024)  # buffer size is 10024 bytes

            if messageType.decode() == "a":
                print("Type: ", messageType)
                data = self.parse2dArray()

            self.startTime2 = time.time()

        except socket.timeout as e:
            pass
        except CorruptedDataError as e:
            self.corruptedDataCounter += 1
        except TimeoutError as e:
            pass

        self.checkConection()
        if time.time() - self.startTime2 > 5:
            raise TimeoutError("No data receded in 5 seconds")

        return data

    def parse2dArray(self) -> list:
        startTime = time.time()
        while True:
            try:
                header, addr = self.sock.recvfrom(10024)  # buffer size is 10024 bytes

                if len(header) < 3:  # Header is to short, data probably lost.
                    raise CorruptedDataError("header receded is corrupt")

                x = int(header[0])
                y = int(header[2])
                size = x * y
                print("Header: ", header)

                if time.time() - startTime > 0.5:  # Timeout
                    raise TimeoutError("timed out wn receding header")
                break
            except socket.timeout as e:
                pass

        startTime = time.time()
        data = b""
        while True:
            try:
                dataPart, addr = self.sock.recvfrom(10024)  # buffer size is 10024 bytes
                data += dataPart
                if len(data) == x * y:  # Reseved all data
                    break
                if time.time() - startTime > 0.5:  # Timeout
                    raise TimeoutError("timed out wn receding data")
            except socket.timeout as e:
                pass

        array = []
        i = 0
        for x in range(100):
            temp = []
            for y in range(200):
                temp.append(data[i])
            array.append(temp)
        return array


if __name__ == '__main__':
    s = Server()
