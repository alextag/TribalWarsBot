import os, time, random, win32gui, sys, threading
from win32con import *
from utilities import village, WindowMgr

WORLD_FROM_BOTTOM = 55
XCOORD_FROM_BOTTOM = 175
MOVE_FROM_COORD = 200
TIME_UNIT = 1.0


class myThread (threading.Thread):

    def __init__(self, attacks, doneFunc, orig, delay, repeatDelay, repeatFunc):
        threading.Thread.__init__(self)
        self.attacks = attacks
        self._stop = threading.Event()
        self.doneFunc = doneFunc
        self.orig = orig
        self.delay = delay
        self.repeatDelay = repeatDelay
        self.repeatFunc = repeatFunc

    def stop(self):
        self._stop.set()

    def run(self):
        repeat = self.repeatDelay * 60
        timepassed = abs(repeat)
        count = 0
        denail = 0
        while not self._stop.isSet():
            if timepassed*TIME_UNIT > repeat + denail:
                timepassed = 0
                attacks = self.attacks
                w = find_window()
                if w is None:
                    self.doneFunc(self.orig, 0)
                    return
                pos = find_wold_map_pos(w)
                close_world_map(w)
                click(w, pos)
                count = 0
                for each in attacks:
                    if self._stop.isSet():
                        self.doneFunc(self.orig, count)
                        return
                    if int(each.preset) == -1 or int(each.pos[0]) == -1 or int(each.pos[1]) == -1:
                        continue
                    done = self.attack(w, each)
                    if done:
                        count += 1
                    time.sleep(random.random())
                if count >= len(attacks):
                    count = 0
                if repeat < 0:
                    break
                denail = random.random()*0.1*repeat
            else:
                timepassed += 1
                time.sleep(TIME_UNIT)
                self.repeatFunc(self.orig, (repeat+denail) - timepassed*TIME_UNIT)
        self.doneFunc(self.orig, count)
        return

    def attack(self, w, vil):
        pos = find_wold_map_pos(w)
        click(w, (pos[0]-80, pos[1] - (XCOORD_FROM_BOTTOM - WORLD_FROM_BOTTOM)))
        time.sleep(0.1)
        if self._stop.isSet():
            return False
        #clickDragLeft(w, (pos[0], pos[1] - (XCOORD_FROM_BOTTOM - WORLD_FROM_BOTTOM)))
        send_clear(w) # CTR-A + backspace or delete
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
        time.sleep((self.delay/1000.0) + 1.5*random.random())
        if self._stop.isSet():
            return False
        type(w, vil.preset)
        return True


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
