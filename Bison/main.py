import time

import numpy as np
from Bison.ImageProcessing.maze_recogn import mazeRecognizer
from Bison.Pathfinding.rrt_star import RRTStar
import matplotlib.pyplot as plt
import os
from Bison.GUI import GUI, CostumEvent
import threading


def yolo(evenData):
    time.sleep(3)
    fig = plt.figure()
    fig.add_subplot(111)
    plt.plot([4,5],[1,2])
    plt.show()
    fig.canvas.draw()


    data = np.fromstring(fig.canvas.tostring_rgb(), dtype=np.uint8, sep='')
    data = data.reshape(fig.canvas.get_width_height()[::-1] + (3,))

    event = evenData["events"]["UpdateImageEventR"]
    eventhandler = evenData["eventHandler"]
    id = evenData["id"]

    yoloEvent = CostumEvent(event, id())
    yoloEvent.SetMyVal(data)
    eventhandler(yoloEvent)
    print("sent")


gui = GUI()
evenData = gui.getEventInfo()
t = threading.Thread(target=yolo, args=(evenData,))
t.start()
gui.run()


# maze = mazeRecognizer()
# lines = maze.runshit()
# Set Initial parameters
# rrtStar = RRTStar(start=[825, 250], goal=[1250, 120], rand_area_x=[600, 1500], rand_area_y=[100, 1000], lineList=lines,
#                  expand_dis=100.0, path_resolution=10.0, max_iter=500, goal_sample_rate=20, connect_circle_dist=450,
#                  edge_dist=30)
# rrtStar.run()
