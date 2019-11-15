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
        theta = (theta * (lVxsV / abs(lVxsV))) * 180 / math.pi  # (lVxsV / abs(lVxsV)) is 1 or -1
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
        #print(f"normalvektor: {lVN}")
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

    def smartTurn(self, lV, sV, lVxsV, snakeEndPoint, lineStartPoint, P, db, rotThreshold):
        """
        Calculates the turn angle for the snake
        :param lV: path vector
        :param sV: snake vector
        :param lVxsV: cross product between lV and sV
        :param snakeEndPoint: (x,y) for front of the snake
        :param lineStartPoint: (x,y) for the start of the path
        :param P: Proportional gain
        :param db: deadband in pixels
        :param rotThreshold: threshold for using lateral shift
        :return: turn angle in int, or "right"/"left" if lateral shift
        """
        rotate = None

        distanceToLine = self.calculatDistanceToLine(lV, snakeEndPoint, lineStartPoint)

        theta = self.calculateTheta(lV, sV, lVxsV)

        #print(f"Distance: {distanceToLine} \n Theta: {theta}")

        if abs(distanceToLine) > rotThreshold:
            if distanceToLine > 0:
                rotate = 1
            else:
                rotate = -1
        elif abs(distanceToLine) > db:
            self.currentAngle = self.currentAngle + int(distanceToLine * P)
        else:
            self.currentAngle = self.currentAngle + theta

        if self.currentAngle > 90:
            self.currentAngle = 90
        elif self.currentAngle < - 90:
            self.currentAngle = -90

        if rotate == -1:
            return "right"
        elif rotate == 1:
            return "left"
        else:
            return self.currentAngle

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

        pointClosest = [mazeLineStart[0] + startToStop[0]*normalizedDistance,
                        mazeLineStart[1] + startToStop[1]*normalizedDistance]

        return pointClosest

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

    def checkCollision(self, snakeFrontCoords, snakeMidCoords, snakeBackCoords, mazeLineList):
        """
        Checks collision of snake against the obstacles of the maze given by line coordinates
        :param snakeFrontCoords: (x,y) of front of snake
        :param snakeMidCoords:(x,y) of middle of snake
        :param snakeBackCoords:(x,y) of back of snake
        :param mazeLineList: list of lines for the maze
        :return: Dunno yet
        """
        snakeFront = Point(snakeFrontCoords[0], snakeFrontCoords[1])
        snakeMid = Point(snakeMidCoords[0], snakeMidCoords[1]).buffer(100)
        snakeBack = Point(snakeBackCoords[0], snakeBackCoords[1]).buffer(100)

        lineCrashFront = []
        lineCrashMid = []
        lineCrashBack = []

        # Check distance between the different points to the lines,
        # add the lines that are to close to the different lists
        for data in mazeLineList:
            x1 = data[0][0]
            y1 = data[0][1]
            x2 = data[0][2]
            y2 = data[0][3]
            obst = LineString([(x1, y1), (x2, y2)])
            if obst.distance(snakeFront) < 75:
                point = self.getClosestPoint([x1, y1], [x2, y2], snakeFrontCoords)
                print(f"Nearest Collision for Head at: {point}")
                dist = self.calculatDistanceToLine(lV=[x2-x1, y2-y1], snakeEndPoint=snakeFrontCoords, lineStartPoint=[x1, y1])
                angle = self.calculateAngleToNearestPoint(snakeFrontCoords, point)
                print(f"distance: {dist}, at angle: {angle}")
                lineCrashFront.append([dist, angle])
            if obst.distance(snakeMid) < 1000:
                point = self.getClosestPoint([x1, y1], [x2, y2], snakeMidCoords)
                print(f"Nearest Collision for Middle at: {point}")
                dist = self.calculatDistanceToLine(lV=[x2-x1, y2-y1], snakeEndPoint=snakeMidCoords, lineStartPoint=[x1,y1])
                angle = self.calculateAngleToNearestPoint(snakeMidCoords, point)
                print(f"distance: {dist}, at angle: {angle}")
                lineCrashMid.append([dist, angle])
            if obst.distance(snakeBack) < 2000:
                point = self.getClosestPoint([x1, y1], [x2, y2], snakeBackCoords)
                print(f"Nearest Collision for Middle at: {point}")
                dist = self.calculatDistanceToLine(lV=[x2-x1, y2-y1], snakeEndPoint=snakeBackCoords, lineStartPoint=[x1,y1])
                angle = self.calculateAngleToNearestPoint(snakeBackCoords, point)
                print(f"distance: {dist}, at angle: {angle}")
                lineCrashBack.append([dist, angle])

        # Calculate angle to the obstacles

if __name__ == "__main__":
    sc = SnakeController()

    sc.checkCollision(snakeFrontCoords=[1000, 500], snakeMidCoords=[200,500], snakeBackCoords=[400, 500], mazeLineList=[[[950, 300, 950, 600]]])


