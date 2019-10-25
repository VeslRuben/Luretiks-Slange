import os
import time

import scipy.misc
from Bison.Com.videoStream import VideoStream
from PIL import Image


v = VideoStream("http://192.168.137.171")

for x in range(10):
    v.reSize(x)
    time.sleep(0.5)
    a = v.getPicture()
    im = Image.fromarray(a)
    im.save(f"C:\\Users\\Ruben\\Pictures\\Camera Roll\\{x}.jpeg")
    time.sleep(0.5)
