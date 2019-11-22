from Bison.GUI import GUI
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

# Generell to do:
# TODO: Implementer collision detection
# TODO: Jobb videre på Seek 'n Destroy
# TODO: GUI-greiene
# TODO: Implementer rotasjon
# TODO: Start conditions for GoToTarget


# Notes fra Houxiang:
# TODO: Physical Limitations are OK, specify them
# TODO: Følehorn med fargekode. Grønn = OK, Rød != OK
# TODO: Penere GUI, snakk med Lars Ivar eller Pierre
# TODO: Ta mer hensyn ved start til hvilke bevegelser som må gjøres
