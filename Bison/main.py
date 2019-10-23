from Bison.ImageProcessing.maze_recogn import mazeRecognizer
from Bison.Pathfinding.rrt_star import RRTStar


maze = mazeRecognizer()


lines = maze.runshit()

# Set Initial parameters
rrtStar = RRTStar(start=[670, 200], goal=[650, 600], rand_area=[0, 1080], lineList=lines)

rrtStar.run()

