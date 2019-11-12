import time

import cv2
import wx
import numpy as np
from Bison.Broker import Broker as b
from Bison.logger import Logger

UpdateImageEventR = wx.NewEventType()
EVT_UPDATE_IMAGE_R = wx.PyEventBinder(UpdateImageEventR, 1)
UpdateImageEventL = wx.NewEventType()
EVT_UPDATE_IMAGE_L = wx.PyEventBinder(UpdateImageEventL, 1)
UpdateTextEvent = wx.NewEventType()
EVT_UPDATE_TEXT = wx.PyEventBinder(UpdateTextEvent, 1)


class CustomEvent(wx.PyCommandEvent):
    def __init__(self, evtType, id):
        wx.PyCommandEvent.__init__(self, evtType, id)
        self.myVal = None

    def SetMyVal(self, val):
        self.myVal = val

    def GetMyVal(self):
        return self.myVal


class ImagePanel(wx.Panel):
    """
    A very simple panel for displaying a wx.Image
    """

    def __init__(self, image, *args, **kwargs):
        wx.Panel.__init__(self, *args, **kwargs)

        self.image = image
        self.Bind(wx.EVT_PAINT, self.OnPaint)

    def OnPaint(self, event):
        dc = wx.PaintDC(self)
        dc.DrawBitmap(wx.BitmapFromImage(self.image), 0, 0)


class StartFrame(wx.Frame):
    """
    A Frame that says Hello World
    """

    def __init__(self, *args, **kw):
        # ensure the parent's __init__ is called
        super(StartFrame, self).__init__(*args, **kw)
        self.Maximize(True)
        self.Bind(wx.EVT_CLOSE, self.OnClose)

        # variabels for threding #################

        ##########################################

        # Maual controll
        self.controlledManually = False

        # Update events #######################
        self.Bind(EVT_UPDATE_IMAGE_R, self.OnNewImageR)
        self.Bind(EVT_UPDATE_IMAGE_L, self.OnNewImageL)
        self.Bind(EVT_UPDATE_TEXT, self.OnNewText)

        #######################################

        panel = wx.Panel(self)
        panel.SetBackgroundColour("gray")

        outerGrid = wx.FlexGridSizer(2, 0, 10, 10)
        topGrid = wx.FlexGridSizer(0, 2, 10, 10)

        # Top  Buttons #############################
        bntHBox = wx.BoxSizer(wx.HORIZONTAL)

        bntVBoxLeft = wx.BoxSizer(wx.VERTICAL)
        self.startBtn = wx.Button(panel, label="Start", size=(130, 40))
        self.startBtn.Bind(wx.EVT_BUTTON, self.OnStartBtn)
        self.startBtn.SetBackgroundColour("gray")
        self.stopBtn = wx.Button(panel, label="Stop", size=(130, 40))
        self.stopBtn.SetBackgroundColour("gray")
        self.stopBtn.Bind(wx.EVT_BUTTON, self.OnStopBtn)
        self.yoloBtn = wx.Button(panel, label="yolo", size=(130, 40))
        self.yoloBtn.SetBackgroundColour("gray")
        self.yoloBtn.Bind(wx.EVT_BUTTON, self.OnYolo)
        bntVBoxLeft.AddMany([(self.startBtn, 1), (self.stopBtn, 1), (self.yoloBtn, 1)])

        bntVBoxRight = wx.BoxSizer(wx.VERTICAL)
        self.manualControl = wx.Button(panel, label="Manual Override", size=(130, 40))
        self.manualControl.Bind(wx.EVT_BUTTON, self.OnManualBtn)
        self.manualControl.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
        self.manualControl.SetBackgroundColour("gray")
        self.prepareMaze = wx.Button(panel, label="Prepare Maze", size=(130, 40))
        self.prepareMaze.Bind(wx.EVT_BUTTON, self.OnPrepareMaze)
        self.prepareMaze.SetBackgroundColour("gray")
        self.findPath = wx.Button(panel, label="Find Path", size=(130, 40))
        self.findPath.Bind(wx.EVT_BUTTON, self.OnFindPath)
        self.findPath.SetBackgroundColour("gray")
        bntVBoxRight.AddMany([(self.manualControl, 1), (self.prepareMaze, 1), (self.findPath, 1)])

        bntHBox.AddMany([(bntVBoxLeft, 1, wx.TOP, 50), (bntVBoxRight, 1, wx.TOP, 50)])
        #################################################
        topGrid.Add(bntHBox, 1, wx.EXPAND | wx.LEFT, 50)

        # Text feeld ####################################
        self.logTextField = wx.TextCtrl(panel, value="", size=(800, 390), style=wx.TE_MULTILINE)

        topGrid.Add(self.logTextField, 1, wx.ALIGN_RIGHT | wx.RIGHT | wx.TOP, 10)
        #################################################
        topGrid.AddGrowableRow(0)
        topGrid.AddGrowableCol(1)

        outerGrid.Add(topGrid, 1, wx.EXPAND)

        # create 2 videosreams on the right side##########
        videoVBox = wx.BoxSizer(wx.HORIZONTAL)
        w = 800
        h = 600
        array = np.random.randint(0, 255, (3, w, h)).astype('uint8')
        image = wx.ImageFromBuffer(w, h, array)
        self.imgL = ImagePanel(image, panel, wx.ALIGN_BOTTOM | wx.ALIGN_RIGHT, size=(w, h))
        self.imgR = ImagePanel(image, panel, wx.ALIGN_BOTTOM | wx.ALIGN_RIGHT, size=(w, h))
        videoVBox.Add(self.imgL, 1, wx.ALIGN_BOTTOM | wx.ALIGN_RIGHT | wx.RIGHT, 10)
        videoVBox.Add(self.imgR, 1, wx.ALIGN_BOTTOM | wx.ALIGN_RIGHT)
        outerGrid.Add(videoVBox, 1, wx.ALIGN_BOTTOM | wx.ALIGN_RIGHT | wx.BOTTOM, 5)
        ################################################

        outerGrid.AddGrowableRow(0)
        outerGrid.AddGrowableCol(0)

        self.manualControl.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)

        panel.SetSizer(outerGrid)

    def OnNewImageR(self, event=None):
        array = event.GetMyVal()
        array = cv2.resize(array, (800, 600))
        h = array.shape[0]
        w = array.shape[1]
        self.imgR.image = image = wx.ImageFromBuffer(w, h, array)
        self.imgR.Update()
        self.imgR.Refresh()
        #Logger.logg("GUI right image updated", Logger.info)

    def OnNewImageL(self, event=None):
        array = event.GetMyVal()
        array = cv2.resize(array, (800, 600))
        h = array.shape[0]
        w = array.shape[1]
        self.imgL.image = image = wx.ImageFromBuffer(w, h, array)
        self.imgL.Update()
        self.imgL.Refresh()
        #Logger.logg("GUI left image updated", Logger.info)

    def OnNewText(self, event=None):
        text = event.GetMyVal()
        self.logTextField.AppendText(text + "\n")
        self.logTextField.Refresh()
        #Logger.logg("GUI text box updated", Logger.info)

    def OnStartBtn(self, event=None):
        with b.lock:
            b.startFlag = True
        Logger.logg("GUI start btn preset", Logger.info)

    def OnStopBtn(self, event=None):
        with b.lock:
            b.stopFlag = True

    def OnYolo(self, event=None):
        with b.lock:
            b.yoloFlag = not b.yoloFlag

    def OnManualBtn(self, event=None):
        self.controlledManually = not self.controlledManually
        with b.lock:
            b.manualControlFlag = not b.manualControlFlag
        self.logTextField.AppendText(f"Snake manual mode: {self.controlledManually}\n")
        Logger.logg(f"GUI manual control: {self.controlledManually}", Logger.info)

    def OnPrepareMaze(self, event=None):
        with b.lock:
            b.prepMaze = True
        Logger.logg("GUI prepare maze btn preset", Logger.info)

    def OnFindPath(self, event=None):
        with b.lock:
            b.findPathFlag = True
        Logger.logg("GUI find path btn preset", Logger.info)

    def OnClose(self, event=None):
        """
        quits the gui and sets a flagg for other threds \n
        :param event: the event
        :return: None
        """
        with b.quitLock:
            b.quitFlag = True
        Logger.logg("GUI shutting down", Logger.info)
        time.sleep(0.5)
        self.Destroy()

    def OnKeyDown(self, event=None):
        keycode = event.GetKeyCode()
        if self.controlledManually:
            with b.moveLock:
                if keycode == wx.WXK_SPACE:
                    b.moveCmd = "s"
                elif keycode == 87:
                    b.moveCmd = "f"
                elif keycode == 83:
                    b.moveCmd = "b"
                elif keycode == 65:
                    b.moveCmd = "l"
                elif keycode == 68:
                    b.moveCmd = "r"
                elif keycode == 69:
                    print("rotate right")
                elif keycode == 81:
                    print("rotate left")
                elif keycode == 82:
                    b.moveCmd = "r"


class GUI:

    def __init__(self):
        self.app = wx.App()
        self.startFrame = StartFrame(None, title='Snake Control', size=wx.Size(1920, 1080))
        Logger.logg("GUI init", Logger.info)

    def getEventInfo(self):
        events = {"UpdateImageEventR": UpdateImageEventR,
                  "UpdateImageEventL": UpdateImageEventL,
                  "UpdateTextEvent": UpdateTextEvent}
        info = {"id": self.startFrame.GetId,
                "eventHandler": self.startFrame.GetEventHandler().ProcessEvent,
                "events": events}
        Logger.logg("GUI event data returned successful", Logger.info)
        return info

    def run(self):
        Logger.logg("GUI running", Logger.info)
        self.startFrame.Show()
        self.app.MainLoop()


def main():
    gui = GUI()
    k = gui.getEventInfo()

    gui.run()


if __name__ == '__main__':
    main()
