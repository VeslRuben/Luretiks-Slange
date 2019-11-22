import cv2
import numpy as np
import imutils
from scipy.spatial import distance as dist
from Bison.Movement import Snake


class cheakPathForObs:

    def __init__(self):
        pass


    def FindObsInPath(self, bilde):
        center = None
        d = None
        x = None
        y = None
        radius = None
        notWhiteLower = ()
        notWhiteUpper = ()

        blurred = cv2.GaussianBlur(bilde, (11, 11), 0)
        color = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(color, notWhiteLower, notWhiteUpper)
        mask = cv2.dilate(mask, None, iterations=3)
        mask = cv2.erode(mask, None, iterations=3)

        cnts = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        cnts = imutils.grab_contours(cnts)
        if len(cnts) > 0:
            c = max(cnts, key=cv2.contourArea)
            ((x, y), radius) = cv2.minEnclosingCircle(c)
            M = cv2.moments(c)
            if radius > 10:
                center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
                cv2.circle(bilde, (int(x), int(y)), int(radius),
                           (0, 255, 255), 2)
                cv2.circle(bilde, center, 2, (0, 0, 255), -1)
        if x is not None and y is not None:
            d = dist.euclidean((x, y), (0, 0))

        if len(cnts) > 0 and d is not None and center is not None and radius is not None:
            return d, bilde, radius, center

        return None




if __name__ == "__main__":
    f = cheakPathForObs
    s = Snake()


    d, bilde, radius, center = f.FindObsInPath()
