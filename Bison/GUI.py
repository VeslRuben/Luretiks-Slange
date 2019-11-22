import time

import cv2
import wx
import numpy as np
from Bison.Broker import Broker as b
from Bison.logger import Logger
import wx.lib.agw.gradientbutton as GB

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


class ParameterDialog(wx.Dialog):
    def __init__(self, parent, id=-1, title="Enter new parameters!"):
        wx.Dialog.__init__(self, parent, id, title, size=(-1, -1))
        self.Bind(wx.EVT_CLOSE, self.OnClose)

        self.mainSizer = wx.BoxSizer(wx.VERTICAL)
        self.topText = wx.StaticText(self, label="Amplitude: 0-10 \nSpeed: 0-100 (Higher = Slower)")
        self.mainSizer.Add(self.topText, 0, wx.ALL, 8)
        with b.lock:
            # amplitude
            self.ampSizer = wx.BoxSizer(wx.HORIZONTAL)
            self.label = wx.StaticText(self, label="Snake Amplitude:")
            self.ampField = wx.TextCtrl(self, value=f"{b.params[0]}", size=(150, 20))
            self.ampField.Bind(wx.EVT_CHAR, self.onChar)
            self.ampSizer.Add(self.label, 0, wx.ALL, 8)
            self.ampSizer.Add(self.ampField, 0, wx.LEFT, 26)
            self.mainSizer.Add(self.ampSizer, 0, wx.ALL)

            # Speed
            self.speedSizer = wx.BoxSizer(wx.HORIZONTAL)
            self.label = wx.StaticText(self, label="Snake Speed:")
            self.speedField = wx.TextCtrl(self, value=f"{b.params[1]}", size=(150, 20))
            self.speedField.Bind(wx.EVT_CHAR, self.onChar)
            self.speedSizer.Add(self.label, 0, wx.ALL, 8)
            self.speedSizer.Add(self.speedField, 0, wx.LEFT, 50)
            self.mainSizer.Add(self.speedSizer, 0, wx.ALL)

        # Ok btn
        self.buttonSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.okbutton = wx.Button(self, label="OK", id=wx.ID_OK)
        self.buttonSizer.Add(self.okbutton, 0, wx.ALL, 8)
        self.mainSizer.Add(self.buttonSizer, 0, wx.ALL, 0)

        self.Bind(wx.EVT_BUTTON, self.onOK, id=wx.ID_OK)
        self.Bind(wx.EVT_TEXT_ENTER, self.onOK)

        self.SetSizer(self.mainSizer)
        self.result = None

    def onOK(self, event):
        result = [self.ampField.GetValue(), self.speedField.GetValue()]
        self.result = result
        self.Destroy()

    def onChar(self, event):
        key = event.GetKeyCode()
        acceptable_characters = "1234567890."
        # 13 = enter, 314 & 316 = arrows, 8 = backspace, 127 = del:
        if chr(key) in acceptable_characters or key == 13 or key == 314 or key == 316 or key == 8 or key == 127:
            event.Skip()
            return
        else:
            return False

    def OnClose(self, event=None):
        self.result = None
        self.Destroy()


class StartFrame(wx.Frame):

    def __init__(self, *args, **kw):
        # ensure the parent's __init__ is called
        super(StartFrame, self).__init__(*args, **kw)
        self.Maximize(True)
        self.Bind(wx.EVT_CLOSE, self.OnClose)

        # variabels for threding #################

        ##########################################

        # show some image details

        # Update events #######################
        self.Bind(EVT_UPDATE_IMAGE_R, self.OnNewImageR)
        self.Bind(EVT_UPDATE_IMAGE_L, self.OnNewImageL)
        self.Bind(EVT_UPDATE_TEXT, self.OnNewText)

        #######################################

        panel = wx.Panel(self)
        #panel.SetBackgroundColour("gray")
        image_file = r'C:\Users\marcu\PycharmProjects\Luretriks-Slange\Pictures\BlueShit.jpg'
        bmp1 = wx.Image(
            image_file,
            wx.BITMAP_TYPE_ANY).ConvertToBitmap()
        # image's upper left corner anchors at panel
        #coordinates (0, 0)
        self.bitmap1 = wx.StaticBitmap(
        panel, -1, bmp1, (0, 0))

        outerGrid = wx.FlexGridSizer(2, 0, 10, 10)
        botGrid = wx.FlexGridSizer(0, 2, 10, 10)

        # Top  Buttons #############################
        bntHBox = wx.BoxSizer(wx.HORIZONTAL)

        # left butons
        bntVBoxLeft = wx.BoxSizer(wx.VERTICAL)

        self.manualControl = wx.Button(panel, label="Manual Override", size=(130, 50))
        self.manualControl.Bind(wx.EVT_BUTTON, self.OnManualBtn)
        self.manualControl.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
        self.manualControl.SetBackgroundColour("gray")

        self.updateParam = GB.GradientButton(panel, label="Update Parameters", size=(130, 50))
        self.updateParam.Bind(wx.EVT_BUTTON, self.OnUpdateParametersBtn)
        self.updateParam.SetBackgroundColour("gray")

        self.stopBtn = GB.GradientButton(panel, label="Stop", size=(130, 50))
        self.stopBtn.SetBackgroundColour("gray")
        self.stopBtn.Bind(wx.EVT_BUTTON, self.OnStopBtn)

        # middel butons
        bntVBoxMidle = wx.BoxSizer(wx.VERTICAL)

        self.prepareMaze = GB.GradientButton(panel, label="Prepare Maze", size=(130, 50))
        self.prepareMaze.Bind(wx.EVT_BUTTON, self.OnPrepareMaze)

        self.findPath = GB.GradientButton(panel, label="Find Path", size=(130, 50))
        self.findPath.Bind(wx.EVT_BUTTON, self.OnFindPath)
        self.findPath.SetBackgroundColour("gray")

        self.runBtn = GB.GradientButton(panel, label="Run", size=(130, 50))
        self.runBtn.SetBackgroundColour("gray")
        self.runBtn.Bind(wx.EVT_BUTTON, self.OnRun)

        bntVBoxMidle.AddMany([(self.runBtn, 1), (self.findPath, 1), (self.updateParam, 1)])
        bntVBoxLeft.AddMany([(self.stopBtn, 1), (self.prepareMaze, 1), (self.manualControl, 1)])
        # Right buttons
        btnVBoxRight = wx.BoxSizer(wx.VERTICAL)

        self.prepareMaze2 = GB.GradientButton(panel, label="Prepare Maze", size=(130, 40))
        # bind....

        self.findPath2 = GB.GradientButton(panel, label="Find Path", size=(130, 40))
        # bind.....

        self.seekAndDestroy = GB.GradientButton(panel, label="Seek and Destroy", size=(130, 40))
        # bind...
        self.prepareMaze.SetBackgroundColour("gray")

        btnVBoxRight.AddMany([(self.prepareMaze2, 1), (self.findPath2, 1), (self.seekAndDestroy, 1)])

        bntHBox.AddMany([(bntVBoxLeft, 0, wx.TOP, 10), (bntVBoxMidle, 0, wx.TOP, 10), (btnVBoxRight, 0, wx.TOP, 10)])
        #################################################
        botGrid.Add(bntHBox, 1, wx.ALIGN_LEFT | wx.LEFT, 10)

        # Text feeld ####################################
        self.logTextField = wx.TextCtrl(panel, value="", size=(820, 390), style=wx.TE_MULTILINE)

        botGrid.Add(self.logTextField, 1, wx.ALIGN_RIGHT|wx.LEFT, 610)
        #################################################
        botGrid.AddGrowableRow(0)
        botGrid.AddGrowableCol(1)



        # create 2 videosreams on the right side##########
        videoVBox = wx.BoxSizer(wx.HORIZONTAL)
        w = 800
        h = 600
        array = np.random.randint(0, 255, (3, w, h)).astype('uint8')
        image = wx.ImageFromBuffer(w, h, array)
        self.imgL = ImagePanel(image, panel, wx.ALIGN_BOTTOM | wx.ALIGN_RIGHT, size=(w, h))
        self.imgR = ImagePanel(image, panel, wx.ALIGN_BOTTOM | wx.ALIGN_RIGHT, size=(w, h))
        videoVBox.Add(self.imgL, 1, wx.ALIGN_TOP | wx.ALIGN_RIGHT | wx.RIGHT, 100)
        videoVBox.Add(self.imgR, 1, wx.ALIGN_TOP | wx.ALIGN_RIGHT)
        outerGrid.Add(videoVBox, 1, wx.ALIGN_TOP | wx.ALIGN_RIGHT | wx.BOTTOM, 10)
        ################################################

        outerGrid.Add(botGrid, 1, wx.ALIGN_LEFT)

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
        # Logger.logg("GUI right image updated", Logger.info)

    def OnNewImageL(self, event=None):
        array = event.GetMyVal()
        array = cv2.resize(array, (800, 600))
        h = array.shape[0]
        w = array.shape[1]
        self.imgL.image = image = wx.ImageFromBuffer(w, h, array)
        self.imgL.Update()
        self.imgL.Refresh()
        # Logger.logg("GUI left image updated", Logger.info)

    def OnNewText(self, event=None):
        text = event.GetMyVal()
        self.logTextField.AppendText(text + "\n")
        self.logTextField.Refresh()
        # Logger.logg("GUI text box updated", Logger.info)

    def OnUpdateParametersBtn(self, event=None):
        dlg = ParameterDialog(self)
        dlg.ShowModal()
        result = dlg.result
        if result:
            with b.lock:
                b.params = result
                b.updateParamFlag = True

    def OnStopBtn(self, event=None):
        with b.lock:
            b.stopFlag = True

    def OnRun(self, event=None):
        with b.lock:
            b.runFlag = not b.runFlag

    def OnManualBtn(self, event=None):
        # warning dialog
        if not self.controlledManually:
            wx.MessageBox('Use "w, s, a, d, r" to control the snake manually', 'Info', wx.OK | wx.ICON_INFORMATION)
        self.controlledManually = not self.controlledManually
        with b.lock:
            b.manualControlFlag = not b.manualControlFlag
        self.logTextField.AppendText(f"Snake manual mode: {self.controlledManually}\n")
        Logger.logg(f"GUI manual control: {self.controlledManually}", Logger.info)

    def OnPrepareMaze(self, event=None):
        # warning dialog
        wx.MessageBox('Make sure the maze is empty', 'Info', wx.OK | wx.ICON_INFORMATION)
        with b.lock:
            b.prepMaze = True
        Logger.logg("GUI prepare maze btn preset", Logger.info)

    def OnFindPath(self, event=None):
        # warning dialog
        wx.MessageBox('Put the snake and the target in the maze', 'Info', wx.OK | wx.ICON_INFORMATION)
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
        print(keycode)
        if self.controlledManually:
            with b.moveLock:
                if keycode == wx.WXK_SPACE:
                    b.moveCmd = "s"
                elif keycode == 87:
                    b.moveCmd = "f"
                elif keycode == 83:
                    b.moveCmd = "b"
                elif keycode == 65:
                    b.moveCmd = "v"
                elif keycode == 68:
                    b.moveCmd = "h"
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
