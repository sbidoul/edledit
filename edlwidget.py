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

def timedelta2ms(td):
    return td.days*86400000 + td.seconds*1000 + td.microseconds//1000

class EDLWidget(QtGui.QWidget):

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
        self.__edl = []
        self.__totalTime = None

    def ms2pixels(self, ms):
        if self.__totalTime:
            return int(ms*self.width()/self.__totalTime)
        else:
            return 0

    def tick(self, timeMs):
        self.__currentTime = timeMs
        self.update()

    def paintEvent(self, event):
        w = self.width()
        h = self.height()
        paint = QtGui.QPainter()
        paint.begin(self)
        paint.setPen(Qt.NoPen)
        paint.setBrush(Qt.green)
        paint.drawRect(0, 0, w, h)
        paint.setBrush(Qt.red)
        for block in self.__edl:
            startPos = self.ms2pixels(timedelta2ms(block.startTime))
            if block.stopTime is None:
                stopPos = w
            else:
                stopPos = self.ms2pixels(timedelta2ms(block.stopTime))
            paint.drawRect(startPos, 0, stopPos-startPos, h)
        if self.__currentTime is not None:
            paint.setPen(Qt.black)
            startPos = min(self.ms2pixels(self.__currentTime), w-1)
            paint.drawLine(startPos, 0, startPos, h)
        paint.end()

