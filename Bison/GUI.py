import time

import wx
import numpy as np
import threading

UpdateImageEvent = wx.NewEventType()
EVT_UPDATE_IMAGE = wx.PyEventBinder(UpdateImageEvent, 1)


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

        panel = wx.Panel(self)
        panel.SetBackgroundColour("gray")

        outerGrid = wx.FlexGridSizer(0, 2, 10, 10)

        # Left side Buttons #############################
        bntVBox = wx.BoxSizer(wx.VERTICAL)
        self.startBtn = wx.Button(panel, label="Start", size=(130, 40))
        self.startBtn.Bind(wx.EVT_BUTTON, self.OnStartBtn)
        self.startBtn.SetBackgroundColour("gray")
        self.stopBtn = wx.Button(panel, label="Stop", size=(130, 40))
        self.stopBtn.SetBackgroundColour("gray")
        self.stopBtn.Bind(wx.EVT_BUTTON, self.OnStopBtn)

        bntVBox.AddMany([(self.startBtn, 1), (self.stopBtn, 1)])
        outerGrid.Add(bntVBox, 1)
        #################################################

        # create 2 videosreams on the right side##########
        videoVBox = wx.BoxSizer(wx.HORIZONTAL)
        w = 800
        h = 600
        array = np.random.randint(0, 255, (3, w, h)).astype('uint8')
        image = wx.ImageFromBuffer(w, h, array)
        self.img1 = ImagePanel(image, panel, size=(w, h))
        self.img2 = ImagePanel(image, panel, size=(w, h))
        videoVBox.Add(self.img1, 1, wx.RIGHT, 10)
        videoVBox.Add(self.img2, 1)
        outerGrid.Add(videoVBox, 1, wx.ALIGN_BOTTOM | wx.ALIGN_RIGHT | wx.BOTTOM, 5)
        ################################################

        outerGrid.AddGrowableRow(0)
        outerGrid.AddGrowableCol(1)

        panel.SetSizer(outerGrid)

    def OnNewImage(self, event=None):
        """
        create a new image by changing underlying numpy array
        """
        w = h = 400
        array = np.random.randint(0, 255, (3, w, h)).astype('uint8')
        self.img1.image = image = wx.ImageFromBuffer(w, h, array)
        self.img1.Update()
        self.img1.Refresh()

    def OnStartBtn(self, event=None):
        pass

    def OnStopBtn(self, event=None):
        pass


def fireEvent(sf):
    while True:
        inp = input("-> ")
        yoloEvent = CostumEvent(UpdateImageEvent, sf.GetId())
        yoloEvent.SetMyVal(inp)
        sf.GetEventHandler().ProcessEvent(yoloEvent)


class GUI():

    def __init__(self):
        self.app = wx.App()
        self.startFrame = StartFrame(None, title='Snake Controll', size=wx.Size(1920, 1080))

    def getEventInfo(self):
        events = {"UpdateImageEvent": UpdateImageEvent}
        info = {"id": self.startFrame.GetId(),
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
