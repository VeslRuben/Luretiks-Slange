from Bison.GUI import GUI, CustomEvent
from Bison.Controller import Controller
from Bison.logger import Logger

try:
    gui = GUI()
    eventData = gui.getEventInfo()

    controller = Controller(eventData)
    controller.start()

    gui.run()

    controller.join()
finally:
    Logger.stopLogging()
