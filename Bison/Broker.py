from threading import Lock


class Broker:
    # Locks##############
    quitLock = Lock()
    lock = Lock()
    moveLock = Lock()
    # Flags ##############
    prepMaze = False
    quitFlag = False
    findPathFlag = False
    startFlag = False
    stopFlag = False
    yoloFlag = False
    manulaControllFlag = False
    autoFlag = False

    # maula movnet of snake###
    moveCmd = ""
    ##########################
