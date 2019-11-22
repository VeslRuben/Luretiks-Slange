import cv2
import numpy as np
from Bison.ImageProcessing.camera import Camera
import matplotlib.pyplot as plt
from Bison.ImageProcessing.maze_recogn import mazeRecognizer
import math
from shapely.geometry import LineString


class DetectDeadEnds:

    def __init__(self):

        pass

    def getDeadEnds(self, frame, lineList):

        bilde = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        # blurred = cv2.GaussianBlur(bilde, (9, 9), 0)
        bilde = cv2.dilate(bilde, None, iterations=6)
        skel = np.zeros(bilde.shape, np.uint8)
        size = np.size(bilde)
        ret, img = cv2.threshold(bilde, 128, 255, 0)
        element = cv2.getStructuringElement(cv2.M, (3, 3))
        done = False

        while (not done):
            eroded = cv2.erode(img, element)
            temp = cv2.dilate(eroded, element)
            temp = cv2.subtract(img, temp)
            skel = cv2.bitwise_or(skel, temp)
            img = eroded.copy()

            zeros = size - cv2.countNonZero(img)
            if zeros == size:
                done = True

        #canny = cv2.Canny(bilde, 50, 120, apertureSize=3)
        #cannyD = cv2.dilate(canny, None, iterations=2)
       #cannyE = cv2.erode(cannyD, None, iterations=3)
        cv2.imshow("cannyD", skel)
        cv2.waitKey()
        corners = cv2.goodFeaturesToTrack(skel, maxCorners=300, qualityLevel=0.4, minDistance=5, blockSize=70)

        xlist = []
        ylist = []
        XYList = []
        corners = corners.tolist()
        for i in corners:
            x, y = i[0]
            x = int(x)
            y = int(y)
            xlist.append(x)
            ylist.append(y)

            XYList.append(i[0])
            cv2.line(skel, (int(x), int(y)), (int(x), int(y)), (203, 192, 255), 2)
        plt.imshow(skel), plt.show()
        listOfCordinates = []

        for i in range(len(XYList)):
            for j in range(i + 1, len(XYList)):

                x, y = XYList[i]
                x2, y2 = XYList[j]

                dist = math.sqrt((x - x2) ** 2 + (y - y2) ** 2)
                if (dist < 150 and dist > 50):
                    listOfCordinates.append([XYList[i], XYList[j]])

        tempLineList = []

        for coordinateData in listOfCordinates:
            lx1 = coordinateData[0][0]
            ly1 = coordinateData[0][1]
            lx2 = coordinateData[1][0]
            ly2 = coordinateData[1][1]
            line = LineString([(lx1, ly1), (lx2, ly2)])
            for data in lineList:
                x1 = data[0][0]
                y1 = data[0][1]
                x2 = data[0][2]
                y2 = data[0][3]
                obst = LineString([(x1, y1), (x2, y2)])
                if not obst.intersects(line):
                    tempLineList.append([[lx1, ly1], [lx2, ly2]])



        print(tempLineList)
        for coords in tempLineList:
            lx1 = coords[0][0]
            ly1 = coords[0][1]
            lx2 = coords[1][0]
            ly2 = coords[1][1]
            cv2.line(bilde, (int(lx1), int(ly1)), (int(lx2), int(ly2)), (50, 0, 255), 2)

        plt.imshow(bilde), plt.show()
        cv2.waitKey()
        print("ferdig")


if __name__ == "__main__":
    m = mazeRecognizer()
    c = Camera()
    c.initCam(1)
    frame = c.takePictureRgb()
    #frame = cv2.imread(r"C:\Users\marcu\PycharmProjects\Luretriks-Slange\Pictures\perf.jpg")
    lines, _ = m.findMaze()
    c = DetectDeadEnds()
    c.getDeadEnds(frame, lines)
