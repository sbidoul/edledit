from PyQt4 import QtCore, QtGui
from PyQt4.phonon import Phonon

from edleditui import Ui_MainWindow

class MainWindow(QtGui.QMainWindow):

    steps = [ (40,"40 ms"), 
              (100,"0.1 sec"),
              (500,"0.5 sec"), 
              (1000, "1 sec"),
              (5000, "5 sec"),
              (30000, "30 sec"),
              (60000, "1 min"),
              (300000, "5 min"),
              (600000, "10 min"), ]

    defaultStepIndex = 7

    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        #self.timerId = None
        self.movieFileName = None
        self.setStep(self.defaultStepIndex)
        self.lastMove = None

    # logic 

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
        self.movieFileName = fileName
        self.ui.player.load(Phonon.MediaSource(self.movieFileName))
        self.ui.player.mediaObject().setTickInterval(100)
        # For some reason this does not work...
        #self.connect(self.ui.player.mediaObject(),
        #        QtCore.SIGNAL("tick(int)"), 
        #        self.refreshTimeWidget)
        self.ui.player.mediaObject().tick.connect(self.refreshTimeWidget)
        self.ui.slider.setMediaObject(self.ui.player.mediaObject())
        self.play()

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

    def refreshTimeWidget(self, timeMs=None):
        print "*"
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
            self.loadMovie(fileName)


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    app.setApplicationName("edledit")
    mainWindow = MainWindow()
    mainWindow.show()
    if len(sys.argv) == 2:
        mainWindow.loadMovie(sys.argv[1])
    sys.exit(app.exec_())

