import math
from shapely.geometry import LineString, Point


class SnakeController:

    def __init__(self):
        self.currentAngle = 0

    def ccw(self, A, B, C):
        """
        I have noe idea
        :param A:
        :param B:
        :param C:
        :return:
        """
        return (C[1] - A[1]) * (B[0] - A[0]) > (B[1] - A[1]) * (C[0] - A[0])

    # Return true if line segments AB and CD intersect
    def intersect(self, A, B, C, D):
        """
        Makes two lines from coordinates, AB and CD.
        Checks if these lines intersect.
        :param A: x1
        :param B: y1
        :param C: x2
        :param D: y2
        :return: True if intersect, False if no intersect
        """
        return self.ccw(A, C, D) != self.ccw(B, C, D) and self.ccw(A, B, C) != self.ccw(A, B, D)

    def calculateLineVectors(self, lineStartPoint, lineEndPoint, snakeStartPoint, snakeEndPoint):
        """
        Calculates line vectors for path and snake
        :param lineStartPoint: (x,y) for path start
        :param lineEndPoint:  (x,y) for path end
        :param snakeStartPoint: (x,y) for snakes end
        :param snakeEndPoint: (x,y) for snakes front
        :return: line vectors as well as cross product
        """
        lV = [lineEndPoint[0] - lineStartPoint[0], lineEndPoint[1] - lineStartPoint[1]]
        sV = [snakeEndPoint[0] - snakeStartPoint[0], snakeEndPoint[1] - snakeStartPoint[1]]
        lVxsV = lV[0] * sV[1] - lV[1] * sV[0]
        return lV, sV, lVxsV

    def calculateTheta(self, lV, sV, lVxsV):
        """
        Calculates the angle between two vectors
        :param lV: path vector
        :param sV: snake vector
        :param lVxsV: Cross product between them
        :return: the angle between them
        """
        theta = math.acos((lV[0] * sV[0] + lV[1] * sV[1]) / (
                math.sqrt(lV[0] ** 2 + lV[1] ** 2) * math.sqrt(sV[0] ** 2 + sV[1] ** 2)))
        try:
            theta = (theta * (lVxsV / abs(lVxsV))) * 180 / math.pi  # (lVxsV / abs(lVxsV)) is 1 or -1
        except ZeroDivisionError:
            theta = 0
        return theta

    def calculateFirstTurnAngle(self, lV, sV, lVxsV):
        """
        Calculates the first turn angle for the snake.
        :param lV: path vector
        :param sV: snake vector
        :param lVxsV: cross product between them
        :return: the angle to turn
        """
        theta = self.calculateTheta(lV, sV, lVxsV)
        self.currentAngle = self.currentAngle + int(theta * 0.3)
        return self.currentAngle

    def calculatDistanceToLine(self, lV, snakeEndPoint, lineStartPoint):
        """
        Calculates distance between the front of the snake and the path line
        :param lV: path vector
        :param snakeEndPoint: coordinates for the snakes front
        :param lineStartPoint: (x,y) for the paths start
        :return: the distance between the snakes front and the path vector in pixels
        """
        # Using distance to line to regulate#########
        lVN = [lV[1], -lV[0]]
        # print(f"normalvektor: {lVN}")
        startSnakeVektor = [snakeEndPoint[0] - lineStartPoint[0], snakeEndPoint[1] - lineStartPoint[1]]
        distSnakeToLine = (lVN[0] * startSnakeVektor[0] + lVN[1] * startSnakeVektor[1]) / math.sqrt(
            lVN[0] ** 2 + lVN[1] ** 2)
        return -distSnakeToLine

    def calculateLines(self, lV, sV, LineEndoPoint, snakeEndPoint):
        """
        Calculates a orthogonal line on the finish point of the path. Creates a line for the snake,
        from front to back and a little longer
        :param lV: path vector
        :param sV: snake vector
        :param LineEndoPoint: (x,y) for the paths end
        :param snakeEndPoint: (x,y) for the front of the snake
        :return: snakeLine and finishLine
        """
        finishVector = [lV[1], -lV[0]]
        scalar = 10
        finishLine = [[LineEndoPoint[0] + (finishVector[0] * scalar), LineEndoPoint[1] + (finishVector[1] * scalar)],
                      [LineEndoPoint[0] + (-finishVector[0] * scalar), LineEndoPoint[1] + (-finishVector[1] * scalar)]]
        snakeLine = [snakeEndPoint, [snakeEndPoint[0] + (-sV[0]) * 2, snakeEndPoint[1] + (-sV[1]) * 2]]
        return snakeLine, finishLine

    def smartTurn(self, lV, sV, lVxsV, snakeEndPoint, lineStartPoint, P, db):
        """
        Calculates the turn angle for the snake
        :param lV: path vector
        :param sV: snake vector
        :param lVxsV: cross product between lV and sV
        :param snakeEndPoint: (x,y) for front of the snake
        :param lineStartPoint: (x,y) for the start of the path
        :param P: Proportional gain
        :param db: deadband in pixels
        :return: turn angle in int, or "right"/"left" if lateral shift
        """

        distanceToLine = self.calculatDistanceToLine(lV, snakeEndPoint, lineStartPoint)

        theta = self.calculateTheta(lV, sV, lVxsV)

        # print(f"Distance: {distanceToLine} \n Theta: {theta}")

        if abs(distanceToLine) > db:
            self.currentAngle = self.currentAngle + int(distanceToLine * P)
        else:
            self.currentAngle = self.currentAngle + theta

        if self.currentAngle > 90:
            self.currentAngle = 90
        elif self.currentAngle < - 90:
            self.currentAngle = -90

        return self.currentAngle


class SnakeCollision:

    def __init__(self, mazeLineList, frontRightLim, frontRightFrontLim, frontFrontLeftLim, frontLeftLim, midRightMin,
                 midRightMax, midLeftMin, midLeftMax, backRightLim, backRightBackLim, backBackLeftLim, backLeftLim):
        """
        Because of how atan2 works, all angles in the positive y-axis, are given as positive angles, while the angles
        for the negative y-axis are given as negative angles. This makes the creation of sectors for the collision
        detection a bit tricky. As such, if you want to have the sector on the left of the front to be from
        135 degrees to 195 degrees, you have to set frontFrontLeftLim to 135 degrees,
        and the frontLeftLim to -165 degrees.

        :param mazeLineList: List of lines in maze
        :param frontRightLim: Minimum angle right, i.e. -15 deg
        :param frontRightFrontLim: Split between right and front, i.e. 45deg
        :param frontFrontLeftLim: Split between front and left, i.e. 135deg
        :param frontLeftLim: Max angle left, i.e. 195 deg
        :param midRightMin: Min angle right, i.e. -15 deg
        :param midRightMax: Max angle right, i.e. 15 deg
        :param midLeftMin: Min angle left, i.e. 165 deg
        :param midLeftMax: Max angle left, i.e. 195 deg
        :param backRightLim: Max Angle right, i.e. 15 deg
        :param backRightBackLim: Split between right and back, i.e. -45deg
        :param backBackLeftLim: Split between back and left, i.e. -135deg
        :param backLeftLim: Max angle left, i.e. 165deg
        """
        self.mazeLines = mazeLineList
        self.frontLeftLim = frontLeftLim
        self.frontFrontLeftLim = frontFrontLeftLim
        self.frontRightFrontLim = frontRightFrontLim
        self.frontRightLim = frontRightLim
        self.midLeftMin = midLeftMin
        self.midLeftMax = midLeftMax
        self.midRightMin = midRightMin
        self.midRightMax = midRightMax
        self.backRightLim = backRightLim
        self.backRightBackLim = backRightBackLim
        self.backBackLeftLim = backBackLeftLim
        self.backLeftLim = backLeftLim

        self.frontRightCollision = False
        self.frontFrontCollision = False
        self.frontLeftCollision = False

        self.midRightCollision = False
        self.midLeftCollision = False

        self.backRightCollision = False
        self.backBackCollision = False
        self.backLeftCollision = False

    def updateCollisions(self, snakeCoordList, distThreshold, offset):
        """
        Updates flags for the different sectors of possible collision for each part of the snake

        :param offset: accounts for the snakes angle
        :param snakeCoordList: list of coordinates for front, mid and back of snake
        :param distThreshold: the threshold to check collision against
        :return: None
        """

        snakeFront = Point(snakeCoordList[0][0], snakeCoordList[0][1])
        snakeMid = Point(snakeCoordList[1][0], snakeCoordList[1][1])
        # snakeBack = Point(snakeCoordList[2][0], snakeCoordList[2][1])

        self.resetCollisions()

        for data in self.mazeLines:
            x1 = data[0][0]
            y1 = data[0][1]
            x2 = data[0][2]
            y2 = data[0][3]
            obst = LineString([(x1, y1), (x2, y2)])
            dist = obst.distance(snakeFront)

            if dist < distThreshold:
                closestPoint = self.getClosestPoint([x1, y1], [x2, y2], [snakeFront.x, snakeFront.y])
                angleToPoint = self.calculateAngleToNearestPoint([snakeFront.x, snakeFront.y],
                                                                 closestPoint) + offset - 90

                print(f"Closest point front: {closestPoint}")

                if angleToPoint < -15:
                    angleToPoint += 360

                # From -15deg to 45deg
                if self.frontFrontLeftLim < angleToPoint <= self.frontLeftLim:
                    self.frontLeftCollision = True
                # From 45 deg to 135deg
                if self.frontRightFrontLim <= angleToPoint <= self.frontFrontLeftLim:
                    self.frontFrontCollision = True
                # From 135 deg to 195deg, takes the opposite
                if self.frontRightLim <= angleToPoint < self.frontRightFrontLim:
                    self.frontRightCollision = True

            if obst.distance(snakeMid) < distThreshold:
                closestPoint = self.getClosestPoint([x1, y1], [x2, y2], [snakeMid.x, snakeMid.y])
                angleToPoint = self.calculateAngleToNearestPoint([snakeMid.x, snakeMid.y], closestPoint) + offset - 90

                print(f"Closest point mid: {closestPoint}")
                print(f"Angle before for mid: {angleToPoint}")

                if angleToPoint < -15:
                    angleToPoint += 360

                print(f"Angle to point after for mid: {angleToPoint}")

                # Checks from -15deg to 15deg
                if self.midLeftMin <= angleToPoint <= self.midLeftMax:
                    self.midLeftCollision = True
                # Checks 165deg to 195deg, takes the opposite
                if self.midRightMin <= angleToPoint <= self.midRightMax:
                    self.midRightCollision = True
            # if obst.distance(snakeBack) < distThreshold and checkSnakeBack:
            #    closestPoint = self.getClosestPoint([x1, y1], [x2, y2], [snakeBack.x, snakeBack.y])
            #    angleToPoint = self.calculateAngleToNearestPoint([snakeBack.x, snakeBack.y], closestPoint)
            #
            #    # Checks from -165 to 135, and takes the opposite of it. Because of how atan2 works
            #    if not (self.backBackLeftLim <= angleToPoint < self.backLeftLim):
            #        self.backLeftCollision = True
            #    # Checks from -45 to -135
            #    if self.backBackLeftLim <= angleToPoint <= self.backRightBackLim:
            #        self.backBackCollision = True
            #    # Checks from -45 to 15
            #    if self.backRightBackLim < angleToPoint <= self.backRightLim:
            #        self.backRightCollision = True

    def resetCollisions(self):
        """
        Resets the collision flags
        :return: None
        """
        self.frontLeftCollision = False
        self.frontFrontCollision = False
        self.frontRightCollision = False

        self.midRightCollision = False
        self.midLeftCollision = False

        self.backLeftCollision = False
        self.backBackCollision = False
        self.backRightCollision = False

    def noCollisions(self):
        if any([self.frontLeftCollision, self.frontFrontCollision, self.frontRightCollision, self.midLeftCollision,
                self.midRightCollision, self.backRightCollision, self.backBackCollision, self.backLeftCollision]):
            return False
        else:
            return True

    def rightSectorCollision(self):
        if any([self.frontRightCollision, self.midRightCollision, self.backRightCollision]):
            return True
        else:
            return False

    def leftSectorCollision(self):
        if any([self.frontLeftCollision, self.midLeftCollision, self.backLeftCollision]):
            return True
        else:
            return False

    def bothSectorCollision(self):
        if self.leftSectorCollision() and self.rightSectorCollision():
            return True
        else:
            return False

    def calculateAngleToNearestPoint(self, snakeCoord, pointCoord):
        """
        Calculates the angle from a point to another point in degrees
        :param snakeCoord: (x,y) for From-coordinate
        :param pointCoord: (x,y) for To-coordinate
        :return: angle between points in degrees
        """
        vectorX = pointCoord[0] - snakeCoord[0]
        vectorY = pointCoord[1] - snakeCoord[1]

        angle = math.atan2(vectorY, vectorX)
        angle = math.degrees(angle)
        return angle

    def getClosestPoint(self, mazeLineStart, mazeLineStop, point):
        """
        Gets closest point between a coordinate and a line given by two set of coordinates
        :param mazeLineStart: (x,y) for start of the line
        :param mazeLineStop: (x,y) for end of the line
        :param point: (x,y) for the point to check against
        :return: (x,y) for the nearest point
        """
        startToPoint = [point[0] - mazeLineStart[0], point[1] - mazeLineStart[1]]
        startToStop = [mazeLineStop[0] - mazeLineStart[0], mazeLineStop[1] - mazeLineStart[1]]

        lengdeMazeLine = startToStop[0] ** 2 + startToStop[1] ** 2

        dotProduct = startToPoint[0] * startToStop[0] + startToPoint[1] * startToStop[1]

        normalizedDistance = dotProduct / lengdeMazeLine

        if normalizedDistance < 0:
            pointClosest = mazeLineStart
        elif normalizedDistance > 1:
            pointClosest = mazeLineStop
        else:
            pointClosest = [mazeLineStart[0] + startToStop[0] * normalizedDistance,
                            mazeLineStart[1] + startToStop[1] * normalizedDistance]
        return pointClosest


if __name__ == "__main__":
    lines = [[[500, 200, 500, 800]], [[0, 0, 300, 200]]]

    sc = SnakeCollision(lines, -15, 45, 135, 195, -15, 15, 165, 195, 15, -45, -135, 165)

    sc.updateCollisions([[100, 500], [100, 150]], 500)
