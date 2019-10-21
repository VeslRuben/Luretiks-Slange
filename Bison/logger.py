from datetime import datetime


class Logger:
    # Logging types
    debug = 0
    info = 1
    cmd = 2
    warning = 3
    error = 4

    @staticmethod
    def startLoggig():
        dt = datetime.now()
        Logger.logFile = open("../Loggs/" + str(dt.day) + str(dt.month) + str(dt.year) + "_" +
                              str(dt.hour) + str(dt.minute) + ".txt", "w+")

    @staticmethod
    def testLog():
        dt = datetime.now()
        Logger.logFile = open("log.txt", "w+")

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
    Logger.logg("krash", Logger.error)
    Logger.logg("farlig", Logger.warning)
    Logger.logg("komando", Logger.cmd)
    Logger.logg("informasjon", Logger.info)
    Logger.logg("bille", Logger.debug)

    Logger.stopLogging()
