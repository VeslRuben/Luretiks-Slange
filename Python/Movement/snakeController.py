import math
from shapely.geometry import LineString, Point
from Python.logger import Logger
from Python.ImageProcessing.checkPathForObst import CheckPathForObst


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
            theta = 180
        return theta

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

    def turn(self, lV, snakeEndPoint, lineStartPoint, P):
        """
        Calculates the turn angle for the snake
        :param lV: path vector
        :param snakeEndPoint: (x,y) for front of the snake
        :param lineStartPoint: (x,y) for the start of the path
        :param P: Proportional gain
        :return: turn angle in int, or "right"/"left" if lateral shift
        """

        distanceToLine = self.calculatDistanceToLine(lV, snakeEndPoint, lineStartPoint)


        self.currentAngle = self.currentAngle + int(distanceToLine * P)

        if self.currentAngle > 90:
            self.currentAngle = 90
        elif self.currentAngle < - 90:
            self.currentAngle = -90

        return self.currentAngle

    def turnTheta(self, theta):
        self.currentAngle += theta

        if self.currentAngle > 90:
            self.currentAngle = 90
        elif self.currentAngle < - 90:
            self.currentAngle = -90
        return self.currentAngle


class SnakeCollision:

    def __init__(self, mazeLineList, frontLeftLim, frontFrontLeftLim, frontRightFrontLim, frontRightLim, midLeftMin,
                 midLeftMax, midRightMin, midRightMax, backRightLim, backRightBackLim, backBackLeftLim, backLeftLim):
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

        # For the front facing camera
        self.snakeObstacle = CheckPathForObst()
        self.colliding = False

    def updateCollisions(self, snakeCoordList, distThreshold, offset, snakePic):
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

        snakeFrontLeftLine = LineString([(snakeFront.x, snakeFront.y), (
            snakeFront.x + distThreshold * math.cos(math.radians(self.frontFrontLeftLim + offset)),
            snakeFront.y + distThreshold * math.sin(math.radians(self.frontFrontLeftLim + offset)))])
        snakeFrontRightLine = LineString([(snakeFront.x, snakeFront.y), (
            snakeFront.x + distThreshold * math.cos(math.radians(self.frontRightFrontLim + offset)),
            snakeFront.y + distThreshold * math.sin(math.radians(self.frontRightFrontLim + offset)))])

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
                angleToPoint = self.calculateAngleToNearestPointV2(snakeCoordList, [snakeFront.x, snakeFront.y],
                                                                   closestPoint)

                # From -15deg to 45deg
                if self.frontFrontLeftLim > angleToPoint >= self.frontLeftLim or obst.intersects(snakeFrontLeftLine):
                    self.frontLeftCollision = True
                    Logger.logg(
                        f"front left collision @closet point: {closestPoint} snake pos: {snakeFront.x}, {snakeFront.y}",
                        Logger.info)
                # From 45 deg to 135deg
                if self.frontRightFrontLim >= angleToPoint >= self.frontFrontLeftLim or obst.intersects(
                        snakeFrontLeftLine) or obst.intersects(snakeFrontRightLine):
                    self.frontFrontCollision = True
                    Logger.logg(
                        f"front front collision @closet point: {closestPoint} snake pos: {snakeFront.x}, {snakeFront.y}",
                        Logger.info)
                # From 135 deg to 195deg, takes the opposite
                if self.frontRightLim >= angleToPoint > self.frontRightFrontLim or obst.intersects(snakeFrontRightLine):
                    self.frontRightCollision = True
                    Logger.logg(
                        f"front right collision @closet point: {closestPoint} snake pos: {snakeFront.x}, {snakeFront.y}",
                        Logger.info)

            dist2 = obst.distance(snakeMid)
            if dist2 < distThreshold:
                closestPoint2 = self.getClosestPoint([x1, y1], [x2, y2], [snakeMid.x, snakeMid.y])
                angleToPoint2 = self.calculateAngleToNearestPointV2(snakeCoordList, [snakeMid.x, snakeMid.y],
                                                                    closestPoint2)

                # Checks from -75deg to -105deg
                if self.midLeftMin >= angleToPoint2 >= self.midLeftMax:
                    self.midLeftCollision = True
                    Logger.logg(
                        f"front mid left collision @closet point: {closestPoint2} snake pos: {snakeMid.x}, {snakeMid.y}",
                        Logger.info)
                # Checks 75deg to 105deg, takes the opposite
                if self.midRightMin <= angleToPoint2 <= self.midRightMax:
                    self.midRightCollision = True
                    Logger.logg(
                        f"front mid right collision @closet point: {closestPoint2} snake pos: {snakeMid.x}, {snakeMid.y}",
                        Logger.info)

        self.colliding = self.snakeObstacle.findObsInPath(snakePic)

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
        """
        Checks all flags to see if there are no collisions
        :return: True if no collisions, False if any collisions
        """
        if any([self.frontLeftCollision, self.frontFrontCollision, self.frontRightCollision, self.midLeftCollision,
                self.midRightCollision, self.backRightCollision, self.backBackCollision, self.backLeftCollision,
                self.colliding]):
            return False
        else:
            return True

    def rightSectorCollision(self):
        """
        Checks for collisions on right sector
        :return: True if any collisions, False if no collisions
        """
        if any([self.frontRightCollision, self.midRightCollision, self.backRightCollision]):
            return True
        else:
            return False

    def leftSectorCollision(self):
        """
        Checks for collisions on left sector
        :return: True if any collisions, False if no collisions
        """
        if any([self.frontLeftCollision, self.midLeftCollision, self.backLeftCollision]):
            return True
        else:
            return False

    def bothSectorCollision(self):
        """
        Checks for collisions on both sectors
        :return: True if collisions on both sides, False if on none or just one of the sides
        """
        if self.leftSectorCollision() and self.rightSectorCollision():
            return True
        else:
            return False

    def calculateAngleToNearestPointV2(self, snakeCoordList, fromPoint, toPoint):
        """
        Calculates angle to nearest point from the snake
        :param snakeCoordList: List of coordinates for the snakes parts
        :param fromPoint: Point from which the angle should be calculated
        :param toPoint: Point to which the angle should be calculated
        :return: Angle in degrees to the point given
        """
        vectorX = [snakeCoordList[1][0] - snakeCoordList[0][0], snakeCoordList[1][1] - snakeCoordList[0][1]]
        vectorY = [toPoint[0] - fromPoint[0], toPoint[1] - fromPoint[1]]

        xDoty = vectorX[0] * vectorY[0] + vectorX[1] * vectorY[1]
        length = math.sqrt(vectorX[0] ** 2 + vectorX[1] ** 2) * math.sqrt(vectorY[0] ** 2 + vectorY[1] ** 2)
        angle = math.acos(xDoty / length)
        XxY = vectorX[0] * vectorY[1] - vectorX[1] * vectorY[0]
        angle = angle * (XxY / abs(XxY))
        return math.degrees(angle)

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
