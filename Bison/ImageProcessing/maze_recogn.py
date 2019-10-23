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
        #hsv = cv2.cvtColor(picture, cv2.COLOR_BGR2HSV)

        #lower_blue = np.array([110, 50, 50])
        #upper_blue = np.array([140, 255, 255])
        #mask = cv2.inRange(hsv, lower_blue, upper_blue)

        #picture[mask != 0] = [153, 149, 160]

        #cv2.imshow("Test", cv2.resize(picture, (1280, 720)))

        grayfilt = cv2.cvtColor(picture, cv2.COLOR_BGR2GRAY)
        grayfilt = cv2.GaussianBlur(grayfilt, (5, 5), 0)

        edges = cv2.Canny(grayfilt, 120, 180, apertureSize=3)
        edges = cv2.dilate(edges, None, iterations=7)
        edges = cv2.erode(edges, None, iterations=5)

        return edges

    def runshit(self):
        pic = cv2.imread(
            'C:\\Users\\h_wal\\OneDrive\\Documents\\Automatiseringsteknikk 3\\Mekatronikk\\Luretriks-Slange\\Pictures\\jallabilde1.jpg',
            -1)

        pic2 = cv2.imread(
            'C:\\Users\\h_wal\\OneDrive\\Documents\\Automatiseringsteknikk 3\\Mekatronikk\\Luretriks-Slange\\Pictures\\jall2.jpg',
            -1)

        edges1 = self.filtering(pic)

        edges2 = self.filtering(pic2)

        lines2 = cv2.HoughLinesP(edges2, 1, np.pi / 300, 110)

        for data in lines2:
            x1 = data[0][0]
            y1 = data[0][1]
            x2 = data[0][2]
            y2 = data[0][3]

            cv2.line(pic2, (x1, y1), (x2, y2), (0,255,0), 2)

        cv2.imwrite('linjebilde2.jpg', pic2)

        while(stillPic):
            cv2.imshow("Picture", cv2.resize(pic, (1280, 720)))
            cv2.imshow("Picture2", cv2.resize(pic2, (1280, 720)))
            cv2.imshow("Filtered", cv2.resize(edges1, (1280, 720)))
            cv2.imshow("Filtered2", cv2.resize(edges2, (1280, 720)))

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        while (realtime):
            _, frame = cap.read()

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            gray = cv2.GaussianBlur(gray, (7, 7), 0)

            edges = cv2.Canny(gray, 100, 180, apertureSize=3)
            edges = cv2.dilate(edges, None, iterations=1)
            edges = cv2.erode(edges, None, iterations=1)

            # print(coord_list[0])

            # if not plotted:
            #    for x, y in coord_list:
            ##        plt.plot(x,y)
            #   plt.show()
            #   plotted = True

            cv2.imshow("Frame", frame)
            cv2.imshow("Gray", np.hstack([gray, edges]))

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()

        return lines2

