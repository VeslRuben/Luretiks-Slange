from Bison.Com.udpCom import UdpConnection
from Bison.Com.videoStream import VideoStream

servoController = UdpConnection("192.168.137.113")
frontCamera = VideoStream("http://192.168.137.171")

