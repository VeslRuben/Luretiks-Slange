from Bison.ImageProcessing.camera import Camera
from Bison.Movement.Snake import Snake
from Bison.Movement.snakeController import SnakeCollision, SnakeController
from Bison.logger import Logger
from Bison.Broker import Broker as b
from Bison.ImageProcessing.cheakPathForObs import cheakPathForObs


class GoToTarget:

    def __init__(self, path, snake: Snake, snakeCollision: SnakeCollision, deadBandAngleSmall:int, deadBandAngleBig:int,
                 deadBandDistSmall:int, deadBandDistBig:int):
        """

        :param path: list of coordinates for path to go
        :param snake: snake-object to call movement functions
        :param snakeCollision: snakeCollision-object to check for collisions
        :param deadBandAngleSmall: the lower deadband for angle used in movement
        :param deadBandAngleBig: the higher deadband for angle used in movement
        :param deadBandDistSmall: the lower deadband for distance used in movement
        :param deadBandDistBig: the higher deadband for distance used in movement
        """
        # Lists
        self.path = path

        # Offsets
        self.deadBandAngleSmall = deadBandAngleSmall
        self.deadBandAngleBig = deadBandAngleBig
        self.deadBandDistSmall = deadBandDistSmall
        self.deadBandDistBig = deadBandDistBig

        # Objects
        self.cam = Camera()
        self.snake = snake
        self.snakeCollision = snakeCollision
        self.snakeController = SnakeController()
        self.snakeObstacle = cheakPathForObs()

        # Flags
        self.moving = False
        self.readyToMoveForward = False
        self.readyToMoveBackward = False
        self.ampChanged = False
        self.colliding = False

        # Path variables
        self.i = 0
        self.goalReached = False

        # Regulation variables
        self.propGain = 0.5

    def checkMovement(self, wantedMovement, args=None):
        """
        Uses collision handler to check if there are any collisions before doing movement
        :param wantedMovement: the function for the wanted movement
        :param args: angle if wantedMovement is the turn-function
        :return: True/False if any movement is applied
        """
        if self.snakeCollision.noCollisions():
            if args:
                return wantedMovement(args)
            else:
                return wantedMovement()
        else:
            return self.collisionHandling()

    def collisionHandling(self):
        """
        Checks for collisions in different sectors, applies movement to try to rectify this
        :return: True if any movement is applied, False if otherwise
        """
        moving = False
        # Checking for front
        Logger.logg(f"Executing collision command", Logger.info)
        if self.snakeCollision.colliding:
            moving = True
        elif self.snakeCollision.frontFrontCollision:
            # Checking both sectors at once
            if self.snakeCollision.bothSectorCollision():
                # Double backwards
                moving = self.snake.moveBackward()
                self.readyToMoveForward = False
                self.readyToMoveBackward = True
            # Checking left sector
            elif self.snakeCollision.leftSectorCollision():
                # Lateral shift right, ready to move backwards
                acc = self.snake.setAmplitude(15)
                Logger.logg(f"Amplitude turned down for lateral shift right, acc: {acc}", Logger.cmd)
                moving = self.snake.moveRight()
                self.ampChanged = True
                self.readyToMoveForward = False
                self.readyToMoveBackward = True
            # Checking right sector
            elif self.snakeCollision.rightSectorCollision():
                # Lateral shift left, ready to move backwards
                acc = self.snake.setAmplitude(15)
                Logger.logg(f"Amplitude turned down for lateral shift left, acc: {acc}", Logger.cmd)
                moving = self.snake.moveLeft()
                self.ampChanged = True
                self.readyToMoveForward = False
                self.readyToMoveBackward = True
            # If only collision in front
            else:
                # Back it up motherfucker
                moving = self.snake.reset()
                self.readyToMoveForward = False
                self.readyToMoveBackward = True
        # Checking for back
        elif self.snakeCollision.backBackCollision:
            # Checking both sectors at once
            if self.snakeCollision.bothSectorCollision():
                # Front it up motherfucker
                print("Crashed back and both sides")
            # Checking left sector
            elif self.snakeCollision.leftSectorCollision():
                # Do something
                print("Crashed back and left side")
            # Checking right sector
            elif self.snakeCollision.rightSectorCollision():
                # Do something
                print("Crashed back and right side")
            # If only collision in front
            else:
                # Front it up motherfucker
                print("Crashed only on back")
        else:
            # Checking both sectors at once
            if self.snakeCollision.bothSectorCollision():
                # Straighten snake, hope for the best
                moving = self.snake.reset()
            # Checking left sector
            elif self.snakeCollision.leftSectorCollision():
                # Reset moving flags, and lateral shift right
                acc = self.snake.setAmplitude(15)
                Logger.logg(f"Amplitude turned down for lateral shift right, acc: {acc}", Logger.cmd)
                moving = self.snake.moveRight()
                self.ampChanged = True
                self.readyToMoveForward = False
                self.readyToMoveBackward = False
            # Checking right sector
            elif self.snakeCollision.rightSectorCollision():
                # Reset moving flags, and lateral shift left
                acc = self.snake.setAmplitude(15)
                Logger.logg(f"Amplitude turned down for lateral shift left, acc: {acc}", Logger.cmd)
                moving = self.snake.moveLeft()
                self.ampChanged = True
                self.readyToMoveBackward = False
                self.readyToMoveForward = False
        return moving

    def calculateOffset(self, snakeCoordinates):
        """
        Calculates the snakes offset in relation to the X-axis of the image
        :param snakeCoordinates: list of the coordinates of the snakes parts
        :return: the offset in angles
        """
        xVector = [1, 0]
        snakeVector = [snakeCoordinates[1][0] - snakeCoordinates[0][0],
                       snakeCoordinates[1][1] - snakeCoordinates[0][1]]
        xVxsV = xVector[0] * snakeVector[1] - xVector[1] * snakeVector[0]
        offset = self.snakeController.calculateTheta(xVector, snakeVector, xVxsV)

        return offset

    def isCommandDone(self):
        """
        Checks if the snake has done the last command sent
        :return: True if done, False if not
        """
        cmdDone = self.snake.isCommandDone()
        if cmdDone:
            self.moving = False
        return cmdDone

    def checkForNewNode(self, lV, sV, lineEnd, snakePointF):
        """
        Checks if the snake has passed a node on the path
        :param lV: The vector for the path
        :param sV: The vector for the snake
        :param lineEnd: (x,y) of the end point of the line
        :param snakePointF: (x,y) for the snakes front
        :return: None
        """
        # Checks if the snake has reached a new node
        snakeLine, finishLine = self.snakeController.calculateLines(lV, sV, lineEnd, snakePointF)
        if self.snakeController.intersect(finishLine[0], finishLine[1], snakeLine[0], snakeLine[1]):
            self.i += 1

    def checkForGoal(self):
        """
        Checks if the snake has reached the goal
        :return: True if it has, False if else
        """
        if self.i >= len(self.path) - 1:
            self.snake.stop()
            print("Stop")
            Logger.logg("Snake reached goal", Logger.info)
            self.i = 0
            return True
        else:
            return False

    def decideMovement(self, lV, sV, lVxsV, snakePointF, lineStart):
        """
        Movement decider. Decides the movement of the snake according to a decision tree
        :param lV: vector of the path
        :param sV: vector of the snake
        :param lVxsV: cross-product of the line vector and the snake vector
        :param snakePointF: (x,y) for the snakes front
        :param lineStart: (x,y) for the start of the line vector
        :return: True if movement is applied, False if else
        """
        moving = False
        if self.readyToMoveForward or self.readyToMoveBackward:
            if self.ampChanged:
                amp = None
                with b.lock:
                    amp = b.params[0]
                acc = self.snake.setAmplitude(amp)
                Logger.logg(f"Amplitude set back to {amp}, acc: {acc}", Logger.cmd)
                self.ampChanged = False
            if self.readyToMoveForward:
                moving = self.checkMovement(self.snake.moveForward)
                self.readyToMoveForward = False
            elif self.readyToMoveBackward:
                moving = self.checkMovement(self.snake.moveBackward)
                self.readyToMoveBackward = False
        else:
            # Finding the angle-offset between snake vector and the path-vector, calculating distance to the line
            theta = self.snakeController.calculateTheta(lV, sV, lVxsV)
            distanceToLine = self.snakeController.calculatDistanceToLine(lV, snakePointF, lineStart)

            # Angle and distance worse than big deadbands
            if abs(theta) > self.deadBandAngleBig and abs(distanceToLine) > self.deadBandDistBig:
                if theta < 0:
                    moving = self.checkMovement(self.snake.rotateCW)
                else:
                    moving = self.checkMovement(self.snake.rotateCCW)
            # Angle is smaller than big dead band, distance is bigger than big deadband
            elif abs(theta) < self.deadBandAngleBig and abs(distanceToLine) > self.deadBandDistBig:
                if distanceToLine < 0:
                    moving = self.checkMovement(self.snake.moveRight)
                else:
                    moving = self.checkMovement(self.snake.moveLeft)
            # Angle is bigger than big dead band, distance is smaller than big dead band
            elif abs(theta) > self.deadBandAngleBig and abs(distanceToLine) < self.deadBandDistBig:
                if theta < 0:
                    moving = self.checkMovement(self.snake.rotateCW)
                else:
                    moving = self.checkMovement(self.snake.rotateCCW)
            else:
                # Angle is bigger than small dead band, distance is bigger than small dead band
                if abs(theta) > self.deadBandAngleSmall and abs(distanceToLine) > self.deadBandDistSmall:
                    turnAngle = self.snakeController.turn(lV, snakePointF, lineStart, self.propGain)
                    moving = self.checkMovement(self.snake.turn, args=turnAngle)
                    self.readyToMoveForward = True
                # Angle is smaller than small dead band, distance is bigger than small dead band
                elif abs(theta) < self.deadBandAngleSmall and abs(distanceToLine) > self.deadBandDistSmall:
                    turnAngle = self.snakeController.turn(lV, snakePointF, lineStart, self.propGain)
                    moving = self.checkMovement(self.snake.turn, args=turnAngle)
                    self.readyToMoveForward = True
                # Angle is bigger than small dead band, distance is smaller than small dead band
                elif abs(theta) > self.deadBandAngleSmall and abs(distanceToLine) < self.deadBandDistSmall:
                    turnAngle = theta
                    moving = self.checkMovement(self.snake.turn, args=turnAngle)
                    self.readyToMoveForward = True
                # Angle is smaller than small dead band, distance is smaller than small dead band
                elif abs(theta) < self.deadBandAngleSmall and abs(distanceToLine) < self.deadBandDistSmall:
                    moving = self.checkMovement(self.snake.moveForward)

        return moving

    def run(self, snakeCoordinates:list, collisionThreshold:int):
        """
        Runs through a cycle for applying movement to the snake. Updates collision, checks if new nodes are passed,
        checks if the goal is reached.

        :param snakeCoordinates: list of coordinates for the snakes parts
        :param collisionThreshold: the threshold for which the collision would apply
        :return: None
        """
        offset = self.calculateOffset(snakeCoordinates)

        snakePic = self.snake.takePicture()
        self.snakeCollision.updateCollisions(snakeCoordinates, collisionThreshold, offset, snakePic)

        # Establishing start and end of the path
        lineStart = self.path[self.i]
        lineEnd = self.path[self.i + 1]

        # Establishing the front and back of the snake
        snakePointF = snakeCoordinates[1]
        snakePointB = snakeCoordinates[0]

        # Getting line vectors and cross-product
        lV, sV, lVxsV = self.snakeController.calculateLineVectors(lineStart, lineEnd, snakePointB,
                                                                  snakePointF)
        self.checkForNewNode(lV, sV, lineEnd, snakePointF)

        self.goalReached = self.checkForGoal()

        if not self.goalReached:
            self.moving = self.decideMovement(lV, sV, lVxsV, snakePointF, lineStart)

