"""
The class that has the main responsibility for all other functions of the program.

author: Håkon Bjerkgaard Waldum, Ruben Svedal Jørundland, Marcus Olai Grindvik
"""

import gc as garbageCollector
import threading
import time
import pickle
import cv2

from Python.broker import Broker as b
from Python.GUI import CustomEvent
from Python.ImageProcessing.draw import drawLines, drawSeveralLines, drawCollisionSectors
from Python.ImageProcessing.camera import Camera
from Python.ImageProcessing.findSnake import FindSnake
from Python.ImageProcessing.findTarget import FindTarget
from Python.ImageProcessing.mazeRecognizer import mazeRecognizer
from Python.Movement.snake import Snake
from Python.Movement.snakeMethods import SnakeCollision
from Python.Pathfinding.rrt_star import RRTStar, multiRRTStar
from Python.logger import Logger
from Python.ImageProcessing.deadEndDetector import DeadEndDetector
from Python.Movement.goToTarget import GoToTarget
from Python.Movement.seekAndDestroy import SeekAndDestroy


class Controller(threading.Thread):

    def __init__(self, eventData):
        super().__init__()
        Camera.initCam(0)
        self.running = True

        self.guiEvents = eventData["events"]
        self.guiId = eventData["id"]
        self.guiEventhandler = eventData["eventHandler"]
        self.eventData = eventData

        # Mase Recognizer varibels ########
        self.maze = mazeRecognizer()
        self.lines = None
        self.lineImageArray = None

        self.deadEnds = DeadEndDetector()
        self.listOfDeadEnds = None
        ###################################

        # RRT* Variabels ##################
        self.rrtStar = None
        self.multiRrtStar = multiRRTStar(rand_area_x=[300, 1700], rand_area_y=[0, 1200],
                                         lineList=None, expand_dis=50.0, path_resolution=25.0, max_iter=2000,
                                         goal_sample_rate=10,
                                         edge_dist=30, connect_circle_dist=800, start_point=None, listOfDeadEnds=None)
        self.rrtPathImage = None
        self.findSnake = FindSnake()
        self.finTarget = FindTarget()
        self.finalPath = None
        ###################################

        # Snake Objects
        self.snakeCollision = SnakeCollision(None, -105, -45, 45, 105, -75, -105, 75, 105, 0, 0, 0, 0)
        self.collisionSectors = [[[15 + 180, -15 + 180], [-165 + 180, -195 + 180]],
                                 [[15 + 180, -45 + 180], [45, 135], [-135 + 180, -195 + 180]]]
        self.snake = Snake("http://192.168.137.87", "192.168.137.252")
        self.goToTarget = GoToTarget(None, self.snake, self.snakeCollision, 10, 45, 20, 80)
        self.seekAndDestroy = None
        self.cam = Camera()

        # Snake variables
        self.overrideMoving = True
        self.cmdDoneTimer = 5
        self.lastCmdSent = 0
        self.seekDistance = 200
        self.deadBand = 80
        self.deadBandAngle = 50
        self.collisionDistance = 75
        self.traveledPath = []
        # self.snake.setFrameSize(7)
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
        updateEvent.setArgument(arg)
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

        :return: None
        """
        self.notifyGui("UpdateTextEvent", "Finding path single-target")
        temp = None
        startX = None
        startY = None
        try:
            cords, temp = self.findSnake.locateSnake(self.cam.takePicture())
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
            self.goToTarget.path = self.finalPath
        else:
            self.notifyGui("UpdateTextEvent", "Could not find path")

        self.traveledPath = []

        self.notifyGui("UpdateImageEventL", temp)
        self.notifyGui("UpdateImageEventR", self.rrtPathImage)

        garbageCollector.collect()

    def prepMazeMulti(self):
        """
        Prepares the maze for multi-target. Finds dead ends and saves these in a list. Then gives the multiRRT the lines
        of the maze as well as the list of dead ends. Updates GUI with pictures of the maze with the lines and the
        dead ends.

        :return: None
        """
        self.notifyGui("UpdateTextEvent", "Preparing Maze")
        self.lines, self.lineImageArray = self.maze.findMaze()
        self.snakeCollision.mazeLines = self.lines

        self.listOfDeadEnds, picDeadEnd = self.deadEnds.getDeadEnds(self.cam.takePicture())
        self.multiRrtStar.lineList = self.lines
        self.multiRrtStar.listOfDeadEnds = self.listOfDeadEnds

        self.notifyGui("UpdateImageEventR", self.lineImageArray)
        self.notifyGui("UpdateImageEventL", cv2.cvtColor(picDeadEnd, cv2.COLOR_BGR2RGB))
        self.notifyGui("UpdateTextEvent", "Maze Ready")

    def findPathMulti(self):
        """
        Finds the snakes location and runs the multiRRT-method to find the most effective path between the dead ends.
        :return: None
        """
        self.notifyGui("UpdateTextEvent", "Finding path multi-target. This can take some time")
        temp = None
        startX = None
        startY = None

        try:
            cords, temp = self.findSnake.locateSnake(self.cam.takePicture())
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
            self.seekAndDestroy = SeekAndDestroy(self.finalPath, self.snake, self.snakeCollision, 10, 45, 20, 80,
                                                 self.eventData)
            self.seekAndDestroy.path = self.finalPath[0]
        else:
            self.notifyGui("UpdateTextEvent", "Could not find path")
            return

        self.traveledPath = []
        bilde = drawSeveralLines(self.cam.takePicture(), self.finalPath, (0, 0, 255))

        # with open('parrot.pkl', 'rb') as f:
        #     self.finalPath = pickle.load(f)
        # bilde = drawSeveralLines(self.cam.takePicture(), self.finalPath, (0, 0, 255))
        #
        # try:
        #     cords, temp = self.findSnake.locateSnake(self.cam.takePicture())
        # except TypeError:
        #     self.notifyGui("UpdateTextEvent", "Could not find snake")
        #     return

        self.notifyGui("UpdateImageEventL", cv2.cvtColor(temp, cv2.COLOR_BGR2RGB))
        self.notifyGui("UpdateImageEventR", bilde)

        # with open('parrot.pkl', 'wb') as f:
        # pickle.dump(self.finalPath, f)

        garbageCollector.collect()

    def runSingleTarget(self):
        """
        Gets the snake to move towards a target.

        :return: Nothing
        """
        colorPic = self.cam.takePicture()

        snakeCoordinates, maskPic = self.findSnake.locateSnakeAverage(1, 1, picture=colorPic)
        if snakeCoordinates:
            # Movement
            # returns false if the snake is not ready to receive a command
            cmdDone = self.goToTarget.isCommandDone()

            # Resets the moving flag if there is no acc inside a given time
            if self.goToTarget.moving and self.lastCmdSent + self.cmdDoneTimer < time.time():
                self.overrideMoving = True
                Logger.logg(f"No done message received in {self.cmdDoneTimer} sec, Overriding movement", Logger.info)

            if cmdDone or self.overrideMoving:
                # Reset override moving flag if active
                self.overrideMoving = False

                # Run go to target to make the movements
                self.goToTarget.run(snakeCoordinates, self.collisionDistance)

                # Set new timer
                self.lastCmdSent = time.time()

                # Appends the new position of the snake to its traveled path
                self.traveledPath.append(snakeCoordinates[1])
            else:
                pass

        self.drawGUIElements(snakeCoordinates, colorPic, maskPic)

    def runMultiTarget(self):
        """
        Gets the snake to go between the different dead ends to search for the target.
        :return: None
        """
        colorPic = self.cam.takePicture()

        snakeCoordinates, maskPic = self.findSnake.locateSnakeAverage(1, 1, picture=colorPic)
        if snakeCoordinates:
            # Movement
            # returns false if the snake is not ready to receive a command
            cmdDone = self.seekAndDestroy.isCommandDone()

            # Resets the moving flag if there is no acc inside a given time
            if self.seekAndDestroy.moving and self.lastCmdSent + self.cmdDoneTimer < time.time():
                self.overrideMoving = True
                Logger.logg(f"No done message received in {self.cmdDoneTimer} sec, Overriding movement", Logger.info)

            if cmdDone or self.overrideMoving:
                # Reset override moving flag if active
                self.overrideMoving = False

                # Run go to target to make the movements
                self.seekAndDestroy.run(snakeCoordinates, self.collisionDistance)

                # Set new timer
                self.lastCmdSent = time.time()

                # Appends the new position of the snake to its traveled path
                self.traveledPath.append(snakeCoordinates[1])
            else:
                pass

        self.drawGUIElements(snakeCoordinates, colorPic, maskPic)

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
                    self.snake.moveBackward()
                elif b.moveCmd == "h":
                    self.snake.moveRight()
                elif b.moveCmd == "v":
                    self.snake.moveLeft()
                elif b.moveCmd == "s":
                    self.snake.stop()
                elif b.moveCmd == "r":
                    self.snake.reset()
                b.moveCmd = ""

    def drawGUIElements(self, snakeCoordinates, colorPic, maskPic):
        """
        Updates the GUI with the pictures of the mask with the path ventured as well as the colored picture with the
        path to go.

        :param snakeCoordinates: List of coordinates of the snakes parts
        :param colorPic: Live picture of the maze
        :param maskPic: Picture of the result of the color thresholding of the snake
        :return: None
        """
        if snakeCoordinates:
            # Update GUI #############################
            offset = self.goToTarget.calculateOffset(snakeCoordinates)

            sectorCollisionsFlags = [[self.snakeCollision.midRightCollision, self.snakeCollision.midLeftCollision],
                                     [self.snakeCollision.frontRightCollision,
                                      self.snakeCollision.frontFrontCollision,
                                      self.snakeCollision.frontLeftCollision]]
            colorPic = drawCollisionSectors(colorPic, snakeCoordinates, self.collisionSectors, sectorCollisionsFlags,
                                            offset,
                                            self.collisionDistance)
        try:
            _ = self.finalPath[0][0][0]
            multi = True
        except TypeError:
            multi = False

        if multi:
            colorPic = drawSeveralLines(colorPic, self.finalPath, (255, 0, 0))
        else:
            colorPic = drawLines(colorPic, self.finalPath, (255, 0, 0))
        colorPic = cv2.cvtColor(colorPic, cv2.COLOR_BGR2RGB)
        self.notifyGui("UpdateImageEventR", colorPic)

        if len(self.traveledPath) > 1:
            maskPic = drawLines(maskPic, self.traveledPath, (0, 255, 0))
        self.notifyGui("UpdateImageEventL", maskPic)

    def run(self) -> None:
        """
        Main function of the controller. This runs continuously.

        :return: None
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
                self.runSingleTarget()
                # b.yoloFlag = True
            else:
                b.lock.release()

            b.lock.acquire()
            if b.seekAndDestroyFlag:
                b.lock.release()
                self.runMultiTarget()
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
            else:
                b.lock.release()

            with b.quitLock:
                if b.quitFlag:
                    self.running = False

            garbageCollector.collect()

        Camera.releaseCam()
        Logger.logg("Controller thread shutting down", Logger.info)
