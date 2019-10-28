import time
from io import BytesIO
import numpy as np
from PIL import Image
import requests
from Bison.logger import Logger


class VideoStream:

    def __init__(self, url: str):
        """

        :param url: The url to connect to
        """
        self.url = url

    def reSize(self, size: int):
        """
        Sets the size of the images taken \n
        :param size: Size of the image represented by an integer value.
            10 = 1600 x 1200,
            9 = 1280 x 1024,
            8 = 1024 x 768,
            7 = 800 x 600,
            6 = 640 x480,
            5 = 400 x 296,
            4 = 320 x 240,
            3 = 240 x 176,
            0 = 160 x 120,
        :return: None
        """
        if size > 10:
            size = 10
        elif size < 3:
            size = 0
        obj = {"var": "framesize", "val": size}
        requests.get(self.url + "/control", params=obj, timeout=3)
        Logger.logg("framesize set to: " + str(size), Logger.info)
        time.sleep(0.3)

    def getPicture(self) -> np.array:
        """
        Gets on picture form the cameras stream. \n
        :return: Image as an numpy array
        """
        try:
            response = requests.get(self.url + "/capture", timeout=3)
            img = Image.open(BytesIO(response.content))
            imgArray = np.array(img)
            return imgArray
        except requests.exceptions.ConnectTimeout:
            Logger.logg("Unable to get image form camera", Logger.warning)
            return None


if __name__ == "__main__":
    c = VideoStream("http://192.168.137.171")
    c.reSize(10)
    c.getPicture()
