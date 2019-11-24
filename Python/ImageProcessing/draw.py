import cv2
import math


def drawLines(image, lines, color=(0, 0, 0)):
    for x in range(0, len(lines) - 1):
        x0 = int(lines[x][0])
        y0 = int(lines[x][1])
        x1 = int(lines[x + 1][0])
        y1 = int(lines[x + 1][1])
        cv2.line(image, (x0, y0), (x1, y1), color, 3)
    return image

def drawSeveralLines(image, pathList, color=(0, 0, 0)):
    """
    Takes in a list of several paths and draws them on a picture
    :param image: Image to draw on
    :param pathList: List of several paths
    :param color: Color the line should be
    :return: Image with the paths drawn
    """
    for lines in pathList:
        for x in range(0, len(lines) - 1):
            x0 = int(lines[x][0])
            y0 = int(lines[x][1])
            x1 = int(lines[x + 1][0])
            y1 = int(lines[x + 1][1])
            cv2.line(image, (x0, y0), (x1, y1), color, 3)
    return image


def drawSection(image, center, startangle, endAngle, collore, radius=50):
    """
    Draws a collision sector on a given picture
    :param image: Image to draw on
    :param center: Center coordinate from which to draw
    :param startangle: Start angle of the sector
    :param endAngle: End angle of the sector
    :param collore: Color to draw the sector in
    :param radius: Radius of the semi-cirlce
    :return: Image with section drawn
    """
    center = (int(center[0]), int(center[1]))
    startangle = int(startangle)
    endAngle = int(endAngle)
    image = cv2.ellipse(image, center, (radius, radius), 0, startangle, endAngle, collore, 2)
    x1 = int(center[0] + radius * math.cos(math.radians(startangle)))
    y1 = int(center[1] + radius * math.sin(math.radians(startangle)))

    x2 = int(center[0] + radius * math.cos(math.radians(endAngle)))
    y2 = int(center[1] + radius * math.sin(math.radians(endAngle)))

    image = cv2.line(image, center, (x1, y1), collore, 2)
    image = cv2.line(image, center, (x2, y2), collore, 2)
    return image


def drawCollisionSectors(image, snakeCoordinates, angleList, collisions, offset, radius=50):
    """
    Takes in a list of angles and collisions to draw all sectors on a picture
    :param image: Image to draw on
    :param snakeCoordinates: List of coordinates for the snakes parts
    :param angleList: List of start/end-angles for the sectors
    :param collisions: List of booleans for the collisions for the sectors
    :param offset: Snakes offset in relation to the x-axis of the picture
    :param radius: Radius of the sector
    :return: Image with drawn sectors
    """
    if offset < 0:
        offset += 360
    for pos, piece, coll in zip(snakeCoordinates, angleList, collisions):
        i = 0
        for startAngle, endAngle in piece:
            if coll[i]:
                color = (0, 0, 255)
            else:
                color = (0, 255, 0)
            image = drawSection(image, tuple(pos), startAngle + offset - 90, endAngle + offset - 90,
                                   color, radius=radius)
            i += 1

    return image



if __name__ == "__main__":
    x = cv2.imread("..\\..\\Pictures/jallaball2.jpg")
    y = drawSection(x, (500, 500), -45, -135, (0, 255, 0))
    cv2.imshow("askdjhf", y)
    cv2.waitKey()
