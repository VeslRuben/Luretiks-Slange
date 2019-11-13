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
    updateParamFlag = False

    # manual movement of snake###
    moveCmd = ""
    ##########################

    # Parameter update
    params = [30, 10]
