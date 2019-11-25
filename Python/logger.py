from datetime import datetime
import os

class Logger:
    # Logging types
    debug = 0
    info = 1
    cmd = 2
    warning = 3
    error = 4

    path = os.getcwd().split("\\")
    if path[len(path) - 1] == "Python":
        path = "..\\"
    else:
        for x in range(2, 10):
            t = "../" * x
            dirs = os.listdir(t)
            if dirs.count("Loggs"):
                path = t
                break
    dt = datetime.now()
    logFile = open(path + "Loggs\\" + str(dt.day) + str(dt.month) + str(dt.year) + "_" +
                          str(dt.hour) + str(dt.minute) + ".txt", "w+")

    @staticmethod
    def stopLogging():
        Logger.logFile.close()

    @staticmethod
    def timeStamp() -> str:
        dt = datetime.now()
        return str(dt) + ": "

    @staticmethod
    def getType(type: int):
        if type == 4:
            return "[Error] "
        elif type == 3:
            return "[Warning] "
        elif type == 2:
            return "[Command] "
        elif type == 1:
            return "[Info] "
        else:
            return "[Debug] "

    @staticmethod
    def logg(message: str, type: int):
        timeStamp = Logger.timeStamp()
        messageType = Logger.getType(type)
        Logger.logFile.write(timeStamp + messageType + message + "\n")


if __name__ == "__main__":
    Logger.logg("Crash", Logger.error)
    Logger.logg("Farlig", Logger.warning)
    Logger.logg("Kommando", Logger.cmd)
    Logger.logg("Informasjon", Logger.info)
    Logger.logg("Bille", Logger.debug)

    Logger.stopLogging()