import cv2
import numpy as np
from Python.ImageProcessing.camera import Camera
import imutils


class FindSnake:

    def __init__(self):
        pass

    def locateSnake(self, frame):

        greenLower = np.array([42, 0, 0], dtype=np.uint8)
        greenUpper = np.array([83, 255, 255], dtype=np.uint8)

        redLower = np.array([100, 170, 20], dtype=np.uint8)
        redUpper = np.array([140, 255, 240], dtype=np.uint8)

        blueLower = np.array([100, 150, 0], dtype=np.uint8)
        blueUpper = np.array([140, 255, 255], dtype=np.uint8)

        lowerWhite = np.array([0, 0, 180], dtype=np.uint8)
        upperWhite = np.array([145, 60, 255], dtype=np.uint8)

        blurred = cv2.GaussianBlur(frame, (7, 7), 0)
        color1 = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)
        maskB = cv2.inRange(color1, blueLower, blueUpper)
        maskG = cv2.inRange(color1, greenLower, greenUpper)
        maskG = cv2.erode(maskG, None, iterations=3)
        maskG = cv2.dilate(maskG, None, iterations=3)

        color2 = cv2.cvtColor(blurred, cv2.COLOR_RGB2HSV)
        maskR = cv2.inRange(color2, redLower, redUpper)
        maskR = cv2.erode(maskR, None, iterations=1)
        maskR = cv2.dilate(maskR, None, iterations=6)

        maskW = cv2.inRange(color1, lowerWhite, upperWhite)
        cnts = cv2.findContours(maskG, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cnts = imutils.grab_contours(cnts)

        cnts1 = cv2.findContours(maskR, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cnts1 = imutils.grab_contours(cnts1)
        try:
            M1 = cv2.moments(cnts1[0])
            x1 = int(M1["m10"] / M1["m00"])
            y1 = int(M1["m01"] / M1["m00"])
            cv2.circle(maskR, (x1, y1), 7, (255, 255, 0), -1)

            M = cv2.moments(cnts[0])
            x0 = int(M["m10"] / M["m00"])
            y0 = int(M["m01"] / M["m00"])
            cv2.circle(maskG, (x0, y0), 7, (255, 255, 0), -1)
            return [[x0, y0], [x1, y1]], cv2.cvtColor(maskG + maskR, cv2.COLOR_GRAY2RGB)
        except ZeroDivisionError as e:
            return None, cv2.cvtColor(maskG + maskR, cv2.COLOR_GRAY2RGB)
        except IndexError as e:
            return None, cv2.cvtColor(maskG + maskR, cv2.COLOR_GRAY2RGB)

    def average(self, values: list, filterExtream=False) -> float:
        if filterExtream and len(values) > 2:
            minimum = min(values)
            values.remove(minimum)
            maximum = max(values)
            values.remove(maximum)
        return sum(values) / len(values)

    def locateSnakeAverage(self, iterations: int, average: int = 1, filterExtreme=False, picture=None):

        cam = Camera()

        greenLower = np.array([42, 0, 0], dtype=np.uint8)
        greenUpper = np.array([83, 255, 255], dtype=np.uint8)

        redLower = np.array([100, 170, 20], dtype=np.uint8)
        redUpper = np.array([140, 255, 240], dtype=np.uint8)

        purpleLower = np.array([145, 70, 30])
        purpleHigher = np.array([170, 255, 190])

        if average < 1:
            average = 1

        cordList = [[], [], [], [], [], []]
        mask = None

        for laps in range(average):

            greenFrames = []
            redFrames = []
            purpleFrames = []

            for i in range(iterations):
                if picture is not None and iterations == 1 and average == 1:
                    frame = picture
                else:
                    frame = cam.takePicture()

                blurred = cv2.GaussianBlur(frame, (7, 7), 0)
                hsvFrame = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)  # From RGB
                maskG = cv2.inRange(hsvFrame, greenLower, greenUpper)
                greenFrames.append(maskG)

                hsvFrame2 = cv2.cvtColor(blurred, cv2.COLOR_RGB2HSV)  # From BGR
                maskR = cv2.inRange(hsvFrame2, redLower, redUpper)
                redFrames.append(maskR)

                maskBP = cv2.inRange(hsvFrame, purpleLower, purpleHigher)
                purpleFrames.append(maskBP)

            greenSum = greenFrames.pop(0)
            if greenFrames:
                for greenFrame in greenFrames:
                    greenSum = greenSum + greenFrame

            redSum = redFrames.pop(0)
            if redFrames:
                for readFram in redFrames:
                    redSum = redSum + readFram

            purpleSum = purpleFrames.pop(0)
            if purpleFrames:
                for purpleFrame in purpleFrames:
                    purpleSum = purpleSum + purpleFrame

            redMask = cv2.erode(redSum, None, iterations=2)
            redMask = cv2.dilate(redMask, None, iterations=3)

            greenMask = cv2.erode(greenSum, None, iterations=4)
            greenMask = cv2.dilate(greenMask, None, iterations=4)

            purpleMask = cv2.erode(purpleSum, None, iterations=2)
            purpleMask = cv2.dilate(purpleMask, None, iterations=5)

            mask = greenMask + redMask

            greenCnts = cv2.findContours(greenMask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            greenCnts = imutils.grab_contours(greenCnts)

            redCnts = cv2.findContours(redMask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            redCnts = imutils.grab_contours(redCnts)

            purpleCnts = cv2.findContours(purpleMask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            purpleCnts = imutils.grab_contours(purpleCnts)

            x0 = x1 = y0 = y1 = x3 = y3 = None

            if redCnts:
                M = cv2.moments(redCnts[0])
                x1 = int(M["m10"] / M["m00"])
                y1 = int(M["m01"] / M["m00"])

            if greenCnts:
                M1 = cv2.moments(greenCnts[0])
                x0 = int(M1["m10"] / M1["m00"])
                y0 = int(M1["m01"] / M1["m00"])

            if purpleCnts:
                M2 = cv2.moments(purpleCnts[0])
                x3 = int(M2["m10"] / M2["m00"])
                y3 = int(M2["m01"] / M2["m00"])

            if x0 is not None and x1 is not None and y0 is not None and y1 is not None:
                cordList[0].append(x0)
                cordList[1].append(y0)
                cordList[2].append(x1)
                cordList[3].append(y1)
                # cordList[4].append(x3)
                # cordList[5].append(y3)

        if len(cordList[0]) < 3:
            filterExtreme = False

        if cordList[0]:
            x0 = self.average(cordList[0], filterExtreme)
            y0 = self.average(cordList[1], filterExtreme)
            x1 = self.average(cordList[2], filterExtreme)
            y1 = self.average(cordList[3], filterExtreme)
            # x3 = self.average(cordList[4], filterExtream)
            # y3 = self.average(cordList[5], filterExtream)
            return [[x0, y0], [x1, y1]], cv2.cvtColor(mask, cv2.COLOR_GRAY2RGB)
        else:
            return None, cv2.cvtColor(mask, cv2.COLOR_GRAY2RGB)


if __name__ == "__main__":
    cam = Camera()
    Camera.initCam(0)
    c = FindSnake()

    try:
        while True:
            cord, yolo = c.locateSnakeAverage(1, 1, False)
            cv2.imshow("swag", yolo)
            cv2.waitKey(10)

    finally:
        cv2.destroyAllWindows()
