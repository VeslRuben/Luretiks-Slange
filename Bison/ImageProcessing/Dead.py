import glob

import cv2
import numpy as np
from Bison.ImageProcessing.camera import Camera
import os


class Dead:

    def getDeadEnds2(self, bilde):
        # img_rgb = cv2.imread(r"C:\Users\marcu\PycharmProjects\Luretriks-Slange\Pictures\DeadEnds\perf2.jpg")
        img_rgb = bilde
        img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)
        img_cannyre = cv2.Canny(img_gray, 50, 120, apertureSize=3)

        path = os.getcwd() + "\\" + "..\\..\\Pictures\\DeadEnds2/*.PNG"

        filenames = [img for img in glob.glob(path)]

        templateList = []
        for img in filenames:
            n = cv2.imread(img, 0)
            templateList.append(n)

        threshold = 0.80

        # loc = np.where( res4 >= threshold)# and np.where(res1 >= threshold) and np.where(res2 >= threshold) and np.where(res3 >= threshold)

        # loop over the scales of the image
        loc = []
        WH = []
        for temp in templateList:

            res = cv2.matchTemplate(img_gray, temp, cv2.TM_CCOEFF_NORMED)
            res = np.where(res >= threshold)
            if res:
                loc.append(res)
                w, h = temp.shape[::-1]
                WH.append([w, h])
            # loc.append(np.where( res >= threshold))

        lastPt = 0
        lastPt2 = 0
        deadEnds = []

        for point, WH in zip(loc, WH):
            w, h = WH
            for pt in zip(*point[::-1]):
                """low = (int(pt[0])-100)
                high = (int(pt[0])+100)
                low2 = (int(pt[1]) - 100)
                high2 = (int(pt[1]) + 100)"""
                deadEnds.append([pt[0] + w / 2, pt[1] + h / 2])
                """
                if low <= lastPt <= high and low2 <= lastPt2 <= high2 :
                    break
                else:
                    
                    lastPt = int(pt[0])
                    lastPt2 = int(pt[1])
                    cv2.rectangle(img_rgb, pt, (pt[0] + w, pt[1] + h), (0,0,255), 2)"""

        tempDeadEnds = []
        for i in range(len(deadEnds)):
            apApend = True
            if i == len(deadEnds):
                break
            else:

                for j in range(i + 1, len(deadEnds)):
                    if (abs(deadEnds[i][0] - deadEnds[j][0]) <= 100 and abs(deadEnds[i][1] - deadEnds[j][1]) <= 100):
                        apApend = False
                        break
            if apApend:
                tempDeadEnds.append(deadEnds[i])
        deadEnds = tempDeadEnds

        for point in deadEnds:
            cv2.circle(img_rgb, (int(point[0]), int(point[1])), 10, (255, 0, 255), 3)

        cv2.imshow("img", img_rgb)

        cv2.waitKey()
        return deadEnds, img_rgb


if __name__ == "__main__":
    c = Camera()
    c.initCam(0)
    bilde = c.takePicture()
    # bilde = cv2.imread(os.getcwd() + "\\" + "..\\..\\Pictures\\DeadEnds\\perf2.jpg")
    c = Dead()
    c.getDeadEnds2(bilde)
