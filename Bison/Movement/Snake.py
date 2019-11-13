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
        """
        Checks for acknowledge from the snake. Times out after a set amount of time given from self.timeOutTime
        :return:  True if acknowledged, False if timed out
        """
        timeOutTime = time.time() + self.timeOutTime
        while True:
            data = self.controller.receive()
            if data == "a":
                Logger.logg(f"Acc received from snake", Logger.info)
                return True
            if time.time() > timeOutTime:
                Logger.logg(f"No acc received from snake", Logger.warning)
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
        """
        Sets the period time of the cycle for the snake
        :param speed: the period time in 3 digits
        :return: True if acknowledged from snake
        """
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
        """
        Sets the amplitude of the snakes movement
        :param amplitude: amplitude in 2 digits
        :return: True if acknowledged from snake
        """
        send = ""
        if amplitude < 10:
            send = "a0" + str(amplitude)
        else:
            send = "a" + str(amplitude)

        self.controller.send(send)
        return self.timeOut()

    def moveForward(self):
        """
        Gives the command to the snake to move forward one cycle
        :return: True if acknowledged
        """
        self.controller.send("f")
        Logger.logg("Sent: f", Logger.cmd)
        return self.timeOut()

    def moveBacwards(self):
        """
        Gives the command to the snake to move backward one cycle
        :return: True if acknowledged
        """
        self.controller.send("b")
        Logger.logg("Sent: b", Logger.cmd)
        return self.timeOut()

    def turn(self, degrees: int):
        """
        Sends a turn command to the snake. \n
        positive degrees is right and negative is left \n
        :param degrees: turnrate in degrees
        :return: True if acknowledged
        """
        send = None
        degrees = 90 + degrees
        if degrees < 10:
            send = "t00" + str(degrees)
        elif degrees < 100:
            send = "t0" + str(degrees)
        else:
            send = "t" + str(degrees)
        self.controller.send(send)
        Logger.logg(f"Sent turn: {degrees}", Logger.cmd)
        return self.timeOut()

    def moveLeft(self):
        """
        Sends command to snake to lateral shift left
        :return: True if acknowledged
        """
        self.controller.send("v")
        Logger.logg("Sent: v", Logger.cmd)
        return self.timeOut()

    def moveRight(self):
        """
        Sends command to snake to lateral shift right
        :return: True if acknowledged
        """
        self.controller.send("h")
        Logger.logg("Sent: h", Logger.cmd)
        return self.timeOut()

    def stop(self):
        """
        Sends command to snake to stop movement
        :return: True if acknowledged
        """
        self.controller.send("s")
        Logger.logg("Sent: s", Logger.cmd)
        return self.timeOut()

    def reset(self):
        """
        Sends command to reset positions to zero point.
        :return: True if acknowledged
        """
        self.controller.send("r")
        Logger.logg("Sent: r", Logger.cmd)
        return self.timeOut()

    def isCommandDone(self) -> bool:
        """
        Checks if the snake is done with the last command
        :return: True if command is done
        """
        data = self.controller.receive()
        if data == "d":
            Logger.logg(f"Snake finished command", Logger.info)
            return True
        else:
            return False


if __name__ == "__main__":
    s = Snake("http://192.168.137.72", "192.168.137.76")
    print(s.reset())

    while True:
        done = s.isCommandDone()
        print(done)
        if done:
            break
