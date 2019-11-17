import gc as soplebil
import threading
import time

from Bison.Broker import Broker as b
from Bison.GUI import CustomEvent
from Bison.ImageProcessing.Draw import drawLines
from Bison.ImageProcessing.camera import Camera
from Bison.ImageProcessing.findSnake import FindSnake
from Bison.ImageProcessing.findTarget import FindTarget
from Bison.ImageProcessing.maze_recogn import mazeRecognizer
from Bison.Movement.Snake import Snake
from Bison.Movement.snakeController import SnakeController, SnakeCollision
from Bison.Pathfinding.rrt_star import RRTStar
from Bison.logger import Logger


class Controller(threading.Thread):

    def setup(self):
        Camera.initCam(0)

    def __init__(self, eventData):
        super().__init__()
        self.setup()
        self.running = True

        self.guiEvents = eventData["events"]
        self.guiId = eventData["id"]
        self.guiEventhandler = eventData["eventHandler"]

        # Mase Recognizer varibels ########
        self.maze = mazeRecognizer()
        self.lines = None
        self.lineImageArray = None
        ###################################

        # RRT* Variabels ##################
        self.rrtStar = None
        self.rrtPathImage = None
        self.findSnake = FindSnake()
        self.finTarget = FindTarget()
        self.finalPath = None
        ###################################

        # Snake variables ###########################
        self.snakeController = SnakeController()
        self.snakeCollision = SnakeCollision(None, -15, 45, 135, 195, -15, 15, 165, 195, 15, -45, -135, 165)
        self.overrideMoving = True
        self.readyToMoveForward = False
        self.readyToMoveBackward = False
        self.deadBand = 100
        self.deadBandAngle = 60
        self.collisionDistance = 50
        self.moving = False
        self.firstLoop = True
        self.i = 0
        self.j = 0
        self.traveledPath = []
        self.cam = Camera()
        self.snake = Snake("http://192.168.137.72", "192.168.137.167")
        time.sleep(1)
        with b.lock:
            print(self.snake.setAmplitude(b.params[0]))
            print(self.snake.setSpeed(b.params[1]))
        #############################################

    def notifyGui(self, event, arg):
        """
        Function for updating the GUI. Takes in an event, as well as an argument.
        depending on what event is to be updated.
        :param event: What to update
        :param arg: With what to update
        :return: Nothing
        """
        updateEvent = CustomEvent(self.guiEvents[event], self.guiId())
        updateEvent.SetMyVal(arg)
        self.guiEventhandler(updateEvent)

    def prepMaze(self):
        """
        Prepares maze by taking picture and running it through maze recognizer.
        Updates events in GUI to show the picture with the lines drawn on.
        :return: Nothing
        """
        self.notifyGui("UpdateTextEvent", "Preparing Maze")
        self.lines, self.lineImageArray = self.maze.findMaze()
        self.snakeCollision.mazeLines = self.lines

        self.notifyGui("UpdateImageEventR", self.lineImageArray)
        self.notifyGui("UpdateTextEvent", "Maze Ready")

    def findPath(self):
        """
        Gets the location of the snake as well as the location of a goal, then
        starts the RRT*-algorithm to find the path through the maze from start to goal.
        Updates events in GUI to show a picture with the maze and found path.
        :return:
        """
        self.notifyGui("UpdateTextEvent", "Finding path...")
        try:
            cords, temp = self.findSnake.LocateSnake(self.cam.takePicture())
            startX = cords[0][0]
            startY = cords[0][1]
        except TypeError:
            self.notifyGui("UpdateTextEvent", "Could not find snake")
        try:
            d, frame, radius, center = self.finTarget.getTarget(self.cam.takePicture())
            goalX = center[0]
            goalY = center[1]
        except TypeError:
            self.notifyGui("UpdateTextEvent", "Could not find target")
            return
        self.rrtStar = RRTStar(start=[startX, startY], goal=[goalX, goalY], rand_area_x=[250, 1500],
                               rand_area_y=[0, 1100],
                               lineList=self.lines,
                               expand_dis=100.0, path_resolution=10.0, max_iter=1000, goal_sample_rate=20,
                               connect_circle_dist=450,
                               edge_dist=30)
        self.rrtStar.lineList = self.lines
        self.rrtPathImage, self.finalPath = self.rrtStar.run(finishLoops=False)
        if self.finalPath is not None:
            self.finalPath = self.finalPath[::-1]
            self.notifyGui("UpdateTextEvent", "Path found!")
        else:
            self.notifyGui("UpdateTextEvent", "Could not find path")

        self.traveledPath = []

        self.notifyGui("UpdateImageEventL", temp)
        self.notifyGui("UpdateImageEventR", self.rrtPathImage)

        soplebil.collect()

    def moveSnakeManually(self):
        """
        Sets the snake in manual mode. Makes it possible to steer the snake manually.
        'w': Forward
        's': Backward
        'a': Lateral Shift Left
        'd': Lateral Shift Right
        'r': Reset positions
        'q': Rotate left
        'e': Rotate right
        :return: Nothing
        """
        with b.moveLock:
            if b.moveCmd != "":
                print(b.moveCmd)
                if b.moveCmd == "f":
                    self.snake.moveForward()
                elif b.moveCmd == "b":
                    self.snake.moveBacwards()
                elif b.moveCmd == "h":
                    self.snake.moveRight()
                elif b.moveCmd == "v":
                    self.snake.moveLeft()
                elif b.moveCmd == "s":
                    self.snake.stop()
                elif b.moveCmd == "r":
                    self.snake.reset()
                b.moveCmd = ""

    def autoMode(self):
        pass

    def goToTarget(self):
        """
        Gets the snake to move towards a target.
        :return: Nothing
        """
        # Update GUI #############################
        pic = self.cam.takePicture()
        colorPic = drawLines(pic, self.finalPath, (255, 0, 0))
        self.notifyGui("UpdateImageEventR", colorPic)
        ##########################################

        # returns if the snake is not ready to receive a command ####
        cmdDone = self.snake.isCommandDone()
        """
        If the snake returns that the last command is done, sets moving flag to false again.
        On the first loop this will pass because of OverrideMoving-flag to set moving to false.
        """
        if cmdDone or self.overrideMoving:
            self.moving = False
            self.overrideMoving = False

        """
        Checks if the snake is in movement, if not in movement, checks if it is ready to move.
        If ready to move, sends command to snake to move forward one cycle.
        """
        if self.moving:
            pass
        elif self.readyToMoveForward:
            snakeCoordinates, _ = self.findSnake.LocateSnakeAverage(1, 1)
            if snakeCoordinates:
                self.snakeCollision.updateCollisions(snakeCoordinates, self.collisionDistance)
                if not self.snakeCollision.frontFrontCollision:
                    self.moving = self.snake.moveForward()
                    self.readyToMoveForward = False
                else:
                    self.collisionHandling()
        elif self.readyToMoveBackward:
            snakeCoordinates, _ = self.findSnake.LocateSnakeAverage(1, 1)
            if snakeCoordinates:
                self.snakeCollision.updateCollisions(snakeCoordinates, self.collisionDistance)
                if not self.snakeCollision.backBackCollision:
                    self.moving = self.snake.moveBacwards()
                    self.readyToMoveBackward = False
                else:
                    self.collisionHandling()
        else:
            lineStart = self.finalPath[self.i]
            lineEnd = self.finalPath[self.i + 1]

            """
            Runs only on the first loop of the run.
            Adjusts the start angle before movement starts
            """
            if self.firstLoop:
                # Find snake coordinates, and the masked picture
                snakeCoordinates, maskPic = self.findSnake.LocateSnakeAverage(1, 1)

                # Check that the snake coordinates are found
                if snakeCoordinates:
                    self.firstLoop = False
                    snakePointF = snakeCoordinates[1]
                    snakePointB = snakeCoordinates[0]

                    lV, sV, lVxsV = self.snakeController.calculateLineVectors(lineStart, lineEnd, snakePointB,
                                                                              snakePointF)
                    snakeAngle = self.snakeController.calculateFirstTurnAngle(lV, sV, lVxsV)
                    self.moving = self.snake.turn(snakeAngle)

                    # Update GUI
                    self.notifyGui("UpdateImageEventL", maskPic)

            ############################################################################
            # Gets the location of the snake, and calculates vectors for path to follow
            # as well as vector for snake. Draws path on the masked picture.
            # Makes the snake turn or ready to move depending on its angle.
            ############################################################################
            else:
                # Get snake coordinates and the masked picture
                snakeCoordinates, maskPic = self.findSnake.LocateSnakeAverage(1, 1)
                # Check that the snake is found
                if snakeCoordinates:
                    snakePointF = snakeCoordinates[1]
                    snakePointB = snakeCoordinates[0]
                    lV, sV, lVxsV = self.snakeController.calculateLineVectors(lineStart, lineEnd, snakePointB,
                                                                              snakePointF)

                    # Update GUI with path on the masked picture
                    if len(self.traveledPath) > 1:
                        maskPic = drawLines(maskPic, self.traveledPath, (0, 255, 0))
                    self.notifyGui("UpdateImageEventL", maskPic)

                    # Checks if the snake has reached a new node
                    snakeLine, finishLine = self.snakeController.calculateLines(lV, sV, lineEnd, snakePointF)
                    if self.snakeController.intersect(finishLine[0], finishLine[1], snakeLine[0], snakeLine[1]):
                        self.i += 1

                    # Checks if the snake has reached the goal
                    if self.i >= len(self.finalPath) - 1:
                        self.snake.stop()
                        print("Stop")
                        Logger.logg("Snake reached goal", Logger.info)
                        self.firstLoop = False
                        with b.lock:
                            b.runFlag = False
                            self.i = 0

                    """ Moving logic"""
                    theta = self.snakeController.calculateTheta(lV, sV, lVxsV)
                    distanceToLine = self.snakeController.calculatDistanceToLine(lV, snakePointF, lineStart)
                    self.snakeCollision.updateCollisions(snakeCoordinates, self.collisionDistance)

                    if self.snakeCollision.noCollisions():
                        # alt er fint
                        if abs(theta) < self.deadBandAngle and abs(distanceToLine) < self.deadBand:
                            turnAngle = self.snakeController.smartTurn(lV, sV, lVxsV, snakePointF, lineStart, 0.5, 20)
                            self.moving = self.snake.turn(turnAngle)
                            self.readyToMoveForward = True
                        # vinker fin distance fuckt
                        elif abs(theta) < self.deadBandAngle and abs(distanceToLine) >= self.deadBand:
                            # Lateral shift
                            if distanceToLine < 0:
                                # Lateral right
                                self.moving = self.snake.moveRight()
                            elif distanceToLine > 0:
                                # Lateral left
                                self.moving = self.snake.moveLeft()
                        # vinkel fuckt distance fin
                        elif abs(theta) >= self.deadBandAngle and abs(distanceToLine) < self.deadBand:
                            # Rotate
                            if theta > 0:
                                # Rotate CCW, left
                                self.moving = self.snake.rotateCCW()
                            elif theta < 0:
                                # Rotate CW, right
                                self.moving = self.snake.rotateCW()
                        # alt er fuckt
                        elif abs(theta) >= self.deadBandAngle and abs(distanceToLine) >= self.deadBand:
                            # Rotate
                            if theta > 0:
                                # Rotate CCW, left
                                self.moving = self.snake.rotateCCW()
                            elif theta < 0:
                                # Rotate CW, right
                                self.moving = self.snake.rotateCW()
                    else:
                        self.collisionHandling()

                    """ Moving logic END!!!!!!"""

                    # Appends the new position of the snake to its traveled path
                    self.traveledPath.append(snakePointF)

    def collisionHandling(self):
        # Checking for front
        if not self.snakeCollision.frontFrontCollision:
            # Checking both sectors at once
            if self.snakeCollision.bothSectorCollision():
                # Double backwards
                self.moving = self.snake.moveBacwards()
                self.readyToMoveForward = False
                self.readyToMoveBackward = True
            # Checking left sector
            elif self.snakeCollision.leftSectorCollision():
                # Lateral shift right, ready to move backwards
                self.moving = self.snake.moveRight()
                self.readyToMoveForward = False
                self.readyToMoveBackward = True
            # Checking right sector
            elif self.snakeCollision.rightSectorCollision():
                # Lateral shift left, ready to move backwards
                self.moving = self.snake.moveLeft()
                self.readyToMoveForward = False
                self.readyToMoveBackward = True
            # If only collision in front
            else:
                # Back it up motherfucker
                self.moving = self.snake.reset()
                self.readyToMoveForward = False
                self.readyToMoveBackward = True
        # Checking for back
        elif not self.snakeCollision.backBackCollision:
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
                self.moving = self.snake.moveRight()
                self.readyToMoveForward = False
                self.readyToMoveBackward = False
            # Checking right sector
            elif self.snakeCollision.rightSectorCollision():
                # Reset moving flags, and lateral shift left
                self.moving = self.snake.moveLeft()
                self.readyToMoveBackward = False
                self.readyToMoveForward = False


    def seekAndDestroy(self):
        """
        Gets the snake to move towards all the targets.
        :return: Nothing
        """
        # Update GUI #############################
        pic = self.cam.takePicture()
        colorPic = drawLines(pic, self.finalPath, (255, 0, 0))
        self.notifyGui("UpdateImageEventR", colorPic)
        ##########################################

        # returns if the snake is not ready to receive a command ####
        cmdDone = self.snake.isCommandDone()
        """
        If the snake returns that the last command is done, sets moving flag to false again.
        On the first loop this will pass because of OverrideMoving-flag to set moving to false.
        """
        if cmdDone or self.overrideMoving:
            self.moving = False
            self.overrideMoving = False

        """
        Checks if the snake is in movement, if not in movement, checks if it is ready to move.
        If ready to move, sends command to snake to move forward one cycle.
        """
        if self.moving:
            pass

        elif self.readyToMoveForward:
            self.moving = self.snake.moveForward()
            self.readyToMoveForward = False
            # return
        else:
            lineStart = self.finalPath[self.j][self.i]
            lineEnd = self.finalPath[self.j][self.i + 1]

            """
            Runs only on the first loop of the run.
            Adjusts the start angle before movement starts
            """
            if self.firstLoop:
                # Find snake coordinates, and the masked picture
                snakeCoordinates, maskPic = self.findSnake.LocateSnakeAverage(1, 1)

                # Check that the snake coordinates are found
                if snakeCoordinates:
                    self.firstLoop = False
                    snakePointF = snakeCoordinates[1]
                    snakePointB = snakeCoordinates[0]

                    lV, sV, lVxsV = self.snakeController.calculateLineVectors(lineStart, lineEnd, snakePointB,
                                                                              snakePointF)
                    snakeAngle = self.snakeController.calculateFirstTurnAngle(lV, sV, lVxsV)
                    self.moving = self.snake.turn(snakeAngle)

                    # Update GUI
                    self.notifyGui("UpdateImageEventL", maskPic)

            ############################################################################
            # Gets the location of the snake, and calculates vectors for path to follow
            # as well as vector for snake. Draws path on the masked picture.
            # Makes the snake turn or ready to move depending on its angle.
            ############################################################################
            else:
                # Get snake coordinates and the masked picture
                snakeCoordinates, maskPic = self.findSnake.LocateSnakeAverage(1, 1)
                # Check that the snake is found
                if snakeCoordinates:
                    snakePointF = snakeCoordinates[1]
                    snakePointB = snakeCoordinates[0]
                    lV, sV, lVxsV = self.snakeController.calculateLineVectors(lineStart, lineEnd, snakePointB,
                                                                              snakePointF)

                    # Update GUI with path on the masked picture
                    if len(self.traveledPath) > 1:
                        maskPic = drawLines(maskPic, self.traveledPath, (0, 255, 0))
                    self.notifyGui("UpdateImageEventL", maskPic)

                    # Checks if the snake has reached a new node
                    snakeLine, finishLine = self.snakeController.calculateLines(lV, sV, lineEnd, snakePointF)
                    if self.snakeController.intersect(finishLine[0], finishLine[1], snakeLine[0], snakeLine[1]):
                        self.i += 1

                    # Checks if the snake has reached the goal
                    if self.i >= len(self.finalPath[self.j]) - 1:
                        self.snake.stop()
                        print("Stop")
                        Logger.logg("Snake reached first goal", Logger.info)
                        self.firstLoop = True
                        with b.lock:
                            b.runFlag = False
                            self.i = 0
                            self.j += 1
                    if self.j >= len(self.finalPath) - 1:
                        self.snake.stop()
                        print("Stop")
                        Logger.logg("Snake reached last goal", Logger.info)
                        self.firstLoop = False
                        with b.lock:
                            b.runFlag = False
                            self.i = 0
                            self.j = 0

                    # Gets the turn angle for the snake in relation to the path
                    turnAngle = self.snakeController.smartTurn(lV, sV, lVxsV, snakePointF, lineStart, 0.5, 20)
                    # self.notifyGui("UpdateTextEvent", f"curent angle {turnAngle}")

                    # If the turn angle returns a string, it does a lateral shift left/right depending on the string
                    if isinstance(turnAngle, str):
                        if turnAngle == "right":
                            self.moving = self.snake.moveRight()
                        elif turnAngle == "left":
                            self.moving = self.snake.moveLeft()

                    # If no lateral shift, applies turning, and sets moving and ready to move-flag to True
                    else:
                        self.moving = self.snake.turn(turnAngle)
                        self.readyToMoveForward = True
                    # Appends the new position of the snake to its traveled path
                    self.traveledPath.append(snakePointF)

    def run(self) -> None:
        """
        Main function of the controller. This runs continuously.
        :return:
        """
        Logger.logg("Controller thread started successfully", Logger.info)

        while self.running:

            b.lock.acquire()
            if b.stopFlag:
                self.snake.stop()
                self.overrideMoving = True
                b.autoFlag = False
                b.startFlag = False
                b.runFlag = False
                b.moveCmd = ""
                b.stopFlag = False
                b.lock.release()
            else:
                b.lock.release()

            b.lock.acquire()
            if b.updateParamFlag:
                b.updateParamFlag = False
                params = b.params
                b.lock.release()
                self.snake.setAmplitude(params[0])
                self.snake.setSpeed(params[1])
            else:
                b.lock.release()

            b.lock.acquire()
            if b.runFlag:
                b.lock.release()
                self.goToTarget()
                # b.yoloFlag = True
            else:
                b.lock.release()

            b.lock.acquire()
            if b.prepMaze:
                b.lock.release()
                self.prepMaze()
                b.prepMaze = False
            else:
                b.lock.release()

            b.lock.acquire()
            if b.findPathFlag:
                b.lock.release()
                self.findPath()
                b.findPathFlag = False
            else:
                b.lock.release()

            b.lock.acquire()
            if b.manualControlFlag:
                b.lock.release()
                self.moveSnakeManually()
            elif b.autoFlag:
                b.lock.release()
                self.autoMode()  # auto move code hear
            else:
                b.lock.release()

            with b.quitLock:
                if b.quitFlag:
                    self.running = False

            soplebil.collect()

        Camera.releaseCam()
        Logger.logg("Controller thread shutting down", Logger.info)
