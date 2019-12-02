"""
A simple logger that creates a file and writes to it

author: Håkon Bjerkgaard Waldum, Ruben Svedal Jørundland, Marcus Olai Grindvik
"""

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
        """
        Stops the logging and saves the file

        :return: None
        """
        Logger.logFile.close()

    @staticmethod
    def timeStamp() -> str:
        """
        Gets the current time and formats it in a string

        :return: Time formated in a string
        """
        dt = datetime.now()
        return str(dt) + ": "

    @staticmethod
    def getType(type: int):
        """
        Gets what kind of info it logs

        :param type: Number corresponding to type
        :return: What type of info it is
        """
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
        """
        Writes the log to the file

        :param message: Message to log
        :param type: What kind of info it is
        :return: None
        """
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
