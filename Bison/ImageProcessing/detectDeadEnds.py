import cv2
import os
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

        cv2.imshow("start", frame)

        bilde = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        blurred = cv2.GaussianBlur(bilde, (9, 9), 0)
        canny = cv2.Canny(blurred,50, 120, apertureSize=3)

        cannyD = cv2.dilate(canny, None, iterations=2)
        cv2.imshow("canny", cannyD)
        corners = cv2.goodFeaturesToTrack(cannyD,maxCorners=100, qualityLevel=0.50, minDistance=20, blockSize=70)


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
            cv2.line(bilde, (x,y), (x,y), (0, 255, 0), 2)

        listOfCordinates = []


        for i in range(len(XYList)):
            for j in range(i + 1, len(XYList)):

                x , y = XYList[i]
                x2 , y2 = XYList[j]

                dist = math.sqrt((x-x2)**2+(y-y2)**2)
                if(dist < 150 and dist>50):
                    listOfCordinates.append([XYList[i],XYList[j]])


        print(listOfCordinates[0][0])

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
                if obst.intersects(line):
                    print('Crash')
                else:
                    tempLineList.append([[lx1, ly1], [lx2, ly2]])

        for coords in tempLineList:
            lx1 = coords[0][0]
            ly1 = coords[0][1]
            lx2 = coords[1][0]
            ly2 = coords[1][1]
            cv2.line(bilde, (int(lx1), int(ly1)), (int(lx2), int(ly2)), (0, 0, 255), 2)

        print(tempLineList)
        plt.imshow(bilde), plt.show()
        cv2.waitKey()


if __name__ == "__main__":
    m = mazeRecognizer()

    frame = cv2.imread(os.getcwd() + "\\" + "..\\..\\Pictures/perf.jpg")

    lines, _ = m.findMaze()
    c = DetectDeadEnds()
    c.getDeadEnds(frame, lines)
