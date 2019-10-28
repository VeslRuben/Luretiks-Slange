import time
from Bison.Com.videoStream import VideoStream
from Bison.Com.udpCom import UdpConnection
import numpy as np


class snake:

    def __init__(self, cameraIp: str, controllerIp: str):
        self.camera = VideoStream("http://192.168.137.171")
        self.controller = UdpConnection("192.168.137.159")

    def setFrameSize(self, size: int):
        """
        Sets the size of the images taken \n
        :param size: Size of the image represented by an integer value.
            10 = 1600 x 1200,
            9 = 1280 x 1024,
            8 = 1024 x 768,
            7 = 800 x 600,
            6 = 640 x480,
            5 = 400 x 296,
            4 = 320 x 240,
            3 = 240 x 176,
            0 = 160 x 120,
        :return: None
        """
        self.camera.reSize(size)

    def takePicture(self) -> np.array:
        """
        Takes a picrure fom the front facing camera on the snake. \n
        The picture has the size set form the setFrame() metode. \n
        :return: returns a picrure as a numpy array
        """
        picture = self.camera.getPicture()
        return picture

    def moveForward(self):
        self.controller.send("f")

    def moveBacwards(self):
        self.controller.send("b")

    def turn(self, degreas: int):
        """
        Seds a turn comand to the snake. \n
        positive degras is right and negative is left \n
        :param degreas: turnrate in deagras
        :return: None
        """
        degreas = 90 + degreas
        self.controller.send("t")
        time.sleep(0.1)
        self.controller.send(str(degreas))

    def moveLeft(self):
        self.controller.send("l")

    def moveRight(self):
        self.controller.send("r")

    def isControllerAlive(self) -> bool:
        """
        cheks if the controller is connnected \n
        :return: true if controller is connected
        """
        self.controller.receive()
        return self.controller.isAlive()
