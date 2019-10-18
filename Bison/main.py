import numpy as np
import cv2
from Bison.Com.webServer import Server

server = Server()

while True:
    data = server.receive()
    print(data)
    if data != None:
        picture = np.array(data)