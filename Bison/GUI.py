import time

import wx
import numpy as np
import threading

UpdateImageEventR = wx.NewEventType()
EVT_UPDATE_IMAGE_R = wx.PyEventBinder(UpdateImageEventR, 1)
UpdateImageEventL = wx.NewEventType()
EVT_UPDATE_IMAGE_L = wx.PyEventBinder(UpdateImageEventL, 1)


class CostumEvent(wx.PyCommandEvent):
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

        # Maual controll
        self.controldManualy = False

        # Update events #######################
        self.Bind(EVT_UPDATE_IMAGE_R, self.OnNewImageR)

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
        self.maualControll = wx.Button(panel, label="Manual Override", size=(130, 40))
        self.maualControll.Bind(wx.EVT_BUTTON, self.OnManualBtn)
        self.maualControll.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
        self.maualControll.SetBackgroundColour("gray")
        self.prepareMaze = wx.Button(panel, label="Prepare Maze", size=(130, 40))
        self.prepareMaze.Bind(wx.EVT_BUTTON, self.OnPrepareMaze)
        self.prepareMaze.SetBackgroundColour("gray")
        self.findPath = wx.Button(panel, label="Find Path", size=(130, 40))
        self.findPath.Bind(wx.EVT_BUTTON, self.OnFindPath)
        self.findPath.SetBackgroundColour("gray")
        bntVBoxRight.AddMany([(self.maualControll, 1), (self.prepareMaze, 1), (self.findPath, 1)])

        bntHBox.AddMany([(bntVBoxLeft, 1, wx.TOP, 50), (bntVBoxRight, 1, wx.TOP, 50)])
        #################################################
        topGrid.Add(bntHBox, 1, wx.EXPAND | wx.LEFT, 50)

        # Text feeld ####################################
        self.logTexFeald = wx.TextCtrl(panel, value="", size=(800, 390))

        topGrid.Add(self.logTexFeald, 1, wx.ALIGN_RIGHT | wx.RIGHT | wx.TOP, 10)
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
        self.imgL = ImagePanel(image, panel, size=(w, h))
        self.imgR = ImagePanel(image, panel, size=(w, h))
        videoVBox.Add(self.imgL, 1, wx.RIGHT, 10)
        videoVBox.Add(self.imgR, 1)
        outerGrid.Add(videoVBox, 1, wx.ALIGN_BOTTOM | wx.ALIGN_RIGHT | wx.BOTTOM, 5)
        ################################################

        outerGrid.AddGrowableRow(0)
        outerGrid.AddGrowableCol(0)

        self.maualControll.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)

        panel.SetSizer(outerGrid)

    def OnNewImage(self, event=None):
        """
        create a new image by changing underlying numpy array
        """
        w = h = 400
        array = np.random.randint(0, 255, (3, w, h)).astype('uint8')
        self.imgL.image = image = wx.ImageFromBuffer(w, h, array)
        self.imgL.Update()
        self.imgL.Refresh()

    def OnNewImageR(self, event=None):
        array = event.GetMyVal()
        h = array.shape[0]
        w = array.shape[1]
        self.imgR.image = image = wx.ImageFromBuffer(w, h, array)
        self.imgR.Update()
        self.imgR.Refresh()

    def OnStartBtn(self, event=None):
        pass

    def OnStopBtn(self, event=None):
        pass

    def OnYolo(self, event=None):
        pass

    def OnManualBtn(self, event=None):
        self.controldManualy = not self.controldManualy
        print(self.controldManualy)

    def OnPrepareMaze(self, event=None):
        pass

    def OnFindPath(self, event=None):
        pass

    def OnKeyDown(self, event=None):
        keycode = event.GetKeyCode()
        if self.controldManualy:
            if keycode == wx.WXK_SPACE:
                print("stop")
            elif keycode == 87:
                print("forward")
            elif keycode == 83:
                print("back")
            elif keycode == 65:
                print("left")
            elif keycode == 68:
                print("right")
            elif keycode == 69:
                print("rotae right")
            elif keycode == 81:
                print("rotate left")
            elif keycode == 82:
                print("reset")


def fireEvent(sf):
    while True:
        inp = input("-> ")
        yoloEvent = CostumEvent(UpdateImageEventR, sf.GetId())
        yoloEvent.SetMyVal(inp)
        sf.GetEventHandler().ProcessEvent(yoloEvent)


class GUI:

    def __init__(self):
        self.app = wx.App()
        self.startFrame = StartFrame(None, title='Snake Controll', size=wx.Size(1920, 1080))

    def getEventInfo(self):
        events = {"UpdateImageEventR": UpdateImageEventR,
                  "UpdateImageEventL": UpdateImageEventL}
        info = {"id": self.startFrame.GetId,
                "eventHandler": self.startFrame.GetEventHandler().ProcessEvent,
                "events": events}
        return info

    def run(self):
        self.startFrame.Show()
        self.app.MainLoop()


def main():
    gui = GUI()
    k = gui.getEventInfo()
    t = threading.Thread(target=fireEvent, args=(k,))
    # t.start()
    gui.run()


if __name__ == '__main__':
    main()
