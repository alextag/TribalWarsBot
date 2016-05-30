import win32gui, re, time, threading, random, sys, os
from win32con import *
import win32com.client as comclt
import pythoncom


WORLD_FROM_BOTTOM = 55
XCOORD_FROM_BOTTOM = 175
MOVE_FROM_COORD = 200
TIME_UNIT = 1.0

class village():

    def __init__(self, pos, preset):
        self.pos = (str(pos[0]),str(pos[1]))
        self.preset = str(preset)

    def distance(self, other):
        pos = (int(self.pos[0]),int(self.pos[1]))
        others = (int(other[0]),int(other[1]))
        xs = (pos[0]-others[0])*(pos[0]-others[0])
        ys = (pos[1]-others[1])*(pos[1]-others[1])
        return xs + (0.75*ys)#np.sqrt(xs + (0.75*ys))  # Could remove sqrt for #PERFORMANCE

    def __str__(self):
        return "("+str(self.pos[0])+"|"+str(self.pos[1])+") - Preset: " + str(self.preset)

class WindowMgr:
    """Encapsulates some calls to the winapi for window management"""
    def __init__ (self):
        """Constructor"""
        self._handle = None

    def find_window(self, class_name, window_name = None):
        """find a window by its class_name"""
        self._handle = win32gui.FindWindow(class_name, window_name)

    def _window_enum_callback(self, hwnd, wildcard):
        '''Pass to win32gui.EnumWindows() to check all the opened windows'''
        if re.match(wildcard, str(win32gui.GetWindowText(hwnd))) != None:
            self._handle = hwnd

    def find_window_wildcard(self, wildcard):
        self._handle = None
        win32gui.EnumWindows(self._window_enum_callback, wildcard)

    def __int__(self):
        return self._handle

class Command:

    def __init__(self, attacker, villages, delay, startindex=0):
        self.villages = villages
        self.attackingVillage = attacker
        self.startindex = startindex
        self.delay = delay

    def __str__(self):
        return str(self.attackingVillage)

class timerThread (threading.Thread):

    def __init__(self, activeSets, commandQueue, timerFunc, orig, doneFunc, aThread):
        threading.Thread.__init__(self)
        self.activeSets = activeSets
        self.commandQueue = commandQueue
        self._stop = threading.Event()
        self.timerFunc = timerFunc
        self.orig = orig
        self._addSet = threading.Event()
        self.setToAdd = None
        self.setToStop = None
        self._stopSet = threading.Event()
        self.doneFunc = doneFunc
        self.aThread = aThread

    def run(self):
        while not self._stop.isSet():
            if self._addSet.isSet() and self.setToAdd is not None:
                self.activeSets.append(self.setToAdd)
                self.setToAdd = None
                self._addSet.clear()
                print "Added set: " + str(self.activeSets[-1][0])

            if self._stopSet.isSet() and self.setToStop is not None:
                i = 0
                while i < len(self.activeSets):
                    if self.activeSets[i][0] == self.setToStop:
                        del self.activeSets[i]
                    else:
                        i += 1

                self.aThread.stopSet(self.setToStop)

                self._stopSet.clear()
                self.doneFunc(self.orig, self.setToStop)
                #print "Removed set: " + str(self.setToStop)
                self.setToStop = None
            for com in self.activeSets:
                com[3] += TIME_UNIT
                if com[3] >= com[2]:
                    com[3] = 0
                    self.commandQueue.append(Command(com[0], com[1], self.orig.maptoattackdelay))
                    #print "Command Sent" + str(com[0])
            self.timerFunc(self.orig, self.activeSets)
            time.sleep(TIME_UNIT)

    def addSet(self):
        self._addSet.set()

    def stopSet(self, setID):
        while self._stopSet.isSet():
            time.sleep(0.1)
        self.setToStop = setID
        self._stopSet.set()

    def stop(self):
        self._stop.set()

class attackerThread (threading.Thread):

    def __init__(self, commandQueue, villaNumber, currentVillageFunction, orig):
        threading.Thread.__init__(self)
        self.commandQueue = commandQueue
        self._stop = threading.Event()
        self._stopSet = threading.Event()
        self.setsToStop = []
        self.currentVillage = 0
        self.villaNumber = villaNumber
        self.currentVillageFunction = currentVillageFunction
        self.orig = orig

    def run(self):
        while not self._stop.isSet():
            if len(self.commandQueue)>0:
                myCopy = self.commandQueue[0]
                time.sleep(5)
                if self._stopSet.isSet():  # and myCopy.attackingVillage in self.setsToStop:
                    self.removeSet()
                    myCopy = None
                    continue
                w = find_window()
                if w is None:
                    continue
                else:
                    focus_window(w)

                    #print "Attack initiated: " + str(myCopy.attackingVillage + 1)
                    pos = find_wold_map_pos(w)
                    close_world_map(w)
                    if self.villaNumber > 1 and self.currentVillage != myCopy.attackingVillage and myCopy.attackingVillage < self.villaNumber:
                        while self.currentVillage != myCopy.attackingVillage:

                            self.currentVillage += 1
                            if self.currentVillage >= self.villaNumber:
                                self.currentVillage = 0
                            self.currentVillageFunction(self.orig, self.currentVillage)
                            next_village(w)

                    click(w, pos)
                    for each in myCopy.villages:
                        if self._stopSet.isSet():  # and myCopy.attackingVillage in self.setsToStop:
                            self.removeSet()
                            break
                        if self._stop.isSet():
                            return
                        if int(each.preset) == -1 or int(each.pos[0]) == -1 or int(each.pos[1]) == -1:
                            continue
                        self.attack(w, each, myCopy.delay)
                        time.sleep(random.random())
                try:
                    if self.commandQueue[0] == myCopy:
                        del self.commandQueue[0]
                except IndexError:
                    continue
            time.sleep(TIME_UNIT)

    def attack(self, w, vil, delay):
        pos = find_wold_map_pos(w)
        click(w, (pos[0]-80, pos[1] - (XCOORD_FROM_BOTTOM - WORLD_FROM_BOTTOM)))
        time.sleep(0.1)
        if self._stop.isSet():
            return False
        send_clear(w) # CTR-A + backspace or delete would be optimal
        if self._stop.isSet():
            return False
        type(w, vil.pos[0])
        if self._stop.isSet():
            return False
        time.sleep(0.1)
        if self._stop.isSet():
            return False
        send_tab(w)
        if self._stop.isSet():
            return False
        time.sleep(0.1)
        if self._stop.isSet():
            return False
        send_clear(w)
        if self._stop.isSet():
            return False
        type(w, vil.pos[1])
        if self._stop.isSet():
            return False
        click(w, (pos[0] + MOVE_FROM_COORD, pos[1] - (XCOORD_FROM_BOTTOM - WORLD_FROM_BOTTOM)))
        if self._stop.isSet():
            return False
        time.sleep((delay/1000.0) + 1.5*random.random())
        if self._stop.isSet():
            return False
        type(w, vil.preset)
        return True

    def stop(self):
        self._stop.set()

    def stopSet(self, setID):
        self.setsToStop.append(setID)
        self._stopSet.set()

    def removeSet(self):
        self._stopSet.clear()
        myCopy = list(self.setsToStop)
        for each in myCopy:
            self.setsToStop.remove(each)

        i = 0
        while i < len(self.commandQueue):
            if self.commandQueue[i].attackingVillage in myCopy:
                del self.commandQueue[i]
            else:
                i += 1


def click(handle, pos):
    lParam = (pos[1] << 16) | pos[0]
    win32gui.PostMessage(handle, WM_LBUTTONDOWN, MK_LBUTTON, lParam )
    time.sleep(0.1)
    win32gui.PostMessage(handle, WM_LBUTTONUP, MK_LBUTTON, lParam )


def find_wold_map_pos(handle):
    bbox = win32gui.GetWindowRect(handle)
    offset = ((abs(abs(bbox[0]) - abs(bbox[2])) - 1040) * 0.5)
    if offset < 0:
        offset = 0
    pos = (int( 130 + offset),
           int(abs(abs(bbox[3]) - abs(bbox[1])) - WORLD_FROM_BOTTOM))
    return pos


def type(handle, text):
    time.sleep(0.3)
    for each in str(text):
        win32gui.PostMessage(handle, WM_CHAR, ord(each), 0)


def find_window():
    w = WindowMgr()
    w.find_window_wildcard(".*Tribal Wars 2.*")
    if w._handle is None:
        print ("Could not find requested window")
        return None
    return w


def send_clear(handle):
    win32gui.PostMessage(handle, WM_KEYDOWN, VK_DELETE, 0)
    win32gui.PostMessage(handle, WM_KEYDOWN, VK_DELETE, 0)
    win32gui.PostMessage(handle, WM_KEYDOWN, VK_DELETE, 0)
    time.sleep(0.1)
    win32gui.PostMessage(handle, WM_KEYUP, VK_DELETE, 0)
    win32gui.PostMessage(handle, WM_KEYUP, VK_DELETE, 0)
    win32gui.PostMessage(handle, WM_KEYUP, VK_DELETE, 0)


def send_tab(handle):
    win32gui.PostMessage(handle, WM_KEYDOWN, VK_TAB, 0)
    time.sleep(0.1)
    win32gui.PostMessage(handle, WM_KEYUP, VK_TAB, 0)


def close_world_map(w):
    click(w, (110, 95))

def next_village(handle):
    wsh = comclt.Dispatch("WScript.Shell")
    wsh.SendKeys("+{RIGHT}")
    time.sleep(2)

def prev_village(handle):
    wsh = comclt.Dispatch("WScript.Shell")
    wsh.SendKeys("+{LEFT}")
    time.sleep(2)


def focus_window(handle):
    pythoncom.CoInitialize()
    if win32gui.GetForegroundWindow() != handle:
        print "Giving focus"
        win32gui.SetForegroundWindow(handle)
