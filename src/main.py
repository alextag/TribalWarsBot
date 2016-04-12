import os, time, random, win32gui, re, sys
from win32con import *
from PIL import ImageGrab

WORLD_FROM_BOTTOM = 55
XCOORD_FROM_BOTTOM = 185

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

def click( handle, pos ):
    lParam = (pos[1] << 16) | pos[0]
    win32gui.PostMessage(handle, WM_LBUTTONDOWN, MK_LBUTTON, lParam )
    time.sleep(0.1)
    win32gui.PostMessage(handle, WM_LBUTTONUP, MK_LBUTTON, lParam )

def Rclick( handle, pos ):
    lParam = (pos[1] << 16) | pos[0]
    win32gui.PostMessage(handle, WM_RBUTTONDOWN, MK_RBUTTON, lParam )
    time.sleep(0.1)
    win32gui.PostMessage(handle, WM_RBUTTONUP, MK_RBUTTON, lParam )

def find_wold_map_pos( handle ):
    bbox = win32gui.GetWindowRect(handle)
    offset = ((abs(abs(bbox[0]) - abs(bbox[2])) - 1040) * 0.5)
    if offset < 0:
        offset = 0
    pos = (int( 130 + offset),
           int(abs(abs(bbox[3]) - abs(bbox[1])) - WORLD_FROM_BOTTOM))
    return pos

def type( handle, text ):
    time.sleep(0.3)
    for each in text:
        win32gui.PostMessage(w._handle, WM_CHAR, ord(each), 0)
        time.sleep(0.2)

def find_window():
    w = WindowMgr()
    w.find_window_wildcard(".*Tribal Wars 2.*")
    if w._handle is None:
        print ("Could not find requested window")
        sys.exit(-1)
    return w

w = find_window()
pos = find_wold_map_pos(w)
click(w, pos)
click(w, (pos[0], pos[1] - (XCOORD_FROM_BOTTOM - WORLD_FROM_BOTTOM)))
type(w, "468")
