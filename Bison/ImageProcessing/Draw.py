import cv2


def drawLines(image, lines, color=(0, 0, 0)):
    for x in range(0, len(lines) - 1):
        x0 = int(lines[x][0])
        y0 = int(lines[x][1])
        x1 = int(lines[x + 1][0])
        y1 = int(lines[x + 1][1])
        cv2.line(image, (x0, y0), (x1, y1), color, 3)
    return image
