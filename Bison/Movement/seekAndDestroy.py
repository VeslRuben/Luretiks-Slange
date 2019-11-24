import math

from Bison.Movement.goToTarget import GoToTarget
from Bison.Movement.Snake import Snake
from Bison.Movement.snakeController import SnakeCollision
from Bison.logger import Logger
from Bison.ImageProcessing.findTarget import FindTarget


class SeekAndDestroy(GoToTarget):

    def __init__(self, path: list, snake: Snake, snakeCollision: SnakeCollision, deadBandAngleSmall: int,
                 deadBandAngleBig: int, deadBandDistSmall: int, deadBandDistBig: int):
        super().__init__(path[0], snake, snakeCollision, deadBandAngleSmall, deadBandAngleBig, deadBandDistSmall,
                         deadBandDistBig)

        # Objects
        self.findTarget = FindTarget()

        # Path Variables
        self.j = 0
        self.totalPath = path
        self.targetAcq = False

    def updatePath(self):
        self.j += 1
        self.path = self.totalPath[j]
        self.i = 1
        Logger.logg(f"Goal reached, new path. i: {self.i}, j: {self.j}", Logger.info)

    def checkDistanceToGoal(self, snakeFrontCoordinates, restOfPath):
        sum = 0
        restOfPath = restOfPath[0]

        firstVector = [restOfPath[0][0] - snakeFrontCoordinates[0], restOfPath[0][1] - snakeFrontCoordinates[1]]
        sum += math.sqrt(firstVector[0] ** 2 + firstVector[1] ** 2)

        for i in range(len(restOfPath) - 1):
            vector = [restOfPath[i + 1][0] - restOfPath[i][0], restOfPath[i + 1][1] - restOfPath[i][1]]

            sum += math.sqrt(vector[0] ** 2 + vector[1] ** 2)

        return sum

    def targetAcquired(self) -> bool:
        pic = self.snake.takePicture()
        temp = self.findTarget.getTarget(pic)
        if temp:
            return True
        else:
            return False

    def run(self, snakeCoordinates: list, collisionThreshold: int):
        if not self.targetAcq:
            offset = self.calculateOffset(snakeCoordinates)

            snakePic = self.snake.takePicture()
            self.snakeCollision.updateCollisions(snakeCoordinates, collisionThreshold, offset, snakePic)

            lineStart = self.path[self.i]
            lineEnd = self.path[self.i + 1]

            # Establishing the front and back of the snake
            snakePointF = snakeCoordinates[1]
            snakePointB = snakeCoordinates[0]

            # Getting line vectors and cross-product
            lV, sV, lVxsV = self.snakeController.calculateLineVectors(lineStart, lineEnd, snakePointB,
                                                                      snakePointF)
            self.checkForNewNode(lV, sV, lineEnd, snakePointF)

            restOfPath = [self.path[self.i + 1:len(self.path) - 1]]

            self.goalReached = self.checkDistanceToGoal(snakePointF, restOfPath)

            if not self.goalReached:
                self.moving = self.decideMovement(lV, sV, lVxsV, snakePointF, lineStart)
            else:
                self.targetAcq = self.targetAcquired()
                if self.j < len(self.totalPath) - 1:
                    self.updatePath()

