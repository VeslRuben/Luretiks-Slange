import socket

class Server:
    host = socket.gethostname()
    port = 6969

    server_socet = socket.socket()
    server_socet.bind((host,port))

    server_socet.listen(2)
    conn, addr = server_socet.accept()
    print(addr)

    while True:
            # receive data stream. it won't accept data packet greater than 1024 bytes
            data = conn.recv(1024).decode()
            if not data:
                # if data is not received break
                break
            print("from connected user: " + str(data))
            data = "yolo"
            conn.send(data.encode("utf-8"))  # send data to the client
    conn.close()  # close the connection


if __name__ == '__main__':
    Server
