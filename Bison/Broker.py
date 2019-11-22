from threading import Lock

class Broker:
    # Locks##############
    quitLock = Lock()
    lock = Lock()
    moveLock = Lock()
    # Flags ##############
    prepMazeSingle = False
    prepMazeMulti = False
    quitFlag = False
    findPathSingleFlag = False
    findPathMultiFlag = False
    startFlag = False
    stopFlag = False
    runFlag = False
    seekAndDestroyFlag = False
    manualControlFlag = False
    autoFlag = False
    updateParamFlag = False

    # manual movement of snake###
    moveCmd = ""
    ##########################

    # Parameter update
    params = [30, 12]
