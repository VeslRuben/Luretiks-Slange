import math

class SnakeController:

    def __init__(self):

        self.curantAngle = 0

    def ccw(self, A, B, C):
        return (C[1] - A[1]) * (B[0] - A[0]) > (B[1] - A[1]) * (C[0] - A[0])

    # Return true if line segments AB and CD intersect
    def intersect(self, A, B, C, D):
        return self.ccw(A, C, D) != self.ccw(B, C, D) and self.ccw(A, B, C) != self.ccw(A, B, D)

    def calculatTurnAngel(self, lV, lVxsV, snakeEndPoint, lineStartPoint, P):
        # usiing distans to line to regulate#########
        lVN = [lV[1], -lV[0]]
        starSnakeVektor = [snakeEndPoint[0] - lineStartPoint[0], snakeEndPoint[1] - lineStartPoint[1]]
        distSnakToLine = abs(lVN[0] * starSnakeVektor[0] + lVN[1] * starSnakeVektor[1]) / math.sqrt(
            lVN[0] ** 2 + lVN[1] ** 2)
        distSnakToLine = distSnakToLine * (lVxsV / abs(lVxsV))  # (lVxsV / abs(lVxsV)) is 1 or -1
        self.curantAngle = self.curantAngle + int(distSnakToLine * P)
        return self.curantAngle

    def calculateLineVektors(self, lineStartPoint, lineEndPoint, snakeStartPoint, snakeEndPoint):
        lV = [lineEndPoint[0] - lineStartPoint[0], lineEndPoint[1] - lineStartPoint[1]]
        sV = [snakeEndPoint[0] - snakeStartPoint[0], snakeEndPoint[1] - snakeStartPoint[1]]
        lVxsV = lV[0] * sV[1] - lV[1] * sV[0]
        return lV, sV, lVxsV

    def calculateTlheta(self, lV, sV, lVxsV):
        theta = math.acos((lV[0] * sV[0] + lV[1] * sV[1]) / (
                math.sqrt(lV[0] ** 2 + lV[1] ** 2) * math.sqrt(sV[0] ** 2 + sV[1] ** 2)))
        theta = (theta * (lVxsV / abs(lVxsV))) * 180 / math.pi  # (lVxsV / abs(lVxsV)) is 1 or -1
        self.curantAngle = self.curantAngle + int(theta * 0.3)
        return self.curantAngle

    def calculateLines(self, lV, sV, LineEndoPoint, snakeEndPoint):
        finithVektor = [lV[1], -lV[0]]
        skalar = 10
        finithLine = [[LineEndoPoint[0] + (finithVektor[0] * skalar), LineEndoPoint[1] + (finithVektor[1] * skalar)],
                      [LineEndoPoint[0] + (-finithVektor[0] * skalar), LineEndoPoint[1] + (-finithVektor[1] * skalar)]]
        snakLine = [snakeEndPoint, [snakeEndPoint[0] + (-sV[0]) * 2, snakeEndPoint[1] + (-sV[1]) * 2]]
        return snakLine, finithLine

    def run(self):
        pass





"""     start = self.finalPath[self.i]
        nextNode = self.finalPath[self.i + 1]
        lV = [nextNode[0] - start[0], nextNode[1] - start[1]]

        # Take piture ####################################################################
        pic = self.cam.takePicture()
        # snakeCords, maskPic = self.findSnake.LocateSnake(pic)
        cordList = []
        snakeCords, maskPic = self.findSnake.LocateSnakeAverage(1, 3, False)

        #################################################################################

        # Draw Picture for GUI ###########################################################
        maskPic = drawLines(maskPic, self.finalPath, (255, 0, 0))
        collorPic = drawLines(pic, self.finalPath, (255, 0, 0))
        if snakeCords is not None:
            self.traveledPath.append(snakeCords[1])
        if len(self.traveledPath) > 1:
            maskPic = drawLines(maskPic, self.traveledPath, (0, 255, 0))

        self.notifyGui("UpdateImageEventL", maskPic)
        self.notifyGui("UpdateImageEventR", collorPic)
        ##################################################################################

        if snakeCords is not None:
            s0 = snakeCords[0]
            s1 = snakeCords[1]
            sV = [s1[0] - s0[0], s1[1] - s0[1]]
            lVxsV = lV[0] * sV[1] - lV[1] * sV[0]
            theta = math.acos((lV[0] * sV[0] + lV[1] * sV[1]) / (
                    math.sqrt(lV[0] ** 2 + lV[1] ** 2) * math.sqrt(sV[0] ** 2 + sV[1] ** 2)))
            theta = (theta * (lVxsV / abs(lVxsV))) * 180 / math.pi  # (lVxsV / abs(lVxsV)) is 1 or -1

            finithVektor = [lV[1], -lV[0]]
            skalar = 10
            finithLine = [[nextNode[0] + (finithVektor[0] * skalar), nextNode[1] + (finithVektor[1] * skalar)],
                          [nextNode[0] + (-finithVektor[0] * skalar), nextNode[1] + (-finithVektor[1] * skalar)]]
            snakLine = [s1, [s1[0] + (-sV[0]) * 2, s1[1] + (-sV[1]) * 2]]

            # Using Angle betwen wktors to regulate######
            #self.curantAngle = self.curantAngle + int(theta * 0.3)
            #self.snake.turn(self.curantAngle)

            # self.notifyGui("UpdateTextEvent", f"Theta {theta}")

            # usiing distans to line to regulate#########
            lVN = [lV[1], -lV[0]]
            starSnakeVektor = [s1[0] - start[0], s1[1] - start[1]]
            distSnakToLine = abs(lVN[0] * starSnakeVektor[0] + lVN[1] * starSnakeVektor[1]) / math.sqrt(
                lVN[0] ** 2 + lVN[1] ** 2)
            distSnakToLine = distSnakToLine * (lVxsV / abs(lVxsV))  # (lVxsV / abs(lVxsV)) is 1 or -1
            self.curantAngle = self.curantAngle + int(distSnakToLine * 0.5)
            self.snake.turn(self.curantAngle)

            self.notifyGui("UpdateTextEvent", f"angel of snake {self.curantAngle}")
            self.notifyGui("UpdateTextEvent", f"dist {distSnakToLine}")

            if self.intersect(finithLine[0], finithLine[1], snakLine[0], snakLine[1]):
                self.i += 1

        if self.i >= len(self.finalPath) - 1:
            self.snake.stop()
            print("stop")
            with b.lock:
                b.yoloFlag = False
                self.i = 0
        time.sleep(0.1)"""