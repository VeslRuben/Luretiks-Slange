"""
Simple protocol to easily be able to use the same overhead camera in all different classes.

author: Håkon Bjerkgaard Waldum, Ruben Svedal Jørundland, Marcus Olai Grindvik
"""

import cv2


class Camera:
    """
    Controls a camera so multiple classes can access the same camera with minimal setup delay \n
    """

    cam = None

    @staticmethod
    def initCam(camNr: int = 0):
        """
        Initialise the camera class with a camera. \n
        must be called only once before getting an instance of the class \n
        :param camNr: Camera to use, 0 is usually the standard webCam on the PC
        :return: None
        """
        Camera.cam = cv2.VideoCapture(camNr)
        Camera.cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
        Camera.cam.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
        Camera.cam.set(cv2.CAP_PROP_AUTOFOCUS, 0)

    @staticmethod
    def releaseCam():
        """
        Release the camera. Called on program quit
        :return:
        """
        Camera.cam.release()

    def takePictureRgb(self):
        """
        Gets one picture from the camera and converts it to RGB
        :return: Picture in RGB as np-array
        """
        _, frame = Camera.cam.read()
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        return frame

    def takePicture(self):
        """
        Gets one picture from the camera
        :return: Picture as np-array
        """
        _, frame = Camera.cam.read()
        return frame
