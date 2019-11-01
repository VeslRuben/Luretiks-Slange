import time
from Bison.Com.videoStream import VideoStream
from Bison.Com.udpCom import UdpConnection
import numpy as np
from Bison.logger import Logger


class Snake:

    def __init__(self, cameraIp: str, controllerIp: str):
        self.camera = VideoStream(cameraIp)
        self.controller = UdpConnection(controllerIp)

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
        Logger.logg("Picture taken by snake", Logger.cmd)
        return picture

    def moveForward(self):
        self.controller.send("f")
        Logger.logg("Sent: f", Logger.cmd)

    def moveBacwards(self):
        self.controller.send("b")
        Logger.logg("Sent: b", Logger.cmd)

    def turn(self, degreas: int):
        """
        Seds a turn comand to the snake. \n
        positive degras is right and negative is left \n
        :param degreas: turnrate in deagras
        :return: None
        """
        send = None
        degreas = 90 + degreas
        if degreas < 10:
            send = "t00" + str(degreas)
        elif degreas < 100:
            send = "t0" + str(degreas)
        else:
            send = "t" + str(degreas)
        self.controller.send(send)
        Logger.logg(f"Sent turn: {degreas}", Logger.cmd)

    def moveLeft(self):
        self.controller.send("v")
        Logger.logg("Sent: v", Logger.cmd)

    def moveRight(self):
        self.controller.send("h")
        Logger.logg("Sent: h", Logger.cmd)

    def stop(self):
        self.controller.send("s")
        Logger.logg("Sent: s", Logger.cmd)

    def reset(self):
        self.controller.send("r")
        Logger.logg("Sent: r", Logger.cmd)

    def isControllerAlive(self) -> bool:
        """
        cheks if the controller is connnected \n
        :return: true if controller is connected
        """
        self.controller.receive()
        return self.controller.isAlive()


if __name__ == "__main__":
    s = Snake("http://192.168.137.171", "192.168.137.60")
    while True:
        i = input("-> ")
        if i == "f":
            s.moveForward()
        elif i == "s":
            s.stop()
        elif i == "r":
            s.reset()
        else:
            s.turn(int(i))
