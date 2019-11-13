import threading
import numpy as np
from shapely.geometry import Point, LineString
import time
from Bison.Broker import Broker as b
from Bison.ImageProcessing.maze_recogn import mazeRecognizer
from Bison.Pathfinding.rrt_star import RRTStar
from Bison.GUI import CustomEvent
from Bison.logger import Logger
from Bison.Movement.Snake import Snake
from Bison.ImageProcessing.camera import Camera
from Bison.ImageProcessing.findSnake import FindSnake
from Bison.Movement.snakeController import SnakeController
from Bison.ImageProcessing.findTarget import FindTarget
from Bison.ImageProcessing.Draw import drawLines


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
        self.overrideMoving = True
        self.moving = False
        self.readyToMove = False
        self.firstLoop = True
        self.i = 0
        self.curantAngle = 0
        self.traveledPath = []
        self.cam = Camera()
        self.snake = Snake("http://192.168.137.72", "192.168.137.196")
        #time.sleep(1)
        #print(self.snake.setAmplitude(30))
        #print(self.snake.setSpeed(10))
        #############################################

    def notifyGui(self, event, arg):
        updateEvent = CustomEvent(self.guiEvents[event], self.guiId())
        updateEvent.SetMyVal(arg)
        self.guiEventhandler(updateEvent)

    def prepMaze(self):
        self.notifyGui("UpdateTextEvent", "Preparing Maze")
        self.lines, self.lineImageArray = self.maze.findMaze()

        self.notifyGui("UpdateImageEventR", self.lineImageArray)
        self.notifyGui("UpdateTextEvent", "Maze Ready")

    def findPath(self):
        self.notifyGui("UpdateTextEvent", "Findig path...")
        try:
            cords, temp = self.findSnake.LocateSnake(self.cam.takePicture())
            startX = cords[0][0]
            startY = cords[0][1]

            d, frame, radius, center = self.finTarget.getTarget(self.cam.takePicture())
            goalX = center[0]
            goalY = center[1]
        except TypeError:
            self.notifyGui("UpdateTextEvent", "fukt")
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
        else:
            self.notifyGui("UpdateTextEvent", "Fani ikke path")

        self.traveledPath = []

        self.notifyGui("UpdateImageEventL", temp)
        self.notifyGui("UpdateImageEventR", self.rrtPathImage)

    def moveSnakeManually(self):
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

    def yolo(self):
        """
        Put yolo test code her!!!!!!!!!
        :return: yolo
        """
        # Update GUI #############################
        pic = self.cam.takePicture()
        colorPic = drawLines(pic, self.finalPath, (255, 0, 0))
        self.notifyGui("UpdateImageEventR", colorPic)
        ##########################################

        # returns if the snake is not redy to reacev a comand ####
        cmdDone = self.snake.isCommandDone()
        if cmdDone or self.overrideMoving:
            self.moving = False
            self.overrideMoving = False

        if self.moving:
            pass
        ##########################################################
        elif self.readyToMove:
            self.moving = self.snake.moveForward()
            self.readyToMove = False
            # return
        else:
            lineStart = self.finalPath[self.i]
            lineEnd = self.finalPath[self.i + 1]

            # Runs ony when the snake starts ###############################
            if self.firstLoop:
                snakeCoordinates, maskPic = self.findSnake.LocateSnakeAverage(1, 1)
                if snakeCoordinates:
                    self.firstLoop = False
                    snakePointF = snakeCoordinates[1]
                    snakePointB = snakeCoordinates[0]

                    lV, sV, lVxsV = self.snakeController.calculateLineVectors(lineStart, lineEnd, snakePointB,
                                                                              snakePointF)
                    snakeAngle = self.snakeController.calculateTheta(lV, sV, lVxsV)
                    self.moving = self.snake.turn(snakeAngle)

                    # Update GUI #############################
                    self.notifyGui("UpdateImageEventL", maskPic)
                    ##########################################
            #################################################################
            else:
                snakeCoordinates, maskPic = self.findSnake.LocateSnakeAverage(1, 1)
                if snakeCoordinates:
                    snakePointF = snakeCoordinates[1]
                    snakePointB = snakeCoordinates[0]
                    lV, sV, lVxsV = self.snakeController.calculateLineVectors(lineStart, lineEnd, snakePointB,
                                                                              snakePointF)

                    # Update GUI #############################
                    if len(self.traveledPath) > 1:
                        maskPic = drawLines(maskPic, self.traveledPath, (0, 255, 0))
                    self.notifyGui("UpdateImageEventL", maskPic)
                    ##########################################

                    # cheks if the snake has reatcht a new node ##############################################
                    snakeLine, finishLine = self.snakeController.calculateLines(lV, sV, lineEnd, snakePointF)
                    if self.snakeController.intersect(finishLine[0], finishLine[1], snakeLine[0], snakeLine[1]):
                        self.i += 1

                    if self.i >= len(self.finalPath) - 1:
                        self.snake.stop()
                        print("Stop")
                        Logger.logg("Snake reached goal", Logger.info)
                        self.firstLoop = False
                        with b.lock:
                            b.runFlag = False
                            self.i = 0
                    ##########################################################################################
                    turnAngle = self.snakeController.smartTurn(lV, sV, lVxsV, snakePointF, lineStart, 0.5, 20, 150)
                    # self.notifyGui("UpdateTextEvent", f"curent angle {turnAngle}")
                    if isinstance(turnAngle, str):
                        if turnAngle == "right":
                            self.moving = self.snake.moveRight()
                        elif turnAngle == "left":
                            self.moving = self.snake.moveLeft()
                    else:
                        self.moving = self.snake.turn(turnAngle)
                        self.readyToMove = True
                    self.traveledPath.append(snakePointF)

    def run(self) -> None:
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
            if b.startFlag:
                b.lock.release()
                # cheks if the steps has already been done
                if not self.lines:
                    self.prepMaze()
                if not self.rrtPathImage:
                    self.findPath()
                b.startFlag = False
            else:
                b.lock.release()

            b.lock.acquire()
            if b.runFlag:
                b.lock.release()
                self.yolo()
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

        Camera.releaseCam()
        Logger.logg("Controller thread shutting down", Logger.info)
