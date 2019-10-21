import math
import random
from shapely.geometry import LineString

import matplotlib.pyplot as plt
from matplotlib.path import Path
import numpy as np

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

for (x, y, angle, length) in lineList:
    xangle = math.cos(np.deg2rad(angle))
    yangle = math.sin(np.deg2rad(angle))
    x2 = x + (length * xangle)
    y2 = y + (length * yangle)
    plt.plot([x, x2], [y, y2], color='k', linestyle='-', linewidth=2)



x_node = [0, 0.31208058741864825, 0.6241611748372965, 0.9362417622559447, 1.248322349674593, 1.5604029370932413, 1.8724835245118896]
y_node = [0, 0.39064780423858964, 0.7812956084771793, 1.1719434127157689, 1.5625912169543585, 1.9532390211929482, 2.3438868254315377]


plt.plot([x_node[0], x_node[1]], [y_node[0], y_node[1]], color='b', linestyle='-', linewidth=2)
plt.plot([x_node[1], x_node[2]], [y_node[1], y_node[2]], color='b', linestyle='-', linewidth=2)
plt.plot([x_node[2], x_node[3]], [y_node[2], y_node[3]], color='b', linestyle='-', linewidth=2)
plt.plot([x_node[3], x_node[4]], [y_node[3], y_node[4]], color='b', linestyle='-', linewidth=2)
plt.plot([x_node[4], x_node[5]], [y_node[4], y_node[5]], color='b', linestyle='-', linewidth=2)

plt.show()

nodecoord = LineString([(x_node[0], y_node[0]), (x_node[1], y_node[1]), (x_node[2], y_node[2]), (x_node[3], y_node[3]),
                        (x_node[4], y_node[4]), (x_node[5], y_node[5])])

nodecoord2 = LineString([(x, y) for (x,y) in zip(x_node, y_node)])

for (lx, ly, la, ll) in lineList:
    obst = LineString([(lx, ly), (lx + (ll * math.cos(np.deg2rad(la))), ly + (ll * math.sin(np.deg2rad(la))))])
    if obst.intersects(nodecoord):
        print("Shit hits the fan")
    else:
        print("No shit in the fan")