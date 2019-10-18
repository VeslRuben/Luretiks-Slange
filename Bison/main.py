import numpy as np
import cv2
from Bison.Com.webServer import Server

server = Server()

while True:
    inn = input("-> ")

    server.send(inn)
