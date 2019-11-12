import time
from Bison.Com.videoStream import VideoStream
from Bison.Com.udpCom import UdpConnection
import numpy as np
from Bison.logger import Logger


class Snake:

    def __init__(self, cameraIp: str, controllerIp: str):
        self.camera = VideoStream(cameraIp)
        self.controller = UdpConnection(controllerIp)
        self.timeOutTime = 0.5

    def timeOut(self):
        timeOutTime = time.time() + self.timeOutTime
        while True:
            data = self.controller.receive()
            if data == "a":
                Logger.logg(f"Acc resived from snake", Logger.info)
                return True
            if time.time() > timeOutTime:
                Logger.logg(f"no acc recevd from snake", Logger.warning)
                return False

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

    def setSpeed(self, speed: int):
        send = ""
        if speed < 10:
            send = "p00" + str(speed)
        elif speed < 100:
            send = "p0" + str(speed)
        else:
            send = "p" + str(speed)
        self.controller.send(send)
        return self.timeOut()

    def setAmplitude(self, amplitude: int):
        send = ""
        if amplitude < 10:
            send = "a0" + str(amplitude)
        else:
            send = "a" + str(amplitude)

        self.controller.send(send)
        return self.timeOut()

    def moveForward(self):
        self.controller.send("f")
        Logger.logg("Sent: f", Logger.cmd)
        return self.timeOut()

    def moveBacwards(self):
        self.controller.send("b")
        Logger.logg("Sent: b", Logger.cmd)
        return self.timeOut()

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
        return self.timeOut()

    def moveLeft(self):
        self.controller.send("v")
        Logger.logg("Sent: v", Logger.cmd)
        return self.timeOut()

    def moveRight(self):
        self.controller.send("h")
        Logger.logg("Sent: h", Logger.cmd)
        return self.timeOut()

    def stop(self):
        self.controller.send("s")
        Logger.logg("Sent: s", Logger.cmd)
        return self.timeOut()

    def reset(self):
        self.controller.send("r")
        Logger.logg("Sent: r", Logger.cmd)
        return self.timeOut()

    def isComandDone(self) -> bool:
        """
        cheks if the controller is connnected \n
        :return: true if controller is connected
        """
        data = self.controller.receive()
        if data == "d":
            Logger.logg(f"snake finisht command", Logger.info)
            return True
        else:
            return False


if __name__ == "__main__":
    s = Snake("http://192.168.137.72", "192.168.137.76")
    print(s.reset())

    while True:
        done = s.isComandDone()
        print(done)
        if done:
            break
