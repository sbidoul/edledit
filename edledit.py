#!/usr/bin/python

import os, mimetypes
from datetime import timedelta

from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import Qt
from PyQt4.phonon import Phonon

import pyedl

from edledit_ui import Ui_MainWindow

# initialize mimetypes database
mimetypes.init()

def timedelta2ms(td):
    return td.days*86400000 + td.seconds*1000 + td.microseconds//1000

def ms2timedelta(ms):
    return timedelta(milliseconds=ms)

class MainWindow(QtGui.QMainWindow):

    steps = [ (    40,   "4 msec"), 
              (   200,  "20 msec"),
              (   500,  "0.5 sec"), 
              (  2000,    "2 sec"),
              (  5000,    "5 sec"),
              ( 20000,   "20 sec"),
              ( 60000,    "1 min"),
              (300000,    "5 min"),
              (600000,   "10 min"), ]

    defaultStepIndex = 7

    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # initialize media components
        mediaObject = self.ui.player.mediaObject()
        mediaObject.setTickInterval(200)
        mediaObject.hasVideoChanged.connect(self.videoChanged)
        mediaObject.tick.connect(self.tick)

        # populate steps combo box
        for stepMs, stepText in self.steps:
            self.ui.stepCombobox.addItem(stepText)

        # icons
        self.play_icon = QtGui.QIcon()
        self.play_icon.addPixmap(QtGui.QPixmap(":/images/control_pause.png"), 
                QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.pause_icon = QtGui.QIcon()
        self.pause_icon.addPixmap(QtGui.QPixmap(":/images/control_play.png"), 
                QtGui.QIcon.Normal, QtGui.QIcon.Off)

        self.movieFileName = None
        self.edlFileName = None
        self.edl = None
        self.edlDirty = False
        self.setStep(self.defaultStepIndex)
        self.lastMove = None

    # logic 

    def loadEDL(self):
        assert self.movieFileName
        self.edlFileName = os.path.splitext(self.movieFileName)[0] + ".edl"
        if os.path.exists(self.edlFileName):
            self.edl = pyedl.load(open(self.edlFileName))
        else:
            self.edl = pyedl.EDL()
        self.edlDirty = False
        self.ui.edlWidget.setEDL(self.edl, self.ui.player.totalTime())
        self.ui.action_Save_EDL.setEnabled(True)
        self.ui.btCutStart.setEnabled(True)
        self.ui.btCutStop.setEnabled(True)
        self.ui.btCutDelete.setEnabled(True)
        self.refreshTitle()

    def saveEDL(self):
        assert self.edlFileName
        assert self.edl is not None
        self.edl.normalize(timedelta(milliseconds=self.ui.player.totalTime()))
        pyedl.dump(self.edl, open(self.edlFileName, "w"))
        self.edlChanged(dirty=False)

    def closeEDL(self):
        self.ui.btGotoNextBoundary.setEnabled(False)
        self.ui.btGotoPrevBoundary.setEnabled(False)
        self.edlFileName = None
        self.edl = None
        self.edlDirty = False
        self.ui.edlWidget.resetEDL()
        self.ui.action_Save_EDL.setEnabled(False)
        self.ui.btCutStart.setEnabled(False)
        self.ui.btCutStop.setEnabled(False)
        self.ui.btCutDelete.setEnabled(False)
        self.refreshTitle()

    def play(self):
        if not self.ui.player.isPlaying():
            self.ui.player.play()
            self.ui.btPlayPause.setIcon(self.play_icon)

    def pause(self):
        if self.ui.player.isPlaying():
            self.ui.player.pause()
            self.ui.btPlayPause.setIcon(self.pause_icon)
            self.tick()

    def getStep(self):
        stepIndex = self.ui.stepCombobox.currentIndex()
        return self.steps[stepIndex][0]

    def setStep(self, stepIndex):
        stepIndex = max(stepIndex, 0)
        stepIndex = min(stepIndex, len(self.steps)-1)
        self.ui.stepCombobox.setCurrentIndex(stepIndex)

    def stepDown(self):
        stepIndex = self.ui.stepCombobox.currentIndex()
        self.setStep(stepIndex - 1)
        
    def stepUp(self):
        stepIndex = self.ui.stepCombobox.currentIndex()
        self.setStep(stepIndex + 1)

    def loadMovie(self, fileName):
        self.closeEDL()
        self.movieFileName = fileName
        self.ui.player.load(Phonon.MediaSource(self.movieFileName))

    def seekTo(self, pos, lastMove=None):
        pos = max(pos, 0)
        pos = min(pos, self.ui.player.totalTime())
        self.ui.player.seek(pos)
        if not self.ui.player.isPlaying():
            self.tick()
        self.lastMove = lastMove

    def seekStep(self, step, lastMove=None):
        pos = self.ui.player.currentTime() + step
        self.seekTo(pos, lastMove)

    def edlChanged(self, dirty):
        self.edlDirty = dirty
        self.ui.edlWidget.setEDL(self.edl, self.ui.player.totalTime())
        self.refreshTitle()

    def refreshTitle(self):
        if self.edlFileName:
            if self.edlDirty:
                star = "*"
            else:
                star = ""
            head, tail = os.path.split(os.path.abspath(self.edlFileName))
            self.setWindowTitle("%s%s (%s) - edledit" % (star, tail, head))
        else:
            self.setWindowTitle("edledit")

    # slots

    def closeEvent(self, event):
        if self.askSave():
            event.accept()
        else:
            event.ignore()

    def askSave(self):
        """ If needed, ask the user to save the current EDL 

        return True is we can proceed, False is the user selected Cancel.
        """
        if not self.edlDirty:
            return True
        msgBox = QtGui.QMessageBox(self)
        msgBox.setIcon(QtGui.QMessageBox.Question)
        msgBox.setText("The current EDL has been modified.")
        msgBox.setInformativeText("Do you want to save your changes?")
        msgBox.setStandardButtons(QtGui.QMessageBox.Save | 
                QtGui.QMessageBox.Discard | QtGui.QMessageBox.Cancel)
        msgBox.setDefaultButton(QtGui.QMessageBox.Save)
        ret = msgBox.exec_()
        if ret == QtGui.QMessageBox.Save:
            self.saveEDL()
            return True
        elif ret == QtGui.QMessageBox.Discard:
            return True
        else:
            return False

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

    def tick(self, timeMs=None):
        if timeMs is None:
            timeMs = self.ui.player.currentTime()
        self.ui.timeEditCurrentTime.setTime(QtCore.QTime(0, 0).addMSecs(timeMs))
        self.ui.edlWidget.tick(timeMs)

    def smartSeekBackward(self):
        if self.lastMove != "b":
            # smart bebhaviour unless last
            # action was smartSeekBackward
            self.stepDown()
            if self.getStep() <= 5000:
                self.pause()
        self.seekStep(-self.getStep(), "b")

    def smartSeekForward(self):
        if self.lastMove != "f":
            # smart bebhaviour unless last
            # action was smartSeekForward
            self.stepDown()
            if self.getStep() <= 5000:
                self.pause()
        self.seekStep(self.getStep(), "f")

    def seekForward(self):
        #if self.lastMove in ("b", "f"):
        #    self.setStep(self.defaultStepIndex)
        self.seekStep(self.getStep())

    def seekBackward(self):
        #if self.lastMove in ("b", "f"):
        #    self.setStep(self.defaultStepIndex)
        self.seekStep(-self.getStep())

    def seekNextBoundary(self):
        #self.pause()
        t = ms2timedelta(self.ui.player.currentTime())
        t = self.edl.getNextBoundary(t)
        if t:
            self.seekTo(timedelta2ms(t))
        else:
            self.seekTo(self.ui.player.totalTime())

    def seekPrevBoundary(self):
        #self.pause()
        t = ms2timedelta(self.ui.player.currentTime())
        t = self.edl.getPrevBoundary(t)
        if t:
            self.seekTo(timedelta2ms(t))
        else:
            self.seekTo(0)

    def seekBoundary(self, index):
        # TODO
        t = self.edlModel.getTimeForIndex(index)
        self.seekTo(timedelta2ms(t))

    def togglePlayPause(self):
        if not self.ui.player.isPlaying():
            self.play()
        else:
            self.pause()

    def cutStart(self):
        t = timedelta(milliseconds=self.ui.player.currentTime())
        self.edl.cutStart(t)
        self.edlChanged(dirty=True)

    def cutStop(self):
        t = timedelta(milliseconds=self.ui.player.currentTime())
        self.edl.cutStop(t)
        self.edlChanged(dirty=True)

    def cutDelete(self):
        t = timedelta(milliseconds=self.ui.player.currentTime())
        self.edl.deleteBlock(t)
        self.edlChanged(dirty=True)

    def actionFileOpen(self):
        if not self.askSave():
            return
        # get video file extensions from mime types database
        exts = ["*" + ext for (ext,mt) in mimetypes.types_map.items() 
                if mt.startswith("video/")]
        exts = " ".join(exts)
        fileName = QtGui.QFileDialog.getOpenFileName(
                self, "Select movie file to open", "", 
                "All Movie Files (%s);;All Files (*.*)" % exts)
        if fileName:
            # unicode() to convert from QString
            fileName = unicode(fileName)
            # change directory so next getOpenFileName will be in same dir
            os.chdir(os.path.split(fileName)[0])
            self.loadMovie(fileName)

    def actionFileSaveEDL(self):
        self.saveEDL()

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    app.setApplicationName("edledit")
    mainWindow = MainWindow()
    mainWindow.show()
    if len(sys.argv) == 2:
        mainWindow.loadMovie(sys.argv[1].decode("utf8"))
    sys.exit(app.exec_())

