"""
Expansion of GoToTarget. Now takes in a list of goals to reach via a list of paths.

author: Håkon Bjerkgaard Waldum, Ruben Svedal Jørundland, Marcus Olai Grindvik
"""

import math
import time

from Python.GUI import CustomEvent
from Python.Movement.goToTarget import GoToTarget
from Python.Movement.snake import Snake
from Python.Movement.snakeMethods import SnakeCollision
from Python.logger import Logger
from Python.ImageProcessing.findTarget import FindTarget
from Python.broker import Broker as b


class SeekAndDestroy(GoToTarget):

    def __init__(self, path: list, snake: Snake, snakeCollision: SnakeCollision, deadBandAngleSmall: int,
                 deadBandAngleBig: int, deadBandDistSmall: int, deadBandDistBig: int, eventData):
        """
        Inherits from the GoToTarget-class.

        :param path: the complete path for multi-target
        :param snake: snake-object for applying commands
        :param snakeCollision: snakeCollision-object for checking for collisions
        :param deadBandAngleSmall: the lower deadband for angle used in movement
        :param deadBandAngleBig: the higher deadband for angle used in movement
        :param deadBandDistSmall: the lower deadband for distance used in movement
        :param deadBandDistBig: the higher deadband for distance used in movement
        """
        super().__init__(path[0], snake, snakeCollision, deadBandAngleSmall, deadBandAngleBig, deadBandDistSmall,
                         deadBandDistBig)

        # Information to update GUI
        self.eventData = eventData
        self.guiEvents = eventData["events"]
        self.guiId = eventData["id"]
        self.guiEventhandler = eventData["eventHandler"]

        # Objects
        self.findTarget = FindTarget()

        # Path Variables
        self.j = 0
        self.totalPath = path
        self.targetAcq = False
        self.goalThreshold = 150

    def updatePath(self):
        """
        Updates to the next path in the list of paths
        :return: None
        """
        self.j += 1
        self.path = self.totalPath[self.j]
        self.i = 1
        Logger.logg(f"Goal reached, new path. i: {self.i}, j: {self.j}", Logger.info)

    def checkDistanceToGoal(self, snakeFrontCoordinates, restOfPath):
        """
        Checks the total length from the snakes head to the goal along the given path
        :param snakeFrontCoordinates: (x,y) for the snakes front
        :param restOfPath: the rest of the path from the node it is going towards
        :return: Length of the path in pixels
        """
        sum = 0
        restOfPath = restOfPath[0]

        firstVector = [restOfPath[0][0] - snakeFrontCoordinates[0], restOfPath[0][1] - snakeFrontCoordinates[1]]
        sum += math.sqrt(firstVector[0] ** 2 + firstVector[1] ** 2)

        for i in range(len(restOfPath) - 1):
            vector = [restOfPath[i + 1][0] - restOfPath[i][0], restOfPath[i + 1][1] - restOfPath[i][1]]

            sum += math.sqrt(vector[0] ** 2 + vector[1] ** 2)

        return sum

    def targetAcquired(self) -> bool:
        """
        Checks if the target is within the frame of the front-facing camera
        :return: True if target is there, False if else
        """
        updateEvent = CustomEvent(self.guiEvents["YesNoEvent"], self.guiId())
        self.guiEventhandler(updateEvent)
        while True:
            with b.lock:
                if b.answer is not None:
                    targetAccq = b.answer
                    break
            time.sleep(0.5)
        return targetAccq

    def run(self, snakeCoordinates: list, collisionThreshold: int):
        """
        Runs through a cycle for the snakes movements and commands. Updates collisions, checks if a new node is passed,
        checks if the goal is reached. Updates to the new path if a goal is reached. Stops if all goals have been reached.

        :param snakeCoordinates: List of coordinates for the snakes parts
        :param collisionThreshold: Threshold for which the collisions should apply
        :return: None
        """
        if not self.targetAcq:
            offset = self.calculateOffset(snakeCoordinates)

            # snakePic = self.snake.takePicture()
            self.snakeCollision.updateCollisions(snakeCoordinates, collisionThreshold, offset, None)

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

            distance = self.checkDistanceToGoal(snakePointF, restOfPath)

            if distance > self.goalThreshold:
                self.goalReached = False
            else:
                self.goalReached = True

            if not self.goalReached:
                self.moving = self.decideMovement(lV, sV, lVxsV, snakePointF, lineStart)
            else:
                goal = self.path[len(self.path) - 1]
                gV = [goal[0] - snakeCoordinates[1][0], goal[1] - snakeCoordinates[1][1]]
                gVxsV = gV[0] * sV[1] - gV[1] * sV[0]
                goalThetea = self.snakeController.calculateTheta(gV, sV, gVxsV)
                if abs(goalThetea) < 10:
                    self.targetAcq = self.targetAcquired()
                    if self.j < len(self.totalPath) - 1:
                        self.updatePath()
                        self.moving = True
                elif abs(goalThetea) < 30:
                    turnAngle = self.snakeController.turnTheta(goalThetea)
                    self.moving = self.checkMovement(self.snake.turn, turnAngle)
                else:
                    if goalThetea > 0:
                        self.moving = self.checkMovement(self.snake.rotateCCW)
                    else:
                        self.moving = self.checkMovement(self.snake.rotateCW)
