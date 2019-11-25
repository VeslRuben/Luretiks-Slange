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

# Generell to do:
# TODO: Jobb videre på Seek 'n Destroy
# TODO: GUI-greiene


# Notes fra Houxiang:
# TODO: Physical Limitations are OK, specify them
