import threading
from Bison.Broker import Broker as b
from Bison.ImageProcessing.maze_recogn import mazeRecognizer
from Bison.Pathfinding.rrt_star import RRTStar
from Bison.GUI import CostumEvent
from Bison.logger import Logger
from Bison.Movement.Snake import Snake
from Bison.ImageProcessing.camera import Camera


class Cotroller(threading.Thread):

    def setup(self):
        Camera.initCma(0)

    def __init__(self, eventData):
        super().__init__()
        self.setup()

        self.runing = True

        self.cam = Camera()

        self.snake = Snake("http://192.168.137.171", "192.168.137.159")

        self.guiEvents = eventData["events"]
        self.guiId = eventData["id"]
        self.guiEventhandler = eventData["eventHandler"]

        # Mase Recognizer varibels ########
        self.maze = mazeRecognizer()
        self.lines = None
        self.lineImageArray = None
        ###################################

        # RRT* Variabels ##################
        self.rrtStar = RRTStar(start=[825, 250], goal=[1450, 600], rand_area_x=[600, 1500], rand_area_y=[100, 1000],
                               lineList=self.lines,
                               expand_dis=100.0, path_resolution=10.0, max_iter=500, goal_sample_rate=20,
                               connect_circle_dist=450,
                               edge_dist=30)
        self.rrtPathImage = None
        ###################################

    def notifyGui(self, event, arg):
        updateEvent = CostumEvent(self.guiEvents[event], self.guiId())
        updateEvent.SetMyVal(arg)
        self.guiEventhandler(updateEvent)

    def prepMaze(self):
        self.notifyGui("UpdateTextEvent", "Preparing Maze")
        self.lines, self.lineImageArray = self.maze.runshit()

        self.notifyGui("UpdateImageEventR", self.lineImageArray)
        self.notifyGui("UpdateTextEvent", "Maze Ready")

    def findPath(self):
        self.notifyGui("UpdateTextEvent", "Findig path...")
        self.rrtStar.lineList = self.lines
        self.rrtPathImage = self.rrtStar.run()

        self.notifyGui("UpdateImageEventR", self.rrtPathImage)

    def moveSnakeManualy(self):
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
        frame = self.cam.takePictureRgb()
        self.notifyGui("UpdateImageEventL", frame)

    def run(self) -> None:
        Logger.logg("Controller thred started sucsefuly", Logger.info)

        while self.runing:

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
                b.yoloFlag = False
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
            if b.manulaControllFlag:
                b.lock.release()
                self.moveSnakeManualy()
            elif b.autoFlag:
                b.lock.release()
                self.autoMode()  # auto move code hear
            else:
                b.lock.release()

            with b.quitLock:
                if b.quitFlag:
                    self.runing = False

        Camera.realesCam()
        Logger.logg("Controller thred shuting down", Logger.info)
