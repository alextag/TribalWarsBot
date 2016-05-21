import win32gui, re, time, threading

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

    def __init__(self, attacker, villages, startindex=0):
        self.villages = villages
        self.attackingVillage = attacker
        self.startindex = startindex

class timerThread (threading.Thread):

    def __init__(self, activeSets, commandQueue, timerFunc, orig):
        threading.Thread.__init__(self)
        self.activeSets = activeSets
        self.commandQueue = commandQueue
        self._stop = threading.Event()
        self.timerFunc = timerFunc
        self.orig = orig

    def run(self):
        while not self._stop.isSet():
            for com in self.activeSets:
                com[3] += TIME_UNIT
                if com[3] >= com[2]:
                    com[3] = 0
                    self.commandQueue.append(Command(com[0], com[1]))
                    print "Command Sent"
            self.timerFunc(self.orig, self.activeSets)
            time.sleep(TIME_UNIT)

    def stop(self):
        self._stop.set()

class attackerThread (threading.Thread):

    def __init__(self, commandQueue):
        threading.Thread.__init__(self)
        self.commandQueue = commandQueue
        self._stop = threading.Event()

    def run(self):
        while not self._stop.isSet():
            if len(self.commandQueue)>0:
                myCopy = self.commandQueue[0]
                #DOSTUFF
                print myCopy
                del self.commandQueue[0]
            time.sleep(TIME_UNIT)

    def stop(self):
        self._stop.set()
