import compare as compare
import cv2
import numpy as np
from Bison.ImageProcessing.camera import Camera
import matplotlib.pyplot as plt
from Bison.ImageProcessing.maze_recogn import mazeRecognizer
import  math



class DetectDeadEnds:

    def __init__(self):

        pass

    def getDeadEnds(self, frame):

        bilde = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        blurred = cv2.GaussianBlur(bilde, (9, 9), 0)
        canny = cv2.Canny(blurred,50, 120, apertureSize=3)

        cannyD = cv2.dilate(canny, None, iterations=2)
        cv2.imshow("canny", cannyD)
        corners = cv2.goodFeaturesToTrack(cannyD,maxCorners=40, qualityLevel = 0.60,minDistance = 20, blockSize = 50 )


        xlist = []
        ylist = []
        XYList = []
        corners = corners.tolist()
        for i in corners:
            x, y = i[0]
            xlist.append(x)
            ylist.append(y)

            XYList.append(i[0])

        listOfCordinates = []


        for i in range(len(XYList)):
            for j in range(i + 1, len(XYList)):

                x , y = XYList[i]
                x2 , y2 = XYList[j]

                dist = math.sqrt((x-x2)**2+(y-y2)**2)
                if(dist < 150 and dist>50):
                    listOfCordinates.append([XYList[i],XYList[j]])





        plt.imshow(bilde), plt.show()
        cv2.waitKey()




















if __name__ == "__main__":
    frame = cv2.imread(r'C:\Users\marcu\PycharmProjects\Luretriks-Slange\Pictures\perf.jpg')
    c = DetectDeadEnds()
    c.getDeadEnds(frame)
