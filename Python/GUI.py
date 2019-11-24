import time
import cv2
import wx
import numpy as np
from Python.broker import Broker as b
from Python.logger import Logger

UpdateImageEventR = wx.NewEventType()
EVT_UPDATE_IMAGE_R = wx.PyEventBinder(UpdateImageEventR, 1)
UpdateImageEventL = wx.NewEventType()
EVT_UPDATE_IMAGE_L = wx.PyEventBinder(UpdateImageEventL, 1)
UpdateTextEvent = wx.NewEventType()
EVT_UPDATE_TEXT = wx.PyEventBinder(UpdateTextEvent, 1)
YesNoEvent = wx.NewEventType()
EVT_YES_NO = wx.PyEventBinder(YesNoEvent, 1)


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
        self.Bind(wx.EVT_PAINT, self.onPaint)

    def onPaint(self, event):
        dc = wx.PaintDC(self)
        dc.DrawBitmap(wx.BitmapFromImage(self.image), 0, 0)


class ParameterDialog(wx.Dialog):
    def __init__(self, parent, id=-1, title="Enter new parameters!"):
        wx.Dialog.__init__(self, parent, id, title, size=(-1, -1))
        self.Bind(wx.EVT_CLOSE, self.onClose)

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

    def onClose(self, event=None):
        self.result = None
        self.Destroy()


class StartFrame(wx.Frame):

    def __init__(self, *args, **kw):
        # ensure the parent's __init__ is called
        super(StartFrame, self).__init__(*args, **kw)
        self.Maximize(True)
        self.Bind(wx.EVT_CLOSE, self.onClose)

        # Maual controll
        self.controlledManually = False

        # Update events #######################
        self.Bind(EVT_UPDATE_IMAGE_R, self.onNewImageR)
        self.Bind(EVT_UPDATE_IMAGE_L, self.onNewImageL)
        self.Bind(EVT_UPDATE_TEXT, self.onNewText)
        self.Bind(EVT_YES_NO, self.onYesNo)

        #######################################

        panel = wx.Panel(self)
        panel.SetBackgroundColour("gray")

        outerGrid = wx.FlexGridSizer(2, 0, 10, 10)
        topGrid = wx.FlexGridSizer(0, 2, 10, 10)

        # Top  Buttons #############################
        bntHBox = wx.BoxSizer(wx.HORIZONTAL)

        # left butons
        bntVBoxLeft = wx.BoxSizer(wx.VERTICAL)

        self.manualControl = wx.Button(panel, label="Manual Override", size=(130, 40))
        self.manualControl.Bind(wx.EVT_BUTTON, self.onManualBtn)
        self.manualControl.Bind(wx.EVT_KEY_DOWN, self.onKeyDown)
        self.manualControl.SetBackgroundColour("gray")

        self.startBtn = wx.Button(panel, label="Update Parameters", size=(130, 40))
        self.startBtn.Bind(wx.EVT_BUTTON, self.onUpdateParametersBtn)
        self.startBtn.SetBackgroundColour("gray")

        self.stopBtn = wx.Button(panel, label="Stop", size=(130, 40))
        self.stopBtn.SetBackgroundColour("gray")
        self.stopBtn.Bind(wx.EVT_BUTTON, self.onStopBtn)

        bntVBoxLeft.AddMany([(self.manualControl, 1), (self.startBtn, 1), (self.stopBtn, 1)])

        # middel butons
        bntVBoxMidle = wx.BoxSizer(wx.VERTICAL)

        self.prepareMaze = wx.Button(panel, label="Prepare Maze", size=(130, 40))
        self.prepareMaze.Bind(wx.EVT_BUTTON, self.onPrepareMazeSingle)
        self.prepareMaze.SetBackgroundColour("gray")

        self.findPath = wx.Button(panel, label="Find Path", size=(130, 40))
        self.findPath.Bind(wx.EVT_BUTTON, self.onFindPathSingle)
        self.findPath.SetBackgroundColour("gray")
        self.findPath.Disable()

        self.runBtn = wx.Button(panel, label="Run", size=(130, 40))
        self.runBtn.SetBackgroundColour("gray")
        self.runBtn.Bind(wx.EVT_BUTTON, self.onRun)
        self.runBtn.Disable()

        bntVBoxMidle.AddMany([(self.prepareMaze, 1), (self.findPath, 1), (self.runBtn, 1)])

        # Right buttons
        btnVBoxRight = wx.BoxSizer(wx.VERTICAL)

        self.prepareMaze2 = wx.Button(panel, label="Prepare Maze", size=(130, 40))
        self.prepareMaze2.Bind(wx.EVT_BUTTON, self.onPrepareMazeMulti)
        self.prepareMaze2.SetBackgroundColour("gray")

        self.findPath2 = wx.Button(panel, label="Find Path", size=(130, 40))
        self.findPath2.Bind(wx.EVT_BUTTON, self.onFindPathMulti)
        self.findPath2.SetBackgroundColour("gray")
        self.findPath2.Disable()

        self.seekAndDestroy = wx.Button(panel, label="Seek and Destroy", size=(130, 40))
        self.seekAndDestroy.Bind(wx.EVT_BUTTON, self.onSeekAndDestroy)
        self.seekAndDestroy.SetBackgroundColour("gray")
        self.seekAndDestroy.Disable()

        btnVBoxRight.AddMany([(self.prepareMaze2, 1), (self.findPath2, 1), (self.seekAndDestroy, 1)])

        bntHBox.AddMany([(bntVBoxLeft, 1, wx.TOP, 50), (bntVBoxMidle, 1, wx.TOP, 50), (btnVBoxRight, 1, wx.TOP, 50)])
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

        self.manualControl.Bind(wx.EVT_KEY_DOWN, self.onKeyDown)

        panel.SetSizer(outerGrid)

    def onYesNo(self, evnet=None):
        dlg = wx.MessageBox('Is the target in front of the snake?', 'Target?', wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION)
        with b.lock:
            if dlg == 2:
                b.answer = True
            elif dlg == 8:
                b.answer = False

    def onNewImageR(self, event=None):
        array = event.GetMyVal()
        array = cv2.resize(array, (800, 600))
        h = array.shape[0]
        w = array.shape[1]
        self.imgR.image = wx.ImageFromBuffer(w, h, array)
        self.imgR.Update()
        self.imgR.Refresh()
        # Logger.logg("GUI right image updated", Logger.info)

    def onNewImageL(self, event=None):
        array = event.GetMyVal()
        array = cv2.resize(array, (800, 600))
        h = array.shape[0]
        w = array.shape[1]
        self.imgL.image = wx.ImageFromBuffer(w, h, array)
        self.imgL.Update()
        self.imgL.Refresh()
        # Logger.logg("GUI left image updated", Logger.info)

    def onNewText(self, event=None):
        text = event.GetMyVal()
        self.logTextField.AppendText(text + "\n")
        self.logTextField.Refresh()
        # Logger.logg("GUI text box updated", Logger.info)

    def onUpdateParametersBtn(self, event=None):
        dlg = ParameterDialog(self)
        dlg.ShowModal()
        result = dlg.result
        if result:
            with b.lock:
                b.params = result
                b.updateParamFlag = True

    def onStopBtn(self, event=None):
        with b.lock:
            b.stopFlag = True

    def onRun(self, event=None):
        with b.lock:
            b.runFlag = not b.runFlag

    def onSeekAndDestroy(self, event=None):
        with b.lock:
            b.seekAndDestroyFlag = not b.seekAndDestroyFlag

    def onManualBtn(self, event=None):
        # warning dialog
        if not self.controlledManually:
            wx.MessageBox('Use "w, s, a, d, r" to control the snake manually', 'Info', wx.OK | wx.ICON_INFORMATION)
        self.controlledManually = not self.controlledManually
        with b.lock:
            b.manualControlFlag = not b.manualControlFlag
        self.logTextField.AppendText(f"Snake manual mode: {self.controlledManually}\n")
        Logger.logg(f"GUI manual control: {self.controlledManually}", Logger.info)

    def onPrepareMazeSingle(self, event=None):
        # warning dialog
        wx.MessageBox('Make sure the maze is empty', 'Info', wx.OK | wx.ICON_INFORMATION)
        with b.lock:
            b.prepMazeSingle = True
        self.findPath.Enable()
        Logger.logg("GUI prepare maze btn pressed", Logger.info)

    def onPrepareMazeMulti(self, event=None):
        # Warning dialog
        wx.MessageBox('Make sure the maze is empty', 'Info', wx.OK | wx.ICON_INFORMATION)
        with b.lock:
            b.prepMazeMulti = True
        self.findPath2.Enable()
        Logger.logg("Gui prepare maze btn pressed", Logger.info)

    def onFindPathSingle(self, event=None):
        # warning dialog
        wx.MessageBox('Put the snake and the target in the maze', 'Info', wx.OK | wx.ICON_INFORMATION)
        with b.lock:
            b.findPathSingleFlag = True
        self.runBtn.Enable()
        Logger.logg("GUI find path btn preset", Logger.info)

    def onFindPathMulti(self, event=None):
        # Warning Dialog
        wx.MessageBox('Put the snake and the target in the maze', 'Info', wx.OK | wx.ICON_INFORMATION)
        with b.lock:
            b.findPathMultiFlag = True
        self.seekAndDestroy.Enable()
        Logger.logg("GUI Find Path Multi btn pressed", Logger.info)

    def onClose(self, event=None):
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

    def onKeyDown(self, event=None):
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
                  "UpdateTextEvent": UpdateTextEvent,
                  "YesNoEvent": YesNoEvent}
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
