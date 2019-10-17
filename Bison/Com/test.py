import socket

UDP_IP = socket.gethostname()
UDP_PORT = 6969

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # UDP
sock.bind((UDP_IP, UDP_PORT))
sock.settimeout(0.01)

while True:
    x = 0
    y = 0
    while True:
        try:
            data, addr = sock.recvfrom(10024)  # buffer size is 10024 bytes
            print("her er a: ", data)
            break
        except socket.timeout as e:
            pass

    while True:
        try:
            data, addr = sock.recvfrom(10024)  # buffer size is 10024 bytes
            x = int(data[0])
            y = int(data[2])
            print("her er tall: ", data)
            break
        except socket.timeout as e:
            pass
    data2 = b""
    while True:
        try:
            data, addr = sock.recvfrom(10024)  # buffer size is 10024 bytes
            data2 += data
            if len(data2) == x * y:
                break
        except socket.timeout as e:
            pass
    print(len(data2))
    array = []
    i = 0
    for x in range(100):
        temp = []
        for y in range(200):
            temp.append(data2[i])
        array.append(temp)
    print(array)
    # print(len(array))
    # print(len(array[0]))
