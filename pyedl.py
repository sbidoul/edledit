import re
from datetime import timedelta

ACTION_NONE = None
ACTION_SKIP = 0
ACTION_MUTE = 1

_block_re = re.compile(r"(\d+(?:\.?\d+)?)\s(\d+(?:\.?\d+)?)\s([01])")

def _td2str(td):
    if td is None or td == timedelta.max:
        return ""
    else:
        return "%f" % (td.days*86400+td.seconds+td.microseconds/1000000.)

class EDLBlock(object):

    def __init__(self, startTime, stopTime, action=ACTION_SKIP):
        # pre-initialize so the validation during intialization will work
        self.__startTime = timedelta.min
        self.__stopTime = timedelta.max
        self.action = ACTION_NONE
        # set properties (validates)
        self.startTime = startTime
        self.stopTime = stopTime
        self.action = action

    @property
    def startTime(self):
        return self.__startTime

    @startTime.setter
    def startTime(self, value):
        if value > self.__stopTime:
            raise RuntimeError("start time must be before stop time")
        self.__startTime = value

    @property
    def stopTime(self):
        if self.__stopTime == timedelta.max:
            return None
        else:
            return self.__stopTime

    @stopTime.setter
    def stopTime(self, value):
        if value is None:
            value = timedelta.max
        if value < self.__startTime:
            raise RuntimeError("end time must be after start timer")
        self.__stopTime = value

    def __str__(self):
        return "%s\t%s\t%d" % (_td2str(self.startTime), _td2str(self.stopTime), 
                self.action)

    def overlaps(self, block):
        # not optimal but easy to understand
        return self.containsTime(block.__startTime) or \
                self.containsTime(block.__stopTime) or \
                block.containsTime(self.__startTime) or \
                block.containsTime(self.__stopTime)

    def containsTime(self, aTime):
        if aTime is None:
            aTime = timedelta.max
        return aTime >= self.__startTime and aTime < self.__stopTime

    def containsEndTime(self, aTime):
        if aTime is None:
            aTime = timedelta.max
        return aTime > self.__startTime and aTime <= self.__stopTime

class EDL(list):

    def findBlock(self, aTime):
        for block in self:
            if block.containsTime(aTime):
                return block
        return None

    def normalize(self, totalTime):
        for block in self:
            if block.stopTime is None or block.stopTime > totalTime:
                block.stopTime = totalTime
        self.validate()

    def blockStart(self, startTime, action=ACTION_SKIP):
        for i, block in enumerate(self):
            if block.containsTime(startTime):
                stopTime = block.stopTime
                block.stopTime = startTime
                self.insert(i+1, EDLBlock(startTime, stopTime, action))
                return
            elif block.startTime >= startTime:
                stopTime = block.startTime
                self.insert(i, EDLBlock(startTime, stopTime, action))
                return
        self.append(EDLBlock(startTime, None, action))

    def blockStop(self, stopTime, action=ACTION_SKIP):
        prevBlock = None
        for i, block in enumerate(self):
            if block.containsTime(stopTime):
                block.stopTime = stopTime
                return
            elif block.startTime >= stopTime:
                if prevBlock:
                    startTime = prevBlock.stopTime
                else:
                    startTime = timedelta(0)
                self.insert(i, EDLBlock(startTime, stopTime, action))
                return
            prevBlock = block
        if prevBlock:
            startTime = prevBlock.stopTime
        else:
            startTime = timedelta(0)
        self.append(EDLBlock(startTime, stopTime, action))

    def deleteBlock(self, aTime):
        """ Delete the block overlapping aTime """
        for i, block in enumerate(self):
            if block.containsTime(aTime):
                del self[i:i+1]
                return
        raise RuntimeError("No block found containing time %s" % aTime)

    def getNextBoundary(self, aTime):
        for block in self:
            if block.startTime > aTime:
                return block.startTime
            if block.stopTime > aTime:
                return block.stopTime
        return None

    def getPrevBoundary(self, aTime):
        for block in reserve(self):
            if block.stopTime < aTime:
                return block.stopTime
            if block.startTime < aTime:
                return block.startTime
        return timedelta(0)

    def validate(self):
        prevBlock = None
        for block in self:
            if not isinstance(block,EDLBlock):
                raise RuntimeError("Element %s not an EDLBlock" % (block,))
            if prevBlock is not None:
                if prevBlock.startTime >= block.startTime:
                    raise RuntimeError("block '%s' and '%s' not in order" % \
                            (prevBlock,block))
                if prevBlock.overlaps(block):
                    raise RuntimeError("block '%s' overlaps block '%s'" % \
                            (prevBlock,block))
            prevBlock = block

def load(fp):
    edl = EDL()
    for line in fp.readlines():
        line = line.strip()
        if not line:
            pass
        mo = _block_re.match(line)
        if not mo:
            raise RuntimeError("Invalid EDL line: '%s'" % (line,))
        start,stop,action = mo.groups()
        edl.append(EDLBlock(
            timedelta(seconds=float(start)),
            timedelta(seconds=float(stop)),
            int(action)))
    return edl

def dump(edl,f):
    for block in edl:
        f.write(str(block))
        f.write("\n")

if __name__ == "__main__":
    import sys
    l = load(open("test.edl"))
    dump(l,sys.stdout)
    print
    print EDLBlock(timedelta(seconds=10.1),
            timedelta(days=1,seconds=12.2,milliseconds=30))
    print
    l = EDL()
    l.blockStart(timedelta(seconds=10))
    dump(l,sys.stdout)
    print
    l.blockStop(timedelta(seconds=12))
    dump(l,sys.stdout)
    print
    l.blockStart(timedelta(minutes=1,seconds=30))
    dump(l,sys.stdout)
    print
    l.deleteBlock(timedelta(seconds=11))
    dump(l,sys.stdout)
    print
    l.validate()
    l.append(EDLBlock(timedelta(seconds=91),timedelta(seconds=100)))
    dump(l,sys.stdout)
    l.validate()
