import gc as soplebil
import math
import threading
import time
import pickle
import cv2

from Bison.Broker import Broker as b
from Bison.GUI import CustomEvent
from Bison.ImageProcessing.Draw import drawLines, drawSection, drawSeveralLines
from Bison.ImageProcessing.camera import Camera
from Bison.ImageProcessing.findSnake import FindSnake
from Bison.ImageProcessing.findTarget import FindTarget
from Bison.ImageProcessing.maze_recogn import mazeRecognizer
from Bison.ImageProcessing.cheakPathForObs import cheakPathForObs
from Bison.Movement.Snake import Snake
from Bison.Movement.snakeController import SnakeController, SnakeCollision
from Bison.Pathfinding.rrt_star import RRTStar, multiRRTStar
from Bison.logger import Logger
from Bison.ImageProcessing.Dead import Dead


class Controller(threading.Thread):

    def __init__(self, eventData):
        super().__init__()
        Camera.initCam(0)
        self.running = True

        self.guiEvents = eventData["events"]
        self.guiId = eventData["id"]
        self.guiEventhandler = eventData["eventHandler"]

        # Mase Recognizer varibels ########
        self.maze = mazeRecognizer()
        self.lines = None
        self.lineImageArray = None

        self.deadEnds = Dead()
        self.listOfDeadEnds = None
        ###################################

        # RRT* Variabels ##################
        self.rrtStar = None
        self.multiRrtStar = multiRRTStar(rand_area_x=[500, 1600], rand_area_y=[0, 1100],
                                         lineList=None, expand_dis=100.0, path_resolution=10.0, max_iter=2000,
                                         goal_sample_rate=30,
                                         edge_dist=30, connect_circle_dist=800, start_point=None, listOfDeadEnds=None)
        self.rrtPathImage = None
        self.findSnake = FindSnake()
        self.finTarget = FindTarget()
        self.finalPath = None
        ###################################

        # Snake variables ###########################
        self.snakeController = SnakeController()
        self.snakeCollision = SnakeCollision(None, -105, -45, 45, 105, -75, -105, 75, 105, 0, 0, 0, 0)
        self.pizzaSlices = [[[15 + 180, -15 + 180], [-165 + 180, -195 + 180]],
                            [[15 + 180, -45 + 180], [45, 135], [-135 + 180, -195 + 180]]]
        self.overrideMoving = True
        self.readyToMoveForward = False
        self.readyToMoveBackward = False
        self.targetAccuaierd = False
        self.cmdDoneTimer = 5
        self.lastCmdSent = 0
        self.ampChanged = False
        self.seekDistance = 200
        self.deadBand = 80
        self.deadBandAngle = 50
        self.collisionDistance = 75
        self.moving = False
        self.firstLoop = True
        self.colliding = False
        self.i = 0
        self.j = 0
        self.traveledPath = []
        self.cam = Camera()
        self.snake = Snake("http://192.168.137.66", "192.168.137.83")
        #self.snake.setFrameSize(7)
        self.snakeObstacle = cheakPathForObs()
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

    def prepMazeSingle(self):
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

    def findPathSingle(self):
        """
        Gets the location of the snake as well as the location of a goal, then
        starts the RRT*-algorithm to find the path through the maze from start to goal.
        Updates events in GUI to show a picture with the maze and found path.
        :return:
        """
        self.notifyGui("UpdateTextEvent", "Finding path single-target")
        temp = None
        startX = None
        startY = None
        try:
            cords, temp = self.findSnake.LocateSnake(self.cam.takePicture())
            startX = cords[0][0]
            startY = cords[0][1]
        except TypeError:
            self.notifyGui("UpdateTextEvent", "Could not find snake")
            return
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
                               expand_dis=100.0, path_resolution=10.0, max_iter=2000, goal_sample_rate=20,
                               connect_circle_dist=700,
                               edge_dist=self.collisionDistance)
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

    def prepMazeMulti(self):
        self.notifyGui("UpdateTextEvent", "Preparing Maze")
        self.lines, self.lineImageArray = self.maze.findMaze()
        self.snakeCollision.mazeLines = self.lines

        self.listOfDeadEnds, picDeadEnd = self.deadEnds.getDeadEnds2(self.cam.takePicture())
        self.multiRrtStar.lineList = self.lines
        self.multiRrtStar.listOfDeadEnds = self.listOfDeadEnds

        self.notifyGui("UpdateImageEventR", self.lineImageArray)
        self.notifyGui("UpdateImageEventL", cv2.cvtColor(picDeadEnd, cv2.COLOR_BGR2RGB))
        self.notifyGui("UpdateTextEvent", "Maze Ready")

    def findPathMulti(self):
        """self.notifyGui("UpdateTextEvent", "Finding path multi-target. This can take some time")
        temp = None
        startX = None
        startY = None

        try:
            cords, temp = self.findSnake.LocateSnake(self.cam.takePicture())
            startX = cords[0][0]
            startY = cords[0][1]
        except TypeError:
            self.notifyGui("UpdateTextEvent", "Could not find snake")
            return

        self.multiRrtStar.start_point = [startX, startY]
        try:
            self.finalPath = self.multiRrtStar.run()
        except TypeError:
            self.notifyGui("UpdateTextEvent", "Could not find path")
            return

        if self.finalPath is not None:
            self.notifyGui("UpdateTextEvent", "Path found!")
        else:
            self.notifyGui("UpdateTextEvent", "Could not find path")
            return

        self.traveledPath = []
        bilde = drawSeveralLines(self.cam.takePicture(), self.finalPath, (0, 0, 255))"""

        with open('parrot.pkl', 'rb') as f:
            self.finalPath = pickle.load(f)
        bilde = drawSeveralLines(self.cam.takePicture(), self.finalPath, (0, 0, 255))

        try:
            cords, temp = self.findSnake.LocateSnake(self.cam.takePicture())
        except TypeError:
            self.notifyGui("UpdateTextEvent", "Could not find snake")
            return

        self.notifyGui("UpdateImageEventL", cv2.cvtColor(temp, cv2.COLOR_BGR2RGB))
        self.notifyGui("UpdateImageEventR", bilde)

        #with open('parrot.pkl', 'wb') as f:
            #pickle.dump(self.finalPath, f)

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
        colorPic = self.cam.takePicture()

        snakeCoordinates, maskPic = self.findSnake.LocateSnakeAverage(1, 1, picture=colorPic)
        if snakeCoordinates:
            xVector = [1, 0]
            snakeVector = [snakeCoordinates[1][0] - snakeCoordinates[0][0],
                           snakeCoordinates[1][1] - snakeCoordinates[0][1]]
            xVxsV = xVector[0] * snakeVector[1] - xVector[1] * snakeVector[0]
            offset = self.snakeController.calculateTheta(xVector, snakeVector, xVxsV)
            self.snakeCollision.updateCollisions(snakeCoordinates, self.collisionDistance, offset)

            # Update GUI #############################
            colorPic = drawLines(colorPic, self.finalPath, (255, 0, 0))
            pizzaSlicesCollision = [[self.snakeCollision.midRightCollision, self.snakeCollision.midLeftCollision],
                                    [self.snakeCollision.frontRightCollision,
                                     self.snakeCollision.frontFrontCollision,
                                     self.snakeCollision.frontLeftCollision]]
            if offset < 0:
                offset += 360
            for pos, piece, coll in zip(snakeCoordinates, self.pizzaSlices, pizzaSlicesCollision):
                i = 0
                for startAngle, endAngle in piece:
                    if coll[i]:
                        color = (0, 0, 255)
                    else:
                        color = (0, 255, 0)
                    colorPic = drawSection(colorPic, tuple(pos), startAngle + offset - 90, endAngle + offset - 90,
                                           color, radius=self.collisionDistance)
                    i += 1
        colorPic = cv2.cvtColor(colorPic, cv2.COLOR_BGR2RGB)
        self.notifyGui("UpdateImageEventR", colorPic)
        ##########################################

        # returns if the snake is not ready to receive a command ####
        cmdDone = self.snake.isCommandDone()
        if self.moving and self.lastCmdSent + self.cmdDoneTimer < time.time():
            self.overrideMoving = True
            Logger.logg(f"No done message reacevd in {self.cmdDoneTimer} sec, overiding movment", Logger.info)
        """
        If the snake returns that the last command is done, sets moving flag to false again.
        On the first loop this will pass because of OverrideMoving-flag to set moving to false.
        """
        if cmdDone or self.overrideMoving:
            self.moving = False
            self.overrideMoving = False
            self.lastCmdSent = time.time()
            snakePic = self.snake.takePicture()
            self.colliding = self.snakeObstacle.FindObsInPath(snakePic)

        """
        Checks if the snake is in movement, if not in movement, checks if it is ready to move.
        If ready to move, sends command to snake to move forward one cycle.
        """
        if self.colliding:
            snakePic = self.snake.takePicture()
            self.colliding = self.snakeObstacle.FindObsInPath(snakePic)
            self.notifyGui("UpdateImageEventL", snakePic)
        elif self.moving:
            pass
        elif self.readyToMoveForward:
            if self.ampChanged:
                amp = None
                with b.lock:
                    amp = b.params[0]
                acc = self.snake.setAmplitude(amp)
                self.ampChanged = False
                Logger.logg(f"ampetude set back to {amp}, acc: {acc}", Logger.cmd)
            if snakeCoordinates:
                if not self.snakeCollision.frontFrontCollision:
                    self.moving = self.snake.moveForward()
                    self.readyToMoveForward = False
                else:
                    self.collisionHandling()
        elif self.readyToMoveBackward:
            if self.ampChanged:
                amp = None
                with b.lock:
                    amp = b.params[0]
                acc = self.snake.setAmplitude(amp)
                Logger.logg(f"ampetude set back to {amp}, acc: {acc}", Logger.cmd)
                self.ampChanged = False
            if snakeCoordinates:
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
        Logger.logg(f"Executing collison comand", Logger.info)
        if self.snakeCollision.frontFrontCollision:
            # Checking both sectors at once
            if self.snakeCollision.bothSectorCollision():
                # Double backwards
                self.moving = self.snake.moveBacwards()
                self.readyToMoveForward = False
                self.readyToMoveBackward = True
            # Checking left sector
            elif self.snakeCollision.leftSectorCollision():
                # Lateral shift right, ready to move backwards
                acc = self.snake.setAmplitude(15)
                Logger.logg(f"ampletude turnd down for lateral shift right, acc: {acc}", Logger.cmd)
                self.moving = self.snake.moveRight()
                self.ampChanged = True
                self.readyToMoveForward = False
                self.readyToMoveBackward = True
            # Checking right sector
            elif self.snakeCollision.rightSectorCollision():
                # Lateral shift left, ready to move backwards
                acc = self.snake.setAmplitude(15)
                Logger.logg(f"ampletude turnd down for lateral shift left, acc: {acc}", Logger.cmd)
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
                Logger.logg(f"ampletude turnd down for lateral shift right, acc: {acc}", Logger.cmd)
                self.moving = self.snake.moveRight()
                self.ampChanged = True
                self.readyToMoveForward = False
                self.readyToMoveBackward = False
            # Checking right sector
            elif self.snakeCollision.rightSectorCollision():
                # Reset moving flags, and lateral shift left
                acc = self.snake.setAmplitude(15)
                Logger.logg(f"ampletude turnd down for lateral shift left, acc: {acc}", Logger.cmd)
                self.moving = self.snake.moveLeft()
                self.ampChanged = True
                self.readyToMoveBackward = False
                self.readyToMoveForward = False

    def seekAndDestroy(self):
        """
        Gets the snake to move towards a target.
        :return: Nothing
        """
        colorPic = self.cam.takePicture()

        snakeCoordinates, maskPic = self.findSnake.LocateSnakeAverage(1, 1, picture=colorPic)
        if snakeCoordinates:
            xVector = [1, 0]
            snakeVector = [snakeCoordinates[1][0] - snakeCoordinates[0][0],
                           snakeCoordinates[1][1] - snakeCoordinates[0][1]]
            xVxsV = xVector[0] * snakeVector[1] - xVector[1] * snakeVector[0]
            offset = self.snakeController.calculateTheta(xVector, snakeVector, xVxsV)
            self.snakeCollision.updateCollisions(snakeCoordinates, self.collisionDistance, offset)

            # Update GUI #############################
            colorPic = drawSeveralLines(colorPic, self.finalPath, (255, 0, 0))
            pizzaSlicesCollision = [[self.snakeCollision.midRightCollision, self.snakeCollision.midLeftCollision],
                                    [self.snakeCollision.frontRightCollision,
                                     self.snakeCollision.frontFrontCollision,
                                     self.snakeCollision.frontLeftCollision]]
            if offset < 0:
                offset += 360
            for pos, piece, coll in zip(snakeCoordinates, self.pizzaSlices, pizzaSlicesCollision):
                i = 0
                for startAngle, endAngle in piece:
                    if coll[i]:
                        color = (0, 0, 255)
                    else:
                        color = (0, 255, 0)
                    colorPic = drawSection(colorPic, tuple(pos), startAngle + offset - 90, endAngle + offset - 90,
                                           color, radius=self.collisionDistance)
                    i += 1
        colorPic = cv2.cvtColor(colorPic, cv2.COLOR_BGR2RGB)
        self.notifyGui("UpdateImageEventR", colorPic)
        ##########################################

        # returns if the snake is not ready to receive a command ####
        cmdDone = self.snake.isCommandDone()
        if self.moving and self.lastCmdSent + self.cmdDoneTimer < time.time():
            self.overrideMoving = True
            Logger.logg(f"No done message received in {self.cmdDoneTimer} sec, overriding movement", Logger.info)

        """
        If the snake returns that the last command is done, sets moving flag to false again.
        On the first loop this will pass because of OverrideMoving-flag to set moving to false.
        """
        if cmdDone or self.overrideMoving:
            self.moving = False
            self.overrideMoving = False
            self.lastCmdSent = time.time()

        if snakeCoordinates:
            endPoint = self.finalPath[self.j][len(self.finalPath[self.j]) - 1]
            angleToEnd = self.snakeCollision.calculateAngleToNearestPointV2(snakeCoordinates, snakeCoordinates[1],
                                                                            endPoint)
            restOfPath = [self.finalPath[self.j][self.i + 1:len(self.finalPath[self.j]) - 1]]
            lenSnakeToEnd = self.calculateDistanceToGoal(snakeCoordinates[1], restOfPath)

            """
            Checks if the snake is in movement, if not in movement, checks if it is ready to move.
            If ready to move, sends command to snake to move forward one cycle.
            """
            if self.moving:
                pass
            elif self.readyToMoveForward:
                if self.ampChanged:
                    amp = None
                    with b.lock:
                        amp = b.params[0]
                    acc = self.snake.setAmplitude(amp)
                    self.ampChanged = False
                    Logger.logg(f"ampetude set back to {amp}, acc: {acc}", Logger.cmd)
                if snakeCoordinates:
                    if not self.snakeCollision.frontFrontCollision:
                        self.moving = self.snake.moveForward()
                        self.readyToMoveForward = False
                    else:
                        self.collisionHandling()
            elif self.readyToMoveBackward:
                if self.ampChanged:
                    amp = None
                    with b.lock:
                        amp = b.params[0]
                    acc = self.snake.setAmplitude(amp)
                    Logger.logg(f"ampetude set back to {amp}, acc: {acc}", Logger.cmd)
                    self.ampChanged = False
                if snakeCoordinates:
                    if not self.snakeCollision.backBackCollision:
                        self.moving = self.snake.moveBacwards()
                        self.readyToMoveBackward = False
                    else:
                        self.collisionHandling()
            elif self.targetAccuaierd:
                pass
            # Checks if the snake has reached the a dead end
            elif lenSnakeToEnd < self.seekDistance:
                if abs(angleToEnd) < 10:
                    self.targetAccuaierd = self.tagetAccu()
                    self.j += 1
                    self.i = 1
                else:
                    self.snake.turn(self.snakeController.currentAngle + angleToEnd)
            else:
                lineStart = self.finalPath[self.j][self.i]
                lineEnd = self.finalPath[self.j][self.i + 1]

                """
                Runs only on the first loop of the run.
                Adjusts the start angle before movement starts
                """
                if self.firstLoop:
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

                        """ Moving logic"""
                        theta = self.snakeController.calculateTheta(lV, sV, lVxsV)
                        distanceToLine = self.snakeController.calculatDistanceToLine(lV, snakePointF, lineStart)

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

    def tagetAccu(self) -> bool:
        pic = self.snake.takePicture()
        temp = self.finTarget.getTarget(pic)
        if temp:
            return True
        else:
            return False

    def calculateDistanceToGoal(self, snakeFrontCoordinates, restOfPath):
        sum = 0

        firstVector = [restOfPath[0][0] - snakeFrontCoordinates[0], restOfPath[0][1] - snakeFrontCoordinates[1]]
        sum += math.sqrt(firstVector[0] ** 2 + firstVector[1] ** 2)

        for i in range(len(restOfPath) - 2):
            vector = [restOfPath[i + 1][0] - restOfPath[i][0], restOfPath[i + 1][1] - restOfPath[i][1]]

            sum += math.sqrt(vector[0] ** 2 + vector[1] ** 2)

        return sum

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
            if b.seekAndDestroyFlag:
                b.lock.release()
                self.seekAndDestroy()
            else:
                b.lock.release()

            b.lock.acquire()
            if b.prepMazeSingle:
                b.prepMazeSingle = False
                b.lock.release()
                self.prepMazeSingle()
            else:
                b.lock.release()

            b.lock.acquire()
            if b.prepMazeMulti:
                b.prepMazeMulti = False
                b.lock.release()
                self.prepMazeMulti()
            else:
                b.lock.release()

            b.lock.acquire()
            if b.findPathSingleFlag:
                b.findPathSingleFlag = False
                b.lock.release()
                self.findPathSingle()
            else:
                b.lock.release()

            b.lock.acquire()
            if b.findPathMultiFlag:
                b.findPathMultiFlag = False
                b.lock.release()
                self.findPathMulti()
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
