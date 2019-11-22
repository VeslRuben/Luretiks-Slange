import cv2
import numpy as np
import imutils
from scipy.spatial import distance as dist
from Bison.Movement.Snake import Snake


class cheakPathForObs:

    def __init__(self):
        pass

    def FindObsInPath(self, bilde):
        tashHold = 61200000
        bilde = cv2.cvtColor(bilde, cv2.COLOR_RGB2BGR)
        notWhiteLower = (0, 60, 0)
        notWhiteUpper = (255, 255, 255)
        yelowLower = (20, 100, 100)
        yellowHiger = (30, 255, 255)

        blurred = cv2.GaussianBlur(bilde, (11, 11), 0)
        color = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(color, notWhiteLower, notWhiteUpper)
        mask = cv2.dilate(mask, None, iterations=3)
        mask = cv2.erode(mask, None, iterations=3)
        mask = np.array(mask)
        if np.sum(mask) > tashHold:
            print(np.sum(mask))
            return "marcus ER SMART"





if __name__ == "__main__":
    f = cheakPathForObs()
    s = Snake("http://192.168.137.102", "192.168.137.167")
    s.setFrameSize(7)
    bilde = s.takePicture()
    smart = f.FindObsInPath(bilde)
    print(smart)
