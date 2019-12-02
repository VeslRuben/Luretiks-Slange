"""
Main run file of the whole program

author: Håkon Bjerkgaard Waldum, Ruben Svedal Jørundland, Marcus Olai Grindvik
"""

from Python.GUI import GUI
from Python.controller import Controller
from Python.logger import Logger

try:
    gui = GUI()
    eventData = gui.getEventInfo()

    controller = Controller(eventData)
    controller.start()

    gui.run()

    controller.join()
finally:
    Logger.stopLogging()
