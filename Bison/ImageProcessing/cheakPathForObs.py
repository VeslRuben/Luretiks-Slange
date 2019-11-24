import cv2
import numpy as np
from Bison.Movement.Snake import Snake


class cheakPathForObs:

    def __init__(self):
        pass

    def FindObsInPath(self, bilde):
        """
        Trashold find a int that represents if half the image is white
        Then the image gets blurred with gaussianblur
        Then the image gets changed to Hsv
        Then color thrasholds out every thing that is white.
        then som filtering
        cheks if half the image is coverd
        returs if the image have a object infront of it or not
        :param bilde:
        :return:
        """
        try:
            threshold = (bilde.shape[0] * bilde.shape[1] * 255) / 2
            bilde = cv2.cvtColor(bilde, cv2.COLOR_RGB2BGR)
            notWhiteLower = (0, 60, 0)
            notWhiteUpper = (255, 255, 255)

            blurred = cv2.GaussianBlur(bilde, (11, 11), 0)
            color = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)
            mask = cv2.inRange(color, notWhiteLower, notWhiteUpper)
            mask = cv2.dilate(mask, None, iterations=3)
            mask = cv2.erode(mask, None, iterations=3)
            mask = np.array(mask)

            if np.sum(mask) > threshold:
                return True
            else:
                return False
        except AttributeError:
            return False


if __name__ == "__main__":
    f = cheakPathForObs()
    s = Snake("http://192.168.137.102", "192.168.137.167")
    s.setFrameSize(7)
    bilde = s.takePicture()
    smart = f.FindObsInPath(bilde)
    print(smart)
