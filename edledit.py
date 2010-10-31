import os

from PyQt4 import QtCore, QtGui
from PyQt4.phonon import Phonon

import pyedl

from edleditui import Ui_MainWindow

class MainWindow(QtGui.QMainWindow):

    steps = [ (    40,  "40 ms"), 
              (   100, "0.1 sec"),
              (   500, "0.5 sec"), 
              (  1000,   "1 sec"),
              (  5000,   "5 sec"),
              ( 30000,  "30 sec"),
              ( 60000,   "1 min"),
              (300000,   "5 min"),
              (600000,  "10 min"), ]

    defaultStepIndex = 7

    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        #self.timerId = None
        self.movieFileName = None
        self.edlFileName = None
        self.edl = None
        self.setStep(self.defaultStepIndex)
        self.lastMove = None

    # logic 

    def loadEDL(self):
        assert self.movieFileName
        basename = os.path.splitext(self.movieFileName)[0]
        self.edlFileName = basename + ".edl"
        if os.path.exists(self.edlFileName):
            self.edl = pyedl.load(open(self.edlFileName))
        else:
            self.edl = pyedl.EDL()
        self.ui.action_Save_EDL.setEnabled(True)
        self.ui.btCutStart.setEnabled(True)
        self.ui.btCutStop.setEnabled(True)

    def saveEDL(self):
        assert self.edlFileName
        assert self.edl is not None
        pyedl.dump(self.edl, open(self.edlFileName,"w"))

    def closeEDL(self):
        self.edlFileName = None
        self.edl = None
        self.ui.action_Save_EDL.setEnabled(False)
        self.ui.btCutStart.setEnabled(False)
        self.ui.btCutStop.setEnabled(False)

    def play(self):
        #if self.timerId is None:
        #    self.timerId = self.startTimer(50)
        if not self.ui.player.isPlaying():
            self.ui.player.play()

    def pause(self):
        #if self.timerId is not None:
        #    self.killTimer(self.timerId)
        #    self.timerId = None
        if self.ui.player.isPlaying():
            self.ui.player.pause()
        self.refreshTimeWidget()

    #def timerEvent(self,event):
    #    self.refreshTimeWidget()

    def setStep(self,stepIndex):
        self.stepIndex = stepIndex
        self.stepIndex = max(self.stepIndex, 0)
        self.stepIndex = min(self.stepIndex, len(self.steps)-1)
        self.step = self.steps[self.stepIndex][0]
        self.ui.labelStep.setText(self.steps[self.stepIndex][1])

    def loadMovie(self,fileName):
        self.closeEDL()
        self.movieFileName = fileName
        self.setWindowTitle("EDL Editor - " + fileName)
        self.ui.player.load(Phonon.MediaSource(self.movieFileName))
        mediaObject = self.ui.player.mediaObject()
        mediaObject.setTickInterval(100)
        mediaObject.hasVideoChanged.connect(self.videoChanged)
        mediaObject.tick.connect(self.refreshTimeWidget)
        self.ui.slider.setMediaObject(mediaObject)

    def seekTo(self, pos, lastMove=None):
        pos = max(pos, 0)
        pos = min(pos, self.ui.player.totalTime())
        self.ui.player.seek(pos)
        self.refreshTimeWidget()
        self.lastMove = lastMove

    def seekStep(self, step, lastMove=None):
        pos = self.ui.player.currentTime() + step
        self.seekTo(pos, lastMove)

    # slots

    def videoChanged(self):
        if self.ui.player.mediaObject().hasVideo():
            seekable = self.ui.player.mediaObject().isSeekable()
            self.ui.btPlayPause.setEnabled(True)
            self.ui.btGotoNextBoundary.setEnabled(seekable)
            self.ui.btGotoPrevBoundary.setEnabled(seekable)
            self.ui.btSmartStepBackward.setEnabled(seekable)
            self.ui.btSmartStepForward.setEnabled(seekable)
            self.ui.btStepBackward.setEnabled(seekable)
            self.ui.btStepForward.setEnabled(seekable)
            self.loadEDL()
            self.play()
        else:
            self.ui.btPlayPause.setEnabled(False)
            self.ui.btGotoNextBoundary.setEnabled(False)
            self.ui.btGotoPrevBoundary.setEnabled(False)
            self.ui.btSmartStepBackward.setEnabled(False)
            self.ui.btSmartStepForward.setEnabled(False)
            self.ui.btStepBackward.setEnabled(False)
            self.ui.btStepForward.setEnabled(False)

    def refreshTimeWidget(self, timeMs=None):
        if timeMs is None:
            timeMs = self.ui.player.currentTime()
        self.ui.timeEditCurrentTime.setTime(QtCore.QTime(0,0).addMSecs(timeMs))

    def stepUp(self):
        self.setStep(self.stepIndex+1)
        self.lastMove = None

    def stepDown(self):
        self.setStep(self.stepIndex-1)
        self.lastMove = None

    def smartSeekBackward(self):
        if self.lastMove != "b":
            # smart bebhaviour unless last
            # action was smartSeekBackward
            self.stepDown()
            if self.step <= 5000:
                self.pause()
        self.seekStep(-self.step, "b")

    def smartSeekForward(self):
        if self.lastMove != "f":
            # smart bebhaviour unless last
            # action was smartSeekForward
            self.stepDown()
            if self.step <= 5000:
                self.pause()
        self.seekStep(self.step, "f")

    def seekForward(self):
        if self.lastMove in ("b","f"):
            self.setStep(self.defaultStepIndex)
        self.seekStep(self.step)

    def seekBackward(self):
        if self.lastMove in ("b","f"):
            self.setStep(self.defaultStepIndex)
        self.seekStep(-self.step)

    def seekNextBoundary(self):
        # TODO
        self.seekTo(self.ui.player.totalTime())

    def seekPreviousBoundary(self):
        # TODO
        self.seekTo(0)

    def togglePlayPause(self):
        if not self.ui.player.isPlaying():
            self.play()
        else:
            self.pause()

    def actionFileOpen(self):
        fileName = QtGui.QFileDialog.getOpenFileName(
                self, "Select movie file to open", "", 
                "All Movie Files (*.mkv *.mpg *.avi);;All Files (*.*)")
        if fileName:
            # unicode() to convert from QString
            self.loadMovie(unicode(fileName))

    def actionFileSaveEDL(self):
        self.saveEDL()

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    app.setApplicationName("edledit")
    mainWindow = MainWindow()
    mainWindow.show()
    if len(sys.argv) == 2:
        mainWindow.loadMovie(sys.argv[1])
    sys.exit(app.exec_())

