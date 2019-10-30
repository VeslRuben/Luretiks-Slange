import cv2
import numpy as np
from Bison.ImageProcessing.camera import Camera
import imutils

class FindSnake:

    def __init__(self):


        pass

    def LocateSnake(self, frame):

        redLower = np.array([100, 170, 40], dtype=np.uint8)
        redUpper = np.array([140, 255, 240], dtype=np.uint8)

        blueLower = np.array([100, 150, 0], dtype=np.uint8)
        blueUpper = np.array([140, 255, 255], dtype=np.uint8)

        lowerWhite = np.array([0, 0, 180], dtype=np.uint8)
        upperWhite = np.array([145, 60, 255], dtype=np.uint8)

        blurred = cv2.GaussianBlur(frame, (11, 11), 0)
        color1 = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)
        maskB = cv2.inRange(color1, blueLower, blueUpper)
        color2 = cv2.cvtColor(blurred, cv2.COLOR_RGB2HSV)
        maskR = cv2.inRange(color2, redLower, redUpper)
        maskW = cv2.inRange(color1, lowerWhite, upperWhite)

        cnts = cv2.findContours(maskR, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cnts = imutils.grab_contours(cnts)
        slangeHeil = maskR +maskB+maskW
        for c in cnts:
            M = cv2.moments(c)
            x = int(M["m10"] / M["m00"])
            y = int(M["m01"] / M["m00"])
            cv2.circle(maskR, (x, y), 7, (255, 255, 255), -1)
            return x,y
        pass







if __name__ == "__main__":
    cam = Camera()
    Camera.initCam(1)
    frame = cam.takePicture()
    c = FindSnake()
    x,y = c.LocateSnake(frame)
    print(x, y)

