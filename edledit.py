import os
from datetime import timedelta

from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import Qt
from PyQt4.phonon import Phonon

import pyedl

from edledit_ui import Ui_MainWindow

# TODO actions on selected block:
# TODO - delete block
# TODO - move selected block start/end to currentTime
# TODO - editable start/stop
# TODO highlight current block in edl table, different highlight than selection
# TODO highlight current start/stop in edl table if currentTime is on a
#      boundary
# TODO general exception handling
# TODO highlight invalid blocks + reason in edl table
# TODO editable time counter?
# TODO review the lastMove mechanism

def timedelta2ms(td):
    return td.days*86400000 + td.seconds*1000 + td.microseconds//1000

def ms2timedelta(ms):
    return timedelta(milliseconds=ms)

class EDLTableModel(QtCore.QAbstractTableModel): 
    def __init__(self, edl, parent=None, *args): 
        QtCore.QAbstractTableModel.__init__(self, parent, *args) 
        self.edl = edl
        self.headerdata = ["Cut start", "Cut stop"]
 
    def emitChanged(self):
        self.emit(QtCore.SIGNAL("layoutChanged()"))

    def rowCount(self, parent): 
        return len(self.edl) 
 
    def columnCount(self, parent): 
        return 2
 
    def getTimedelta(self, index):
        edlBlock = self.edl[index.row()]
        if index.column() == 0:
            return edlBlock.startTime
        else:
            return edlBlock.stopTime

    def getTimeMilliseconds(self, index):
        t = self.getTimedelta(index)
        return timedelta2ms(t)

    def data(self, index, role): 
        if role == Qt.DisplayRole: 
            t = self.getTimedelta(index)
            if t is not None:
                hours, remainder = divmod(t.seconds, 3600)
                hours = t.days*24 + hours
                minutes, seconds = divmod(remainder, 60)
                milliseconds = t.microseconds//1000
                return QtCore.QVariant("%02d:%02d:%02d.%03d" % (hours, minutes,
                    seconds, milliseconds))
            else:
                return QtCore.QVariant()
        else:
            return QtCore.QVariant()

    def headerData(self, col, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return QtCore.QVariant(self.headerdata[col])
        else:
            return QtCore.QVariant()

    #def setData(self, index, value, role):
    #    print index, value, role
    #    #self.emit(QtCore.SIGNAL("dataChanged()"))
    #    return False

    #def flags(self, index):
    #    return Qt.ItemIsEditable | Qt.ItemIsEnabled

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
        for stepMs, stepText in self.steps:
            self.ui.stepCombobox.addItem(stepText)

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
        self.edlmodel = EDLTableModel(self.edl, self)
        self.ui.edlTable.setModel(self.edlmodel)
        self.ui.action_Save_EDL.setEnabled(True)
        self.ui.btCutStart.setEnabled(True)
        self.ui.btCutStop.setEnabled(True)

    def saveEDL(self):
        assert self.edlFileName
        assert self.edl is not None
        self.edl.normalize(timedelta(seconds=self.ui.player.totalTime()//1000))
        self.edlmodel.emitChanged()
        pyedl.dump(self.edl, open(self.edlFileName, "w"))

    def closeEDL(self):
        self.edlFileName = None
        self.edl = None
        self.ui.action_Save_EDL.setEnabled(False)
        self.ui.btCutStart.setEnabled(False)
        self.ui.btCutStop.setEnabled(False)

    def play(self):
        if not self.ui.player.isPlaying():
            self.ui.player.play()
            icon = QtGui.QIcon()
            icon.addPixmap(QtGui.QPixmap(":/images/control_pause.png"), 
                    QtGui.QIcon.Normal, QtGui.QIcon.Off)
            self.ui.btPlayPause.setIcon(icon)

    def pause(self):
        if self.ui.player.isPlaying():
            self.ui.player.pause()
            icon = QtGui.QIcon()
            icon.addPixmap(QtGui.QPixmap(":/images/control_play.png"), 
                    QtGui.QIcon.Normal, QtGui.QIcon.Off)
            self.ui.btPlayPause.setIcon(icon)
            self.refreshTimeWidget()

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
        if not self.ui.player.isPlaying():
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
        self.ui.timeEditCurrentTime.setTime(QtCore.QTime(0, 0).addMSecs(timeMs))

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
        if self.lastMove in ("b", "f"):
            self.setStep(self.defaultStepIndex)
        self.seekStep(self.getStep())

    def seekBackward(self):
        if self.lastMove in ("b", "f"):
            self.setStep(self.defaultStepIndex)
        self.seekStep(-self.getStep())

    def seekNextBoundary(self):
        self.pause()
        t = ms2timedelta(self.ui.player.currentTime())
        t = self.edl.getNextBoundary(t)
        if t:
            self.seekTo(timedelta2ms(t))
        else:
            self.seekTo(self.ui.player.totalTime())

    def seekPrevBoundary(self):
        self.pause()
        t = ms2timedelta(self.ui.player.currentTime())
        t = self.edl.getPrevBoundary(t)
        if t:
            self.seekTo(timedelta2ms(t))
        else:
            self.seekTo(0)

    def seekBoundary(self, index):
        t = self.edlmodel.getTimeMilliseconds(index)
        self.seekTo(t)
        #self.ui.edlTable.selectRow(index.row())

    def togglePlayPause(self):
        if not self.ui.player.isPlaying():
            self.play()
        else:
            self.pause()

    def cutStart(self):
        t = timedelta(milliseconds=self.ui.player.currentTime())
        self.edl.blockStart(t)
        self.edlmodel.emitChanged()

    def cutStop(self):
        t = timedelta(milliseconds=self.ui.player.currentTime())
        self.edl.blockStop(t)
        self.edlmodel.emitChanged()

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

