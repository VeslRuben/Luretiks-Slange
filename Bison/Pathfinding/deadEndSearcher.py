import numpy as np
from shapely.geometry import LineString, Point
import cv2

class deadEndSearcher():

    class Node:
        def __init__(self, x, y):
            self.x_start = x
            self.y_start = y
            self.x_end = None
            self.y_end = None

    def __init__(self, start, lineList, edgeDistance, edgePic):
        self.start = self.Node(start[0], start[1])
        self.lineList = lineList
        self.edgeDistance = edgeDistance
        self.listOfDeadEnds = []
        self.edgePic = edgePic

    def findDeadEnds(self):
        node = self.start
        leftOk = self.moveLeft(node, 80)
        rightOk = self.moveRight(node, 80)
        upOk = self.moveUp(node, 80)
        downOk = self.moveDown(node, 80)

        if [leftOk, rightOk, upOk, downOk].count(False) >= 3:
            # ekspander videre, med mindre step, typ 20 på de som var false
            self.listOfDeadEnds.append([node.x_end, node.y_end])
        else:
            pass



    def moveUp(self, node, movement):
        node.x_end = node.x_start
        node.y_end = node.y_start + movement
        node_line = LineString([(node.x_start, node.y_start), (node.x_end, node.y_end)])
        for data in self.lineList:
            x1 = data[0][0]
            y1 = data[0][1]
            x2 = data[0][2]
            y2 = data[0][3]
            obst = LineString([(x1, y1), (x2, y2)])
            if obst.intersects(node_line):
                return False
            if obst.distance(node_line) < self.edgeDistance:
                return False
        return True

    def moveDown(self, node, movement):
        node.x_end = node.x_start
        node.y_end = node.y_start - movement
        node_line = LineString([(node.x_start, node.y_start), (node.x_end, node.y_end)])
        for data in self.lineList:
            x1 = data[0][0]
            y1 = data[0][1]
            x2 = data[0][2]
            y2 = data[0][3]
            obst = LineString([(x1, y1), (x2, y2)])
            if obst.intersects(node_line):
                return False
            if obst.distance(node_line) < self.edgeDistance:
                return False
        return True

    def moveLeft(self, node, movement):
        node.x_end = node.x_start - movement
        node.y_end = node.y_start
        node_line = LineString([(node.x_start, node.y_start), (node.x_end, node.y_end)])
        for data in self.lineList:
            x1 = data[0][0]
            y1 = data[0][1]
            x2 = data[0][2]
            y2 = data[0][3]
            obst = LineString([(x1, y1), (x2, y2)])
            if obst.intersects(node_line):
                return False
            if obst.distance(node_line) < self.edgeDistance:
                return False
        return True

    def moveRight(self, node, movement):
        node.x_end = node.x_start + movement
        node.y_end = node.y_start
        node_line = LineString([(node.x_start, node.y_start), (node.x_end, node.y_end)])
        for data in self.lineList:
            x1 = data[0][0]
            y1 = data[0][1]
            x2 = data[0][2]
            y2 = data[0][3]
            obst = LineString([(x1, y1), (x2, y2)])
            if obst.intersects(node_line):
                return False
            if obst.distance(node_line) < self.edgeDistance:
                return False
        return True


    def yolo(self):
        BWGrid = cv2.bitwise_not(self.edgePic)

    def floodFill(self, start):
        pass



if __name__ == "__main__":
    pass