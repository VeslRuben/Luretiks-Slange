import math
import random
from shapely.geometry import LineString

import matplotlib.pyplot as plt
from matplotlib.path import Path
import numpy as np

show_animation = True

class RRT:

    class Node:
        def __init__(self, x, y):
            self.x = x
            self.y = y
            self.path_x = []
            self.path_y = []
            self.parent = None

    def __init__(self, start, goal, obstacle_list, rand_area, lineList, expand_dis=3.0,
                 path_resolution=0.5, goal_sample_rate=5, max_iter=500):
        self.start = self.Node(start[0], start[1])
        self.end = self.Node(goal[0], goal[1])
        self.min_rand = rand_area[0]
        self.max_rand = rand_area[1]
        self.expand_dis = expand_dis
        self.path_resolution = path_resolution
        self.goal_sample_rate = goal_sample_rate
        self.max_iter = max_iter
        self.obstacle_list = obstacle_list
        self.node_list = []
        self.lineList = lineList

    def planning(self, animation=True):
        """
        rrt path planning
        :param animation: flag for animation on or off
        """
        self.node_list = [self.start]
        for i in range(self.max_iter):
            rnd_node = self.get_random_node()
            nearest_ind = self.get_nearest_node_index(self.node_list, rnd_node)
            nearest_node = self.node_list[nearest_ind]

            new_node = self.steer(nearest_node, rnd_node, self.expand_dis)

            if self.checkObstacle(new_node, self.lineList):
                self.node_list.append(new_node)

            if animation and i % 5 == 0:
                self.draw_graph(rnd_node)

            if self.calc_dist_to_goal(self.node_list[-1].x, self.node_list[-1].y) <= self.expand_dis:
                final_node = self.steer(self.node_list[-1], self.end, self.expand_dis)
                if self.check_collision(final_node, self.obstacle_list):
                    return self.generate_final_course(len(self.node_list) - 1)

            if animation and i % 5:
                self.draw_graph(rnd_node)

        return None

    def steer(self, from_node, to_node, extend_length=float("inf")):
        new_node = self.Node(from_node.x, from_node.y)
        d, theta = self.calc_distance_and_angle(new_node, to_node)

        new_node.path_x = [new_node.x]
        new_node.path_y = [new_node.y]

        if extend_length > d:
            extend_length = d

        n_expand = math.floor(extend_length / self.path_resolution)

        for _ in range(n_expand):
            new_node.x += self.path_resolution * math.cos(theta)
            new_node.y += self.path_resolution * math.sin(theta)
            new_node.path_x.append(new_node.x)
            new_node.path_y.append(new_node.y)

        d, _ = self.calc_distance_and_angle(new_node, to_node)
        if d <= self.path_resolution:
            new_node.path_x.append(to_node.x)
            new_node.path_y.append(to_node.y)

        new_node.parent = from_node

        return new_node

    def draw_graph(self, rnd=None):
        plt.clf()
        if rnd is not None:
            plt.plot(rnd.x, rnd.y, "^k")
        for node in self.node_list:
            if node.parent:
                plt.plot(node.path_x, node.path_y, "-g")

        for (lx, ly, la, ll) in self.lineList:
            self.plot_obstacle(lx, ly, la, ll)

        #for (ox, oy, size) in self.obstacle_list:
        #    self.plot_circle(ox, oy, size)

        plt.plot(self.start.x, self.start.y, "xr")
        plt.plot(self.end.x, self.end.y, "xr")
        plt.axis("equal")
        plt.axis([-2, 15, -2, 15])
        plt.grid(False)
        plt.pause(0.01)

    def generate_final_course(self, goal_ind):
        path = [[self.end.x, self.end.y]]
        node = self.node_list[goal_ind]
        while node.parent is not None:
            path.append([node.x, node.y])
            node = node.parent
        path.append([node.x, node.y])

        return path

    def calc_dist_to_goal(self, x ,y):
        dx = x - self.end.x
        dy = y - self.end.y
        return math.sqrt(dx ** 2 + dy ** 2)

    def get_random_node(self):
        if random.randint(0,100) > self.goal_sample_rate:
            rnd = self.Node(random.uniform(self.min_rand, self.max_rand),
                            random.uniform(self.min_rand, self.max_rand))
        else:
            rnd = self.Node(self.end.x, self.end.y)
        return rnd

    @staticmethod
    def plot_obstacle(x, y, angle, length):
        xangle = math.cos(np.deg2rad(angle))
        yangle = math.sin(np.deg2rad(angle))
        x2 = x+(length*xangle)
        y2 = y+(length*yangle)
        plt.plot([x, x2], [y, y2], color='k', linestyle='-', linewidth=2)

    @staticmethod
    def checkObstacle(node, lineList):
        dx_list = [x for x in node.path_x] # This includes the whole path
        dy_list = [y for y in node.path_y] # This includes points for the whole path
        node_line = LineString([(x, y) for (x,y) in zip(dx_list, dy_list)])
        for(lx, ly, la, ll) in lineList:
            obst = LineString([(lx, ly), (lx+(ll*math.cos(np.deg2rad(la))), ly+(ll*math.sin(np.deg2rad(la))))])
            if obst.intersects(node_line):
                return False
        return True

    @staticmethod
    def plot_circle(x, y, size, color="-b"):
        deg = list(range(0, 360, 5))
        deg.append(0)
        x1 = [x + size * math.cos(np.deg2rad(d)) for d in deg]
        y1 = [y + size * math.sin(np.deg2rad(d)) for d in deg]
        plt.plot(x1, y1, color)

    @staticmethod
    def get_nearest_node_index(node_list, rnd_node):
        dlist=[(node.x - rnd_node.x) ** 2 + (node.y - rnd_node.y)
               ** 2 for node in node_list]
        minind = dlist.index(min(dlist))

        return minind

    @staticmethod
    def check_collision(node, obstacleList):
        for(ox, oy, size) in obstacleList:
            dx_list = [ox - x for x in node.path_x]
            dy_list = [oy - y for y in node.path_y]
            d_list = [dx * dx + dy * dy for (dx, dy) in zip(dx_list, dy_list)]

            if min(d_list) <= size ** 2:
                return False

        return True

    @staticmethod
    def calc_distance_and_angle(from_node, to_node):
        dx = to_node.x - from_node.x
        dy = to_node.y - from_node.y
        d = math.sqrt(dx ** 2 + dy ** 2)
        theta = math.atan2(dy, dx)
        return d, theta

def main(gx=6.0, gy=10.0):
    print("Start" + __file__)


    # First four points are the maze walls
    lineList = [
        (-1, -1, 0, 12),
        (11, -1, 90, 12),
        (11, 11, 180, 12),
        (-1, 11, 270, 12),
        (3, -1, 90, 4),
        (-1, 1, 0, 2),
        (5, 8, 270, 7),
        (-1, 5, 0, 6),
        (5, 1, 0, 3)
    ]

    obstacleList = [
        (5, 5, 1),
        (3, 6, 2),
        (3, 8, 2),
        (3, 10, 2),
        (7, 5, 2),
        (9, 5, 2),
        (8, 10, 1)
    ]

    rrt = RRT(start=[0, 0], goal=[gx, gy],
              rand_area=[-2, 15],
              obstacle_list=obstacleList, lineList=lineList)
    path = rrt.planning(animation=show_animation)



    if path is None:
        print("Cannot find path")
    else:
        print("Found a path!")

        if show_animation:
            rrt.draw_graph()
            plt.plot([x for (x,y) in path], [y for (x, y) in path], '-r')
            plt.grid(True)
            plt.pause(0.01)
            plt.show()

if __name__ == '__main__':
    main()