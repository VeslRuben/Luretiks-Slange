import os
import time

from Bison.logger import Logger

print (os.listdir('.') )# current level


path = os.getcwd().split("\\")
if path[len(path)-1] == "Bison":
    print(path)
else:
    for x in range(2,10):
        t = "../" * x
        dirs = os.listdir(t)
        print(dirs)

Logger.startLoggig()


