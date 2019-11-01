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
import cv2


class Controller(threading.Thread):

    def setup(self):
        Camera.initCam(0)

    def __init__(self, eventData):
        super().__init__()
        self.setup()

        self.running = True
        self.i = 0
        self.moving = False

        self.cam = Camera()

        self.snake = Snake("http://192.168.137.171", "192.168.137.60")

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
        self.rrtStar = RRTStar(start=[x, y], goal=[1200, 400], rand_area_x=[250, 1500], rand_area_y=[0, 1100],
                               lineList=self.lines,
                               expand_dis=100.0, path_resolution=10.0, max_iter=500, goal_sample_rate=20,
                               connect_circle_dist=450,
                               edge_dist=30)
        self.rrtStar.lineList = self.lines
        self.rrtPathImage, self.finalPath = self.rrtStar.run()
        if self.finalPath is not None:
            self.finalPath = self.finalPath[::-1]
        else:
            self.notifyGui("UpdateTextEvent", "Fani ikke path")

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

    def ccw(self, A, B, C):
        return (C[1] - A[1]) * (B[0] - A[0]) > (B[1] - A[1]) * (C[0] - A[0])

    # Return true if line segments AB and CD intersect
    def intersect(self, A, B, C, D):
        return self.ccw(A, C, D) != self.ccw(B, C, D) and self.ccw(A, B, C) != self.ccw(A, B, D)

    def yolo(self):
        """
        Put yolo test code her!!!!!!!!!
        :return: yolo
        """
        if not self.moving:
            self.snake.moveForward()
            self.moving = True
        start = self.finalPath[self.i]
        nextNode = self.finalPath[self.i + 1]
        lV = [nextNode[0] - start[0], nextNode[1] - start[1]]

        snakeCords, maskPic = self.findSnake.LocateSnake(self.cam.takePicture())
        self.notifyGui("UpdateImageEventL", maskPic)
        if snakeCords is not None:
            s0 = snakeCords[0]
            s1 = snakeCords[1]
            sV = [s1[0] - s0[0], s1[1] - s0[1]]
            lVxsV = lV[0] * sV[1] - lV[1] * sV[0]
            theta = math.acos((lV[0] * sV[0] + lV[1] * sV[1]) / (
                    math.sqrt(lV[0] ** 2 + lV[1] ** 2) * math.sqrt(sV[0] ** 2 + sV[1] ** 2)))
            theta = (theta * (lVxsV / abs(lVxsV))) * 180 / math.pi  # (lVxsV / abs(lVxsV)) is 1 or -1
            print("Final theta ", theta)

            finithVektor = [lV[1], -lV[0]]
            skalar = 10
            finithLine = [[nextNode[0] + (finithVektor[0] * skalar), nextNode[1] + (finithVektor[1] * skalar)],
                          [nextNode[0] + (-finithVektor[0] * skalar), nextNode[1] + (-finithVektor[1] * skalar)]]
            snakLine = [s1, [s1[0] + (-sV[0]) * skalar, s1[1] + (-sV[1]) * skalar]]
            print(f"finith line {finithLine}")
            print(f"Snake line {snakLine}")
            print(f"sv {sV}")

            self.snake.turn(int(theta * 0.5))
            if self.intersect(finithLine[0], finithLine[1], snakLine[0], snakLine[1]):
                self.i += 1
                print(f"line: {self.i}")

        print(f" len lines: {len(self.finalPath)}")
        if self.i >= len(self.finalPath) - 1:
            self.snake.stop()
            print("stop")
            with b.lock:
                b.yoloFlag = False
                self.i = 0
                self.moving = False
        time.sleep(1)

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
