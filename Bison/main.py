from Bison.GUI import GUI, CostumEvent
from Bison.Controller import Cotroller
from Bison.logger import Logger

try:
    gui = GUI()
    evenData = gui.getEventInfo()

    controller = Cotroller(evenData)
    controller.start()

    gui.run()

    controller.join()
finally:
    Logger.stopLogging()
