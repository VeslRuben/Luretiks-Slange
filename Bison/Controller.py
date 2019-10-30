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
import math


class Controller(threading.Thread):

    def setup(self):
        Camera.initCam(0)

    def __init__(self, eventData):
        super().__init__()
        self.setup()

        self.running = True

        self.cam = Camera()

        self.snake = Snake("http://192.168.137.171", "192.168.137.12")

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
        self.finalPath = None
        ###################################

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
            x = cords[0][0]
            y = cords[0][1]
        except TypeError:
            self.notifyGui("UpdateTextEvent", "fukt")
            return
        self.rrtStar = RRTStar(start=[x, y], goal=[1350, 100], rand_area_x=[250, 1500], rand_area_y=[0, 1100],
                               lineList=self.lines,
                               expand_dis=100.0, path_resolution=10.0, max_iter=500, goal_sample_rate=20,
                               connect_circle_dist=450,
                               edge_dist=30)
        self.rrtStar.lineList = self.lines
        self.rrtPathImage, self.finalPath = self.rrtStar.run()
        self.finalPath = self.finalPath[::-1]

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
                elif b.moveCmd == "r":
                    self.snake.moveRight()
                elif b.moveCmd == "l":
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
        start = self.finalPath[0]
        nextNode = self.finalPath[1]

        startPoint = Point(start[0], start[1])
        nodePos = Point(nextNode[0], nextNode[1])

        movingLine = LineString([(start[0], start[1]), (nextNode[0], nextNode[1])])

        thetaLine = (math.asinh(
            (nextNode[1] - start[1]) / math.sqrt((nextNode[0] - start[0]) ** 2 + (nextNode[1] - start[1]) ** 2))) * (
                                180 / math.pi)
        print("tetha line: ", thetaLine)

        # self.snake.moveForward()
        temp = self.findSnake.LocateSnake(self.cam.takePicture())
        if temp is not None:
            cords, yolo = temp
            p0 = cords[0]
            p1 = cords[1]
            self.notifyGui("UpdateImageEventL", yolo)
            snakePos = Point(p0[0], p0[1])
            print("pos", p0)
            distanceToLine = movingLine.distance(snakePos)
            try:
                thetaSnake = (math.asinh((y - start[1]) / math.sqrt((x - start[0]) ** 2 + (y - start[1]) ** 2))) * (
                            180 / math.pi)
            except ZeroDivisionError:
                thetaSnake = thetaLine

            print("snake tehta ", thetaSnake)

            # sving kode her

            distToNode = snakePos.distance(nodePos)
            if distToNode < 10:
                self.snake.stop()
                print("stop")
                with b.lock:
                    b.yoloFlag = False
        time.sleep(0.3)

    def run(self) -> None:
        Logger.logg("Controller thread started successfully", Logger.info)

        while self.running:

            b.lock.acquire()
            if b.stopFlag:
                self.snake.stop()
                b.autoFlag = False
                b.startFlag = False
                b.yoloFlag = False
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
            if b.yoloFlag:
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
