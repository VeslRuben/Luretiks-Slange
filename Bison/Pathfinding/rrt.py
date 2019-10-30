import math
import random
from shapely.geometry import LineString

import matplotlib.pyplot as plt

show_animation = False
show_final_animation = True


class RRT:

    class Node:
        def __init__(self, x, y):
            self.x = x
            self.y = y
            self.path_x = []
            self.path_y = []
            self.parent = None

    def __init__(self, start, goal, rand_area_x, rand_area_y, lineList, edge_dist, expand_dis=0.5,
                 path_resolution=0.1, goal_sample_rate=5, max_iter=7000):
        self.start = self.Node(start[0], start[1])
        self.end = self.Node(goal[0], goal[1])
        self.min_rand_x = rand_area_x[0]
        self.max_rand_x = rand_area_x[1]
        self.min_rand_y = rand_area_y[0]
        self.max_rand_y = rand_area_y[1]
        self.expand_dis = expand_dis
        self.path_resolution = path_resolution
        self.goal_sample_rate = goal_sample_rate
        self.max_iter = max_iter
        self.node_list = []
        self.lineList = lineList
        self.edge_dist = edge_dist

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

            if self.checkObstaclev2(new_node, self.lineList, self.edge_dist):
                self.node_list.append(new_node)

            if animation and i % 5 == 0:
                self.draw_graph(rnd_node)

            if self.calc_dist_to_goal(self.node_list[-1].x, self.node_list[-1].y) <= self.expand_dis:
                final_node = self.steer(self.node_list[-1], self.end, self.expand_dis)
                if self.checkObstaclev2(final_node, self.lineList, self.edge_dist):
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
        #print(n_expand)

        for _ in range(n_expand):
            new_node.x += self.path_resolution * math.cos(theta)
            #print(self.path_resolution * math.cos(theta))
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

        for (data) in self.lineList:
            x1 = data[0][0]
            y1 = data[0][1]
            x2 = data[0][2]
            y2 = data[0][3]
            self.plotObstaclev2(x1, y1, x2, y2)

        plt.plot(self.start.x, self.start.y, "xr")
        plt.plot(self.end.x, self.end.y, "xr")
        plt.axis("equal")
        plt.axis([0, 1920, 0, 1080])
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
            rnd = self.Node(random.uniform(self.min_rand_x, self.max_rand_x),
                            random.uniform(self.min_rand_y, self.max_rand_y))
        else:
            rnd = self.Node(self.end.x, self.end.y)
        return rnd

    @staticmethod
    def plotObstaclev2(x1, y1, x2, y2):
        plt.plot([x1, x2], [y1, y2], color='k', linestyle='-', linewidth=1)

    @staticmethod
    def checkObstaclev2(node, lineList, edgeDistance):
        dx_list = [x for x in node.path_x]
        dy_list = [y for y in node.path_y]
        node_line = LineString([(x, y) for (x,y) in zip(dx_list, dy_list)])
        for data in lineList:
            x1 = data[0][0]
            y1 = data[0][1]
            x2 = data[0][2]
            y2 = data[0][3]
            obst = LineString([(x1, y1), (x2, y2)])
            if obst.intersects(node_line):
                return False
            if obst.distance(node_line) < edgeDistance:
                return False
        return True

    @staticmethod
    def get_nearest_node_index(node_list, rnd_node):
        dlist=[(node.x - rnd_node.x) ** 2 + (node.y - rnd_node.y)
               ** 2 for node in node_list]
        minind = dlist.index(min(dlist))

        return minind

    @staticmethod
    def calc_distance_and_angle(from_node, to_node):
        dx = to_node.x - from_node.x
        dy = to_node.y - from_node.y
        d = math.sqrt(dx ** 2 + dy ** 2)
        theta = math.atan2(dy, dx)
        return d, theta

def main(gx=1.1, gy=10.0, exp_dist=0.5):
    print("Start" + __file__)

if __name__ == '__main__':
    main()