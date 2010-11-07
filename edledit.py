import os
from datetime import timedelta

from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import Qt
from PyQt4.phonon import Phonon

import pyedl

from edledit_ui import Ui_MainWindow

# TODO about box
# TODO BUG: load movie does not trigger videoChanged
# TODO BUG: stop cut behaviour when already within a cut block
# TODO BUG: error while loading movie put app in incoherent state
# TODO actions on selected block:
# TODO - delete block
# TODO - move selected block start/end to currentTime
# TODO - editable start/stop
# TODO general exception handling
# TODO review the lastMove mechanism

def timedelta2ms(td):
    return td.days*86400000 + td.seconds*1000 + td.microseconds//1000

def ms2timedelta(ms):
    return timedelta(milliseconds=ms)

class EDLTableModel(QtCore.QAbstractTableModel): 

    ACTION_EYE = 0
    ACTION_CUT = 1 

    def __init__(self, edl, totalTime, parent=None, *args): 
        QtCore.QAbstractTableModel.__init__(self, parent, *args) 
        self.edl = edl
        self.totalTime = totalTime
        self.viewList = self._makeViewList(edl, totalTime)
        self.currentTime = None
        self.currentTimeIndex = -1
        # icons
        eye_icon = QtGui.QIcon()
        eye_icon.addPixmap(QtGui.QPixmap(":/images/eye.png"), 
                QtGui.QIcon.Normal, QtGui.QIcon.Off)
        cut_icon = QtGui.QIcon()
        cut_icon.addPixmap(QtGui.QPixmap(":/images/cut.png"), 
                QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.viewIcons = [eye_icon, cut_icon]
 
    def _makeViewList(self, edl, totalTime):
        l = []
        if edl and edl[0].startTime:
            l.append((self.ACTION_EYE, timedelta(0)))
        prevBlock = None
        for block in edl:
            if prevBlock and block.startTime > prevBlock.stopTime:
                l.append((self.ACTION_EYE, prevBlock.stopTime))
            l.append((self.ACTION_CUT, block.startTime))
            prevBlock = block
        if prevBlock and prevBlock.stopTime and totalTime > prevBlock.stopTime:
            l.append((self.ACTION_EYE, prevBlock.stopTime))
        return l

    def getCurrentTimeIndex(self):
        cti = 0
        for a, t in self.viewList[1:]:
            if t > self.currentTime:
                return cti
            cti += 1
        return cti

    def setCurrentTime(self, t):
        self.currentTime = t
        cti = self.getCurrentTimeIndex()
        if cti != self.currentTimeIndex:
            self.dataChanged.emit(
                    self.createIndex(self.currentTimeIndex, 1), 
                    self.createIndex(self.currentTimeIndex, 1))
            self.currentTimeIndex = cti
            self.dataChanged.emit(
                    self.createIndex(self.currentTimeIndex, 1), 
                    self.createIndex(self.currentTimeIndex, 1))

    def emitChanged(self):
        self.viewList = self._makeViewList(self.edl, self.totalTime)
        self.emit(QtCore.SIGNAL("layoutChanged()"))

    def getTimeForIndex(self, index):
        return self.viewList[index.row()][1]

    # QAbstractTableModel overrides

    def rowCount(self, parent): 
        return len(self.viewList)
 
    def columnCount(self, parent): 
        return 2
 
    def data(self, index, role): 
        if role == Qt.DisplayRole: 
            if index.column() == 1:
                t = self.viewList[index.row()][1]
                hours, remainder = divmod(t.seconds, 3600)
                hours = t.days*24 + hours
                minutes, seconds = divmod(remainder, 60)
                milliseconds = t.microseconds//1000
                return "%02d:%02d:%02d.%03d" % (hours, minutes,
                        seconds, milliseconds)
        elif role == Qt.FontRole:
            if index.column() == 1 and index.row() == self.currentTimeIndex:
                font = QtGui.QFont()
                font.setBold(True)
                return font
        elif role == Qt.DecorationRole:
            if index.column() == 0:
                return self.viewIcons[self.viewList[index.row()][0]]
        return QtCore.QVariant()

    def headerData(self, col, orientation, role):
        headerdata = ["", "Time code"]
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return QtCore.QVariant(headerdata[col])
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

        # initialize media components
        mediaObject = self.ui.player.mediaObject()
        mediaObject.setTickInterval(100)
        mediaObject.hasVideoChanged.connect(self.videoChanged)
        mediaObject.tick.connect(self.refreshTimeWidget)
        self.ui.slider.setMediaObject(mediaObject)

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
        self.edlModel = EDLTableModel(self.edl, 
                ms2timedelta(self.ui.player.totalTime()), self)
        self.ui.edlTable.setModel(self.edlModel)
        self.ui.edlTable.setColumnWidth(0, 22)
        self.ui.edlTable.setColumnWidth(1, 100)
        self.ui.action_Save_EDL.setEnabled(True)
        self.ui.btCutStart.setEnabled(True)
        self.ui.btCutStop.setEnabled(True)

    def saveEDL(self):
        assert self.edlFileName
        assert self.edl is not None
        self.edl.normalize(timedelta(milliseconds=self.ui.player.totalTime()))
        self.edlModel.emitChanged()
        pyedl.dump(self.edl, open(self.edlFileName, "w"))

    def closeEDL(self):
        self.ui.btGotoNextBoundary.setEnabled(False)
        self.ui.btGotoPrevBoundary.setEnabled(False)
        self.edlFileName = None
        self.edl = None
        self.edlModel = EDLTableModel(self.edl, timedelta(0), self)
        self.ui.edlTable.setModel(self.edlModel)
        self.ui.action_Save_EDL.setEnabled(False)
        self.ui.btCutStart.setEnabled(False)
        self.ui.btCutStop.setEnabled(False)

    def play(self):
        if not self.ui.player.isPlaying():
            self.ui.player.play()
            self.ui.btPlayPause.setIcon(self.play_icon)

    def pause(self):
        if self.ui.player.isPlaying():
            self.ui.player.pause()
            self.ui.btPlayPause.setIcon(self.pause_icon)
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
        self.movieFileName = fileName
        self.setWindowTitle("EDL Editor - " + fileName)
        self.ui.player.load(Phonon.MediaSource(self.movieFileName))

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
        self.edlModel.setCurrentTime(ms2timedelta(timeMs))

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
        t = self.edlModel.getTimeForIndex(index)
        self.seekTo(timedelta2ms(t))
        #self.ui.edlTable.selectRow(index.row())

    def togglePlayPause(self):
        if not self.ui.player.isPlaying():
            self.play()
        else:
            self.pause()

    def cutStart(self):
        t = timedelta(milliseconds=self.ui.player.currentTime())
        self.edl.cutStart(t)
        self.edlModel.emitChanged()

    def cutStop(self):
        t = timedelta(milliseconds=self.ui.player.currentTime())
        self.edl.cutStop(t)
        self.edlModel.emitChanged()

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
        mainWindow.loadMovie(sys.argv[1].decode("utf8"))
    sys.exit(app.exec_())

