import win32gui, re

class village():

    def __init__(self, pos, preset):
        self.pos = (str(pos[0]),str(pos[1]))
        self.preset = str(preset)

    #def distance(self, other):
    #    xs = np.power((self.pos[0]-other.pos[0]), 2)
    #    ys = np.power((self.pos[1]-other.pos[1]), 2)
    #    return np.sqrt(xs + (0.75*ys))

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
