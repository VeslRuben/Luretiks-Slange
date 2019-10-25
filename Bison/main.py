from Bison.ImageProcessing.maze_recogn import mazeRecognizer
from Bison.Pathfinding.rrt_star import RRTStar
import os



maze = mazeRecognizer()


lines = maze.runshit()

# Set Initial parameters
rrtStar = RRTStar(start=[800, 250], goal=[650, 600], rand_area_x=[600, 1500], rand_area_y=[100, 1000], lineList=lines,
                  expand_dis=50.0, path_resolution=10, max_iter=1000, goal_sample_rate=5, connect_circle_dist=400)

rrtStar.run()

