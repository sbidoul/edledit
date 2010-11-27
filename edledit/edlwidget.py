# This file is part of edledit.
# Copyright (C) 2010 Stephane Bidoul
#
# edledit is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# edledit is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with edledit.  If not, see <http://www.gnu.org/licenses/>.

from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import Qt

import pyedl

def timedelta2ms(td):
    return td.days*86400000 + td.seconds*1000 + td.microseconds//1000

HCURSOR = 5
WCURSOR = 5

class EDLWidget(QtGui.QWidget):

    # signals

    seek = QtCore.pyqtSignal('qint64')

    def __init__(self, *args, **kwargs):
        QtGui.QWidget.__init__(self, *args, **kwargs)
        self.__edl = []
        self.__totalTime = None # ms
        self.__currentTime = None # ms

    def setEDL(self, edl, totalTime):
        self.__edl = edl
        self.__totalTime = totalTime
        if totalTime is not None:
            self.__currentTime = max(self.__currentTime, 0)
            self.__currentTime = min(self.__currentTime, self.__totalTime)
        else:
            self.__currentTime = None
        self.update()

    def resetEDL(self):
        self.setEDL([], None)
        self.update()

    def ms2pixels(self, ms):
        if self.__totalTime:
            w = self.width()-WCURSOR*2
            x = ms*w//self.__totalTime
            return x+WCURSOR
        else:
            return WCURSOR

    def pixels2ms(self, x):
        if self.__totalTime:
            w = self.width()-WCURSOR*2
            x = max(x-WCURSOR, 0)
            ms = x*self.__totalTime//w
            return ms
        else:
            return 0

    def createPaths(self):
        h = self.height()
        self.gradientGreen = QtGui.QLinearGradient(0, h, 0, 0)
        self.gradientGreen.setColorAt(0.0, QtGui.QColor(0, 100, 0))
        self.gradientGreen.setColorAt(0.5, QtGui.QColor(0, 255, 0))
        self.gradientGreen.setSpread(QtGui.QGradient.ReflectSpread)
        self.gradientRed = QtGui.QLinearGradient(0, h, 0, 0)
        self.gradientRed.setColorAt(0.0, QtGui.QColor(100, 0, 0))
        self.gradientRed.setColorAt(0.5, QtGui.QColor(255, 0, 0))
        self.gradientRed.setSpread(QtGui.QGradient.ReflectSpread)
        self.gradientBlue = QtGui.QLinearGradient(0, h, 0, 0)
        self.gradientBlue.setColorAt(0.0, QtGui.QColor(0, 0, 100))
        self.gradientBlue.setColorAt(0.5, QtGui.QColor(0, 0, 255))
        self.gradientBlue.setSpread(QtGui.QGradient.ReflectSpread)
        self.pathCutStart = QtGui.QPainterPath()
        self.pathCutStart.moveTo(2, HCURSOR)
        self.pathCutStart.lineTo(0, HCURSOR)
        self.pathCutStart.lineTo(0, h-HCURSOR)
        self.pathCutStart.lineTo(2, h-HCURSOR)
        self.pathCutStop = QtGui.QPainterPath()
        self.pathCutStop.moveTo(-2, HCURSOR)
        self.pathCutStop.lineTo(0, HCURSOR)
        self.pathCutStop.lineTo(0, h-HCURSOR)
        self.pathCutStop.lineTo(-2, h-HCURSOR)
        self.pathPointer = QtGui.QPainterPath()
        self.pathPointer.moveTo(-HCURSOR,0)
        self.pathPointer.lineTo(HCURSOR,0)
        self.pathPointer.lineTo(0,HCURSOR)
        self.pathPointer.closeSubpath()
        self.pathPointer.moveTo(-HCURSOR,h-1)
        self.pathPointer.lineTo(HCURSOR,h-1)
        self.pathPointer.lineTo(0,h-1-HCURSOR)
        self.pathPointer.closeSubpath()

    # slots

    @QtCore.pyqtSlot('qint64')
    def tick(self, timeMs):
        self.__currentTime = timeMs
        self.update()

    # handle events

    def resizeEvent(self, event):
        self.createPaths()

    def mousePressEvent(self, event):
        if self.__totalTime:
            self.seek.emit(self.pixels2ms(event.x()))

    def paintEvent(self, event):
        w = self.width()
        h = self.height()
        paint = QtGui.QPainter()
        paint.begin(self)
        # draw green block covering all surface
        paint.setPen(Qt.NoPen)
        paint.setBrush(self.gradientGreen)
        paint.drawRect(WCURSOR, HCURSOR, w-WCURSOR*2, h-HCURSOR*2)
        # draw cut blocks
        for block in self.__edl:
            startPos = self.ms2pixels(timedelta2ms(block.startTime))
            if block.stopTime is None:
                stopPos = self.ms2pixels(self.__totalTime)
            else:
                stopPos = self.ms2pixels(timedelta2ms(block.stopTime))
            # red block
            if block.action == pyedl.ACTION_SKIP:
                paint.setBrush(self.gradientRed)
            elif block.action == pyedl.ACTION_MUTE:
                paint.setBrush(self.gradientBlue)
            else:
                paint.setBrush(self.gradientRed)
            paint.drawRect(startPos, HCURSOR, stopPos-startPos, h-HCURSOR*2)
            # cut start and cut stop
            paint.save()
            pen = QtGui.QPen(Qt.black)
            pen.setWidth(3)
            paint.setPen(pen)
            paint.translate(startPos, 0)
            paint.drawPath(self.pathCutStart)
            paint.translate(stopPos-startPos, 0)
            paint.drawPath(self.pathCutStop)
            paint.restore()
        # draw current position pointer
        if self.__currentTime is not None:
            paint.setPen(Qt.black)
            startPos = self.ms2pixels(self.__currentTime)
            paint.save()
            paint.setPen(Qt.darkGray)
            paint.setBrush(Qt.darkGray)
            paint.translate(startPos, 0)
            paint.drawPath(self.pathPointer)
            paint.restore()
        paint.end()

