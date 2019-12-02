"""
Checks for obstacles in the view of the front-facing camera

author: Håkon Bjerkgaard Waldum, Ruben Svedal Jørundland, Marcus Olai Grindvik
"""

import cv2
import numpy as np
from Python.Movement.snake import Snake


class CheckPathForObst:

    def __init__(self):
        pass

    def findObsInPath(self, picture):
        """
        Requests a picture from the front-facing camera, and checks if a given amount of the pixels are non-white.
        :param picture: picture from the front-facing camera
        :return:True if obstacle in path, False if not
        """
        try:
            threshold = (picture.shape[0] * picture.shape[1] * 255) / 2
            picture = cv2.cvtColor(picture, cv2.COLOR_RGB2BGR)
            notWhiteLower = (0, 40, 0)
            notWhiteUpper = (255, 255, 255)

            blurred = cv2.GaussianBlur(picture, (11, 11), 0)
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
    f = CheckPathForObst()
    s = Snake("http://192.168.137.102", "192.168.137.167")
    s.setFrameSize(7)
    bilde = s.takePicture()
    smart = f.findObsInPath(bilde)
    print(smart)
