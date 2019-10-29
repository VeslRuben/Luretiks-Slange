import time

import numpy as np
from Bison.ImageProcessing.maze_recogn import mazeRecognizer
from Bison.Pathfinding.rrt_star import RRTStar
import matplotlib.pyplot as plt
import os
from Bison.GUI import GUI, CostumEvent
import threading

maze = mazeRecognizer()
lines = maze.runshit()

#Set Initial parameters
rrtStar = RRTStar(start=[825, 250], goal=[1450, 600], rand_area_x=[600, 1500], rand_area_y=[100, 1000], lineList=lines,
                  expand_dis=100.0, path_resolution=10.0, max_iter=500, goal_sample_rate=20, connect_circle_dist=450,
                  edge_dist=30)

gui = GUI()
evenData = gui.getEventInfo()
t = threading.Thread(target=rrtStar.run, args=(evenData,))
t.start()
gui.run()



# rrtStar.run()
