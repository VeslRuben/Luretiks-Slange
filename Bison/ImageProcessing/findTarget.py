# import the necessary packages
from collections import deque
from imutils.video import VideoStream
import numpy as np
import argparse
import cv2
import imutils
import time
from Bison.Com.videoStream import VideoStream


class findTarget:

    def __init__(self):
        pass
    def getTarget(self):

        blueLower = (100, 150, 0)
        blueUper = (140, 255, 255)

        ap = argparse.ArgumentParser()
        ap.add_argument("-b", "--buffer", type=int, default=64,
                        help="max buffer size")
        args = vars(ap.parse_args())
        pts = deque(maxlen=args["buffer"])
        frame = cv2.imread(r"C:\Users\marcu\PycharmProjects\Luretriks-Slange\Pictures\Front kamera\9.jpeg")

        height, width, channels = frame.shape
        scale = 1.0
        center = (width / 2, height / 2)
        angle90 = -90

        M = cv2.getRotationMatrix2D(center, angle90, scale)
        frame = cv2.warpAffine(frame, M, (height, width))
        time.sleep(0.5)

        cv2.imshow("bilde", frame)
        blurred = cv2.GaussianBlur(frame, (11, 11), 0)
        coulor = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(coulor, blueLower, blueUper)
        cv2.imshow("farger", mask)

        mask = cv2.dilate(mask, None, iterations=2)
        mask = cv2.erode(mask, None, iterations=2)

        cnts = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cnts = imutils.grab_contours(cnts)
        center = None

        if len(cnts) > 0:
            c = max(cnts, key=cv2.contourArea)
            ((x, y), radius) = cv2.minEnclosingCircle(c)
            M = cv2.moments(c)
            if radius > 3:
                cv2.circle(frame, (int(x), int(y)), int(radius),
                           (0, 255, 255), 2)
                cv2.circle(frame, center, 2, (0, 0, 255), -1)

        pts.appendleft(center)

        cv2.imshow("frame", frame)
        key = cv2.waitKey(1) & 0xFF



    cv2.destroyAllWindows()


if __name__ == "__main__":
    c = findTarget()
    c.getTarget()