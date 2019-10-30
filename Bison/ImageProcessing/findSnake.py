import cv2
import numpy as np
from Bison.ImageProcessing.camera import Camera
import imutils


class FindSnake:

    def __init__(self):

        pass

    def LocateSnake(self, frame):
        blackLower = np.array([0, 0, 0], dtype=np.uint8)
        blackUpper = np.array([200, 200, 30], dtype=np.uint8)

        redLower = np.array([100, 170, 40], dtype=np.uint8)
        redUpper = np.array([140, 255, 240], dtype=np.uint8)

        blueLower = np.array([100, 150, 0], dtype=np.uint8)
        blueUpper = np.array([140, 255, 255], dtype=np.uint8)

        lowerWhite = np.array([0, 0, 180], dtype=np.uint8)
        upperWhite = np.array([145, 60, 255], dtype=np.uint8)

        blurred = cv2.GaussianBlur(frame, (7, 7), 0)
        color1 = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)
        maskB = cv2.inRange(color1, blueLower, blueUpper)
        maskBl = cv2.inRange(color1, blackLower, blackUpper)
        maskBl = cv2.erode(maskBl, None, iterations=4)
        maskBl = cv2.dilate(maskBl, None, iterations=5)

        color2 = cv2.cvtColor(blurred, cv2.COLOR_RGB2HSV)
        maskR = cv2.inRange(color2, redLower, redUpper)
        maskR = cv2.erode(maskR, None, iterations=3)
        maskR = cv2.dilate(maskR, None, iterations=4)

        maskW = cv2.inRange(color1, lowerWhite, upperWhite)
        cnts1 = cv2.findContours(maskBl, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cnts1 = imutils.grab_contours(cnts1)

        cnts = cv2.findContours(maskR, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cnts = imutils.grab_contours(cnts)
        try:
            M1 = cv2.moments(cnts1[0])
            x1 = int(M1["m10"] / M1["m00"])
            y1 = int(M1["m01"] / M1["m00"])
            cv2.circle(maskBl, (x1, y1), 7, (255, 255, 0), -1)

            M = cv2.moments(cnts[0])
            x0 = int(M["m10"] / M["m00"])
            y0 = int(M["m01"] / M["m00"])
            cv2.circle(maskR, (x0, y0), 7, (255, 255, 0), -1)
            return [[x0, y0], [x1, y1]], cv2.cvtColor(maskBl + maskR, cv2.COLOR_GRAY2RGB)
        except ZeroDivisionError as e:
            return None


if __name__ == "__main__":
    cam = Camera()
    Camera.initCam(0)
    frame = cam.takePicture()
    c = FindSnake()
    cords, yolo = c.LocateSnake(frame)
    cv2.imshow("yolo",yolo)
    cv2.waitKey()
    cv2.destroyAllWindows()
    print(cords)
