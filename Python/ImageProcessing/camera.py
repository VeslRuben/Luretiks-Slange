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
        must be called ony ones before geting an instance of the class \n
        :param camNr: Camra to use, 0 is the standard webCam og te PC
        :return: None
        """
        Camera.cam = cv2.VideoCapture(camNr)
        Camera.cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
        Camera.cam.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
        Camera.cam.set(cv2.CAP_PROP_AUTOFOCUS, 0)

    @staticmethod
    def releaseCam():
        """
        Realsese the camera. called on program quit
        :return:
        """
        Camera.cam.release()

    def takePictureRgb(self):
        _, frame = Camera.cam.read()
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        return frame

    def takePicture(self):
        _, frame = Camera.cam.read()
        return frame
