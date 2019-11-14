import cv2
import numpy as np
from matplotlib import pyplot as plt
import imutils
from shapely.geometry import LineString
from Bison.ImageProcessing.camera import Camera
import os


class Dead:

    def getDeadEnds2(self, bilde):
        # img_rgb = cv2.imread(r"C:\Users\marcu\PycharmProjects\Luretriks-Slange\Pictures\DeadEnds\perf2.jpg")
        img_rgb = bilde
        img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)
        img_cannyre = cv2.Canny(img_gray, 50, 120, apertureSize=3)

        path = os.getcwd()+ "\\" + "..\\..\\Pictures\\DeadEnds/"
        template = cv2.imread(path + "DeadEnd1.PNG", 0)
        template2 = cv2.imread(path + "DeadEnd2.PNG", 0)
        template3 = cv2.imread(path + "DeadEnd3.PNG", 0)
        template4 = cv2.imread(path + "DeadEnd4.PNG", 0)
        template5 = cv2.imread(path + "DeadEnd5.PNG", 0)
        template6 = cv2.imread(path + "DeadEnd6.PNG", 0)
        template7 = cv2.imread(path + "DeadEnd7.PNG", 0)
        template8 = cv2.imread(path + "DeadEnd8.PNG", 0)
        template9 = cv2.imread(path + "DeadEnd9.PNG", 0)
        template10 = cv2.imread(path + "DeadEnd10.PNG", 0)
        template11 = cv2.imread(path + "DeadEnd11.PNG", 0)
        template12 = cv2.imread(path + "DeadEnd12.PNG", 0)
        template13 = cv2.imread(path + "DeadEnd13.PNG", 0)
        template14 = cv2.imread(path + "DeadEnd14.PNG", 0)
        template15 = cv2.imread(path + "DeadEnd15.PNG", 0)
        template16 = cv2.imread(path + "DeadEnd16.PNG", 0)
        template17 = cv2.imread(path + "DeadEnd17.PNG", 0)
        template18 = cv2.imread(path + "DeadEnd18.PNG", 0)
        template19 = cv2.imread(path + "DeadEnd19.PNG", 0)
        template20 = cv2.imread(path + "DeadEnd20.PNG", 0)
        template21 = cv2.imread(path + "DeadEnd21.PNG", 0)
        template22 = cv2.imread(path + "DeadEnd22.PNG", 0)
        """img_canny2 = cv2.Canny(template2, 50, 120, apertureSize=3)
        img_canny3 = cv2.Canny(template3, 50, 120, apertureSize=3)
        img_canny4 = cv2.Canny(template4, 50, 120, apertureSize=3)
        img_canny5 = cv2.Canny(template5, 50, 120, apertureSize=3)
        img_canny6 = cv2.Canny(template6, 50, 120, apertureSize=3)
        img_canny7 = cv2.Canny(template7, 50, 120, apertureSize=3)"""

        templateList = []
        """templateList.append(img_canny)
        templateList.append(img_canny2)
        templateList.append(img_canny3)
        templateList.append(img_canny4)
        templateList.append(img_canny5)
        templateList.append(img_canny6)
        templateList.append(img_canny7)"""

        templateList.append(template)
        templateList.append(template2)
        templateList.append(template3)
        templateList.append(template4)
        templateList.append(template5)
        templateList.append(template6)
        templateList.append(template7)
        templateList.append(template8)
        templateList.append(template9)
        templateList.append(template10)
        templateList.append(template11)
        templateList.append(template12)
        templateList.append(template13)
        templateList.append(template14)
        templateList.append(template15)
        templateList.append(template16)
        templateList.append(template17)
        templateList.append(template18)
        templateList.append(template19)
        templateList.append(template20)
        templateList.append(template21)
        templateList.append(template22)

        w, h = template.shape[::-1]

        """res = cv2.matchTemplate(img_gray,template,cv2.TM_CCOEFF_NORMED)
        res1 = cv2.matchTemplate(img_gray,template2,cv2.TM_CCOEFF_NORMED)
        res2 = cv2.matchTemplate(img_gray,template3,cv2.TM_CCOEFF_NORMED)
        res3 = cv2.matchTemplate(img_gray,template4,cv2.TM_CCOEFF_NORMED)
        res4 = cv2.matchTemplate(img_gray,template5,cv2.TM_CCOEFF_NORMED)
        res5 = cv2.matchTemplate(img_gray,template6,cv2.TM_CCOEFF_NORMED)"""
        threshold = 0.85

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
            cv2.circle(img_rgb, (int(point[0]), int(point[1])),10,(255,0,255), 3)

        cv2.imshow("img", img_rgb)

        cv2.waitKey()
        return deadEnds, img_rgb

if __name__ == "__main__":
    c = Camera()
    c.initCam(1)
    bilde = c.takePicture()
    c = Dead()
    c.getDeadEnds2(bilde)
