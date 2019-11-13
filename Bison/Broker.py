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
    runFlag = False
    manualControlFlag = False
    autoFlag = False

    # manual movement of snake###
    moveCmd = ""
    ##########################
