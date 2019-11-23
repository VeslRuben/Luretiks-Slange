from Bison.ImageProcessing.camera import Camera
from Bison.Movement.Snake import Snake
from Bison.Movement.snakeController import SnakeCollision, SnakeController
from Bison.logger import Logger
from Bison.Broker import Broker as b
from Bison.ImageProcessing.cheakPathForObs import cheakPathForObs


class GoToTarget:

    def __init__(self, path, snake: Snake, snakeCollision: SnakeCollision, deadBandAngleSmall:int, deadBandAngleBig:int,
                 deadBandDistSmall:int, deadBandDistBig:int):
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
        if self.snakeCollision.noCollisions():
            if args:
                return wantedMovement(args)
            else:
                return wantedMovement()
        else:
            self.collisionHandling()

    def collisionHandling(self):
        # Checking for front
        Logger.logg(f"Executing collision command", Logger.info)
        if self.snakeCollision.colliding:
            pass
        elif self.snakeCollision.frontFrontCollision:
            # Checking both sectors at once
            if self.snakeCollision.bothSectorCollision():
                # Double backwards
                self.moving = self.snake.moveBackward()
                self.readyToMoveForward = False
                self.readyToMoveBackward = True
            # Checking left sector
            elif self.snakeCollision.leftSectorCollision():
                # Lateral shift right, ready to move backwards
                acc = self.snake.setAmplitude(15)
                Logger.logg(f"Amplitude turned down for lateral shift right, acc: {acc}", Logger.cmd)
                self.moving = self.snake.moveRight()
                self.ampChanged = True
                self.readyToMoveForward = False
                self.readyToMoveBackward = True
            # Checking right sector
            elif self.snakeCollision.rightSectorCollision():
                # Lateral shift left, ready to move backwards
                acc = self.snake.setAmplitude(15)
                Logger.logg(f"Amplitude turned down for lateral shift left, acc: {acc}", Logger.cmd)
                self.moving = self.snake.moveLeft()
                self.ampChanged = True
                self.readyToMoveForward = False
                self.readyToMoveBackward = True
            # If only collision in front
            else:
                # Back it up motherfucker
                self.moving = self.snake.reset()
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
                self.moving = self.snake.reset()
            # Checking left sector
            elif self.snakeCollision.leftSectorCollision():
                # Reset moving flags, and lateral shift right
                acc = self.snake.setAmplitude(15)
                Logger.logg(f"Amplitude turned down for lateral shift right, acc: {acc}", Logger.cmd)
                self.moving = self.snake.moveRight()
                self.ampChanged = True
                self.readyToMoveForward = False
                self.readyToMoveBackward = False
            # Checking right sector
            elif self.snakeCollision.rightSectorCollision():
                # Reset moving flags, and lateral shift left
                acc = self.snake.setAmplitude(15)
                Logger.logg(f"Amplitude turned down for lateral shift left, acc: {acc}", Logger.cmd)
                self.moving = self.snake.moveLeft()
                self.ampChanged = True
                self.readyToMoveBackward = False
                self.readyToMoveForward = False

    def calculateOffset(self, snakeCoordinates):
        xVector = [1, 0]
        snakeVector = [snakeCoordinates[1][0] - snakeCoordinates[0][0],
                       snakeCoordinates[1][1] - snakeCoordinates[0][1]]
        xVxsV = xVector[0] * snakeVector[1] - xVector[1] * snakeVector[0]
        offset = self.snakeController.calculateTheta(xVector, snakeVector, xVxsV)

        return offset

    def isCommandDone(self):
        cmdDone = self.snake.isCommandDone()
        if cmdDone:
            self.moving = False
        return cmdDone

    def checkForNewNode(self, lV, sV, lineEnd, snakePointF):
        # Checks if the snake has reached a new node
        snakeLine, finishLine = self.snakeController.calculateLines(lV, sV, lineEnd, snakePointF)
        if self.snakeController.intersect(finishLine[0], finishLine[1], snakeLine[0], snakeLine[1]):
            self.i += 1


    def checkForGoal(self):
        # Checks if the snake has reached the goal
        if self.i >= len(self.path) - 1:
            self.snake.stop()
            print("Stop")
            Logger.logg("Snake reached goal", Logger.info)
            self.i = 0
            return True
        else:
            return False

    def goToTarget(self, snakeCoordinates:list, collisionThreshold:int):
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
            if self.readyToMoveForward or self.readyToMoveBackward:
                if self.ampChanged:
                    amp = None
                    with b.lock:
                        amp = b.params[0]
                    acc = self.snake.setAmplitude(amp)
                    Logger.logg(f"Amplitude set back to {amp}, acc: {acc}", Logger.cmd)
                    self.ampChanged = False
                if self.readyToMoveForward:
                    self.moving = self.checkMovement(self.snake.moveForward)
                    self.readyToMoveForward = False
                elif self.readyToMoveBackward:
                    self.moving = self.checkMovement(self.snake.moveBackward)
                    self.readyToMoveBackward = False
            else:
                # Finding the angle-offset between snake vector and the path-vector, calculating distance to the line
                theta = self.snakeController.calculateTheta(lV, sV, lVxsV)
                distanceToLine = self.snakeController.calculatDistanceToLine(lV, snakePointF, lineStart)

                # Angle and distance worse than big deadbands
                if abs(theta) > self.deadBandAngleBig and abs(distanceToLine) > self.deadBandDistBig:
                    if theta < 0:
                        self.moving = self.checkMovement(self.snake.rotateCW)
                    else:
                        self.moving = self.checkMovement(self.snake.rotateCCW)
                # Angle is smaller than big dead band, distance is bigger than big deadband
                elif abs(theta) < self.deadBandAngleBig and abs(distanceToLine) > self.deadBandDistBig:
                    if distanceToLine < 0:
                        self.moving = self.checkMovement(self.snake.moveRight)
                    else:
                        self.moving = self.checkMovement(self.snake.moveLeft)
                # Angle is bigger than big dead band, distance is smaller than big dead band
                elif abs(theta) > self.deadBandAngleBig and abs(distanceToLine) < self.deadBandDistBig:
                    if theta < 0:
                        self.moving = self.checkMovement(self.snake.rotateCW)
                    else:
                        self.moving = self.checkMovement(self.snake.rotateCCW)
                else:
                    # Angle is bigger than small dead band, distance is bigger than small dead band
                    if abs(theta) > self.deadBandAngleSmall and abs(distanceToLine) > self.deadBandDistSmall:
                        turnAngle = self.snakeController.turn(lV, snakePointF, lineStart, self.propGain)
                        self.moving = self.checkMovement(self.snake.turn, args=turnAngle)
                        self.readyToMoveForward = True
                    # Angle is smaller than small dead band, distance is bigger than small dead band
                    elif abs(theta) < self.deadBandAngleSmall and abs(distanceToLine) > self.deadBandDistSmall:
                        turnAngle = self.snakeController.turn(lV, snakePointF, lineStart, self.propGain)
                        self.moving = self.checkMovement(self.snake.turn, args=turnAngle)
                        self.readyToMoveForward = True
                    # Angle is bigger than small dead band, distance is smaller than small dead band
                    elif abs(theta) > self.deadBandAngleSmall and abs(distanceToLine) < self.deadBandDistSmall:
                        turnAngle = theta
                        self.moving = self.checkMovement(self.snake.turn, args=turnAngle)
                        self.readyToMoveForward = True
                    # Angle is smaller than small dead band, distance is smaller than small dead band
                    elif abs(theta) < self.deadBandAngleSmall and abs(distanceToLine) < self.deadBandDistSmall:
                        self.moving = self.checkMovement(self.snake.moveForward)

