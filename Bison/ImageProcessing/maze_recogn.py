import os
import numpy as np
import cv2
import time

realtime = False
stillPic = False

cap = cv2.VideoCapture(1)
time.sleep(0.01)

plotted = False


class mazeRecognizer:

    def __init__(self):
        pass

    def filtering(self, picture):
        grayfilt = cv2.cvtColor(picture, cv2.COLOR_BGR2GRAY)
        grayfilt = cv2.GaussianBlur(grayfilt, (7, 7), 0)

        edges = cv2.Canny(grayfilt, 120, 150, apertureSize=3)
        edges = cv2.dilate(edges, None, iterations=8)
        edges = cv2.erode(edges, None, iterations=7)
        kernel = np.ones((21, 21), np.uint8)
        edges = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)

        return edges

    def runshit(self):
        pic2 = cv2.imread(
            os.getcwd() + "\\" + "..\\Pictures/test2jallball.jpg",
            -1)

        edges2 = self.filtering(pic2)

        lines2 = cv2.HoughLinesP(edges2, 1, np.pi / 1000, 85, maxLineGap=10, minLineLength=40)

        for data in lines2:
            x1 = data[0][0]
            y1 = data[0][1]
            x2 = data[0][2]
            y2 = data[0][3]

            cv2.line(pic2, (x1, y1), (x2, y2), (0, 255, 0), 2)

        cv2.imwrite('linjebilde2.jpg', pic2)

        while stillPic:
            cv2.imshow("Picture2", cv2.resize(pic2, (1280, 720)))
            cv2.imshow("Filtered2", cv2.resize(edges2, (1280, 720)))

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        while realtime:
            _, frame = cap.read()

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            gray = cv2.GaussianBlur(gray, (7, 7), 0)

            edges = cv2.Canny(gray, 100, 180, apertureSize=3)
            edges = cv2.dilate(edges, None, iterations=1)
            edges = cv2.erode(edges, None, iterations=1)

            cv2.imshow("Frame", frame)
            cv2.imshow("Gray", np.hstack([gray, edges]))

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()

        return lines2, cv2.resize(pic2, (800, 600))
