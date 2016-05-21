import random, win32gui, sys, wx, pickle, threading
from win32con import *
from utilities import village, WindowMgr
from main import *

class BotGUI(wx.Frame):

    def __init__(self, parent=None):
        # Initializing parameters and setting up the GUI, not much to see here...
        wx.Frame.__init__(self, parent, -1, 'TribalOT', size=(600, 400))
        self.Bind(wx.EVT_CLOSE, self.onClose)
        self.panel = wx.Panel(self)
        self.reverseSort = False

        self.repeatDelay = -1
        self.maptoattackdelay = 2000
        self.thread = None
        self.closing = False
        self.sets = []
        self.setHomes = []
        self.setTimes = []
        self.villages = []
        try:
            self.load_data()
        except IOError:
            self.sets.append("First Village")
            self.setHomes.append((500, 500))
            self.setTimes.append(-1)
            self.villages.append([village((-1, -1), -1)])

        temp = wx.StaticText(self.panel, -1, "Attacking village: ", pos=(10, 5))
        self.set_list = wx.ListBox(self.panel, 2, pos=wx.Point(10, 25), size=(180, 280),
                                   choices=self.sets, name='Sets')
        self.set_list.SetSelection(0)
        self.thread = myThread(self.villages[0], doneFunc, self, self.maptoattackdelay, self.repeatDelay, timerFunc)

        temp = wx.StaticText(self.panel, -1, "Targets and preset key: ", pos=(210, 5))

        self.vil_list = wx.ListBox(self.panel, 3, pos=wx.Point(210, 25), size=(250, 280),
                                   choices=[str(each) for each in self.villages[0]], name='Villages')
        self.vil_list.SetSelection(0)

        self.set_list.Bind(wx.EVT_LISTBOX, self.onSetListBox, id=2)
        self.vil_list.Bind(wx.EVT_LISTBOX, self.onVilListBox, id=3)
        self.selected_set = 0
        self.selected_vil = 0

        self.addSetButton = wx.Button(self.panel, label="Add Set", pos=(10, 305))
        self.Bind(wx.EVT_BUTTON, self.addSet, self.addSetButton)

        self.remSetButton = wx.Button(self.panel, label="Remove Set", pos=(10, 333))
        self.Bind(wx.EVT_BUTTON, self.remSet, self.remSetButton)

        self.setUpButton = wx.Button(self.panel, label="UP", pos=(110, 325), size=(32, 32))
        self.Bind(wx.EVT_BUTTON,self.setUp, self.setUpButton)

        self.setDownButton = wx.Button(self.panel, label="DOWN", pos=(150, 325), size=(48, 32))
        self.Bind(wx.EVT_BUTTON, self.setDown, self.setDownButton)

        self.newAttackButton = wx.Button(self.panel, label="Create New Attack", pos=(470, 5), size=(110, 25))
        self.Bind(wx.EVT_BUTTON, self.newAttack, self.newAttackButton)

        self.homeCoordText = wx.TextCtrl(self.panel, -1, str(self.setHomes[0][0]), pos=(105, 5), size=(40, 16))
        self.homeCoordText.Bind(wx.EVT_TEXT, self.saveHome)
        self.homeCoordText2 = wx.TextCtrl(self.panel, -1, str(self.setHomes[0][1]), pos=(150, 5), size=(40, 16))
        self.homeCoordText2.Bind(wx.EVT_TEXT, self.saveHome)
        self.coordText = wx.TextCtrl(self.panel, -1, str(self.villages[0][0].pos[0]), pos=(480, 40), size=(40, 16))
        self.coordText.Bind(wx.EVT_TEXT, self.saveAttack)
        self.coordText2 = wx.TextCtrl(self.panel, -1, str(self.villages[0][0].pos[1]), pos=(530, 40), size=(40, 16))
        self.coordText2.Bind(wx.EVT_TEXT, self.saveAttack)
        self.presetText = wx.TextCtrl(self.panel, -1, str(self.villages[0][0].preset), pos=(515, 60), size=(16, 16))
        self.presetText.Bind(wx.EVT_TEXT, self.saveAttack)

        #self.saveAttackButton = wx.Button(self.panel, label="Save", pos=(470,90), size=(110,50))
        #self.Bind(wx.EVT_BUTTON, self.saveAttack, self.saveAttackButton)

        self.sortVillagesButton = wx.Button(self.panel, label="Sort 1to2", pos=(465, 85), size=(60, 30))
        self.Bind(wx.EVT_BUTTON, self.sortVillages, self.sortVillagesButton)

        self.deleteAttackButton = wx.Button(self.panel, label="Delete", pos=(525, 85), size=(50, 30))
        self.Bind(wx.EVT_BUTTON, self.deleteAttack, self.deleteAttackButton)

        self.continueCheckBox = wx.CheckBox(self.panel, -1, label=" Continue from \n selected attack", pos=(470, 170))

        self.runButton = wx.Button(self.panel, label="Run Set", pos=(470, 205), size=(100, 40))
        self.Bind(wx.EVT_BUTTON, self.run, self.runButton)

        self.attackNum = wx.StaticText(self.panel, -1, "Number of attacks: " + str(len(self.villages[0])), pos=(210, 305))
        self.presetNum = wx.StaticText(self.panel, -1, self.makePresetText(), pos=(210, 335))

        #self.timeSlider = wx.Slider(self.panel, -1, value=self.maptoattackdelay, minValue=0, maxValue=5000, style=(wx.SL_HORIZONTAL|wx.SL_LABELS), pos=(480, 145))
        #self.timeSlider.Bind(wx.EVT_SLIDER, self.timeSliderScroll)
        self.timeMTA = wx.TextCtrl(self.panel, -1, str(self.maptoattackdelay), pos=(475, 145), size=(60, 16))
        self.timeMTA.Bind(wx.EVT_TEXT, self.timeMTAChange)

        self.timeMTAText = wx.StaticText(self.panel, -1, "MapToAttack Delay: ", pos=(470, 120))
        self.timeMTAText = wx.StaticText(self.panel, -1, "msec", pos=(540, 145))

        self.timeRepeat = wx.TextCtrl(self.panel, -1, str(self.setTimes[0]), pos=(475, 275), size=(60, 16))
        self.timeRepeat.Bind(wx.EVT_TEXT, self.timeRepeatChange)

        self.timeRepeatText = wx.StaticText(self.panel, -1, "Repeat attacks every: ", pos=(470, 250))
        self.timeRepeatText = wx.StaticText(self.panel, -1, "mins", pos=(540, 275))

        self.timeLeft = wx.StaticText(self.panel, -1, "00:00", pos=(500, 310))
        font = wx.Font(18, wx.DEFAULT, wx.NORMAL, wx.BOLD)
        self.timeLeft.SetFont(font)

    def sortVillages(self, e):
        # Get the selected set.
        selected_set = self.set_list.GetSelection()
        # Get the attacking village of the selected set.
        home = self.setHomes[selected_set]

        # A function that compares two village objects based on what we want.
        def compare(vil1, vil2):
            dis1 = vil1.distance(home)
            dis2 = vil2.distance(home)
            if dis1>dis2:
                return 1
            elif dis1==dis2:
                return 0
            return -1

        # Get all the attack coordinates and preset keys for the selected set.
        self.villages[selected_set] = sorted(self.villages[selected_set], cmp=compare)
        # Sort ascending or descending.
        if self.reverseSort:
            self.villages[selected_set] = list(reversed(self.villages[selected_set]))
            self.reverseSort = False
            self.sortVillagesButton.SetLabelText("Sort 1to2")
        else:
            self.reverseSort = True
            self.sortVillagesButton.SetLabelText("Sort 2to1")

        # Refresh the GUI.
        self.onSetListBox(None)
        self.set_list.SetSelection(selected_set)
        self.vil_list.SetSelection(len(self.villages[selected_set]) - 1)
        self.resetTexts()

    def timeRepeatChange(self, e):
        # Keep track of the "Repeat attacks every:" value.
        selected_set = self.set_list.GetSelection()
        try:
            self.setTimes[selected_set] = int(self.timeRepeat.GetValue())
            self.repeatDelay = int(self.timeRepeat.GetValue())
        except:
            self.setTimes[selected_set] = -1
            self.repeatDelay = -1
            self.timeRepeat.SetValue("-1")

    def timeMTAChange(self, e):
        # Keep track of the "MapToAttack Delay" value.
        try:
            self.maptoattackdelay = int(self.timeMTA.GetValue())
        except:
            self.maptoattackdelay = 1500
            self.timeMTA.SetValue("1500")

    def saveHome(self, e):
        # Save the coordinates of the attacking village if they are changed.
        selected_set = self.set_list.GetSelection()
        try:
            pos = (str(int(self.homeCoordText.GetValue())), str(int(self.homeCoordText2.GetValue())))
        except ValueError:
            pos = ("500", "500")
        self.setHomes[selected_set] = pos

    def run(self, e):
        # If you are already running
        if threading.activeCount() > 1:
            self.thread.stop()
            self.runButton.SetLabelText("Stopping Set")

        # If you are not already running
        else:
            # Find which set the user wants to you to run
            selected_set = self.set_list.GetSelection()
            selected_vil = self.vil_list.GetSelection()

            # If the user wants to continue from the selected attack, remove the previous attacks from the list.
            if self.continueCheckBox.Get3StateValue():
                self.thread = myThread(list(self.villages[selected_set][selected_vil:]), doneFunc, self, self.maptoattackdelay, -1, timerFunc)
            # Else run the whole set with all the attacks.
            else:
                self.thread = myThread(list(self.villages[selected_set]), doneFunc, self, self.maptoattackdelay, self.repeatDelay, timerFunc)
            self.thread.start()

            self.runButton.SetLabelText("Stop Set")

    def deleteAttack(self, e):
        # Get which set and which attack are selected
        selected_set = self.set_list.GetSelection()
        selected_vil = self.vil_list.GetSelection()

        # If this is the last attack in that set, create a new empty attack before deleting this one
        if len(self.villages[selected_set]) == 1:
            self.newAttack(None)

        # Delete the selected attack
        del self.villages[selected_set][selected_vil]

        # Refresh the GUI.
        self.onSetListBox(None)
        self.set_list.SetSelection(selected_set)
        new_selection = min(selected_vil, len(self.villages[selected_set])-1)
        self.vil_list.SetSelection(new_selection)
        self.resetTexts()

    def newAttack(self, e):
        # Get the selected set.
        selected_set = self.set_list.GetSelection()
        # Add an empty attack in that set.
        self.villages[selected_set].append(village((-1, -1), -1))
        # Refresh the GUI.
        self.onSetListBox(None)
        self.set_list.SetSelection(selected_set)
        self.vil_list.SetSelection(len(self.villages[selected_set])-1)
        self.resetTexts()

    def saveAttack(self, e):
        ''' This runs when the coordinates or the preset for an attack are changed. '''
        # Get which set and which attack in that set are selected.
        selected_set = self.set_list.GetSelection()
        selected_vil = self.vil_list.GetSelection()

        # If any of the coordinates are changed, see if they are valid numbers and try to save them.
        try:
            pos = (str(abs(int(self.coordText.GetValue()))), str(abs(int(self.coordText2.GetValue()))))
        except ValueError:
            pos = ("-1", "-1")
        # Same for presets.
        try:
            preset = str(abs(int(self.presetText.GetValue())))
        except ValueError:
            preset = "-1"

        # Save the new values.
        self.villages[selected_set][selected_vil].pos = pos
        self.villages[selected_set][selected_vil].preset = preset

        # Refresh the GUI.
        self.onSetListBox(None, False)
        self.set_list.SetSelection(selected_set)
        self.vil_list.SetSelection(selected_vil)
        #self.resetTexts()

    def setUp(self, e):
        ''' Moves a set up on the list.'''
        # Get the selected set.
        index = self.set_list.GetSelection()
        # If the selected set is already on top, do nothing.
        if index < 1:
            return
        # Else, change places with the set above it.
        temp = self.villages[index]
        self.villages[index] = self.villages[index-1]
        self.villages[index-1] = temp

        temp = self.sets[index]
        self.sets[index] = self.sets[index-1]
        self.sets[index-1] = temp

        temp = self.setHomes[index]
        self.setHomes[index] = self.setHomes[index-1]
        self.setHomes[index-1] = temp

        temp = self.setTimes[index]
        self.setTimes[index] = self.setTimes[index-1]
        self.setTimes[index-1] = temp

        # Refresh the GUI.
        self.resetSetListBox()
        self.set_list.SetSelection(index-1)

    def setDown(self,e ):
        ''' Moves a set down on the list.'''
        # Get the selected set.
        index = self.set_list.GetSelection()
        # If the selected set is last, do nothing.
        if index >= len(self.sets)-1:
            return
        # Else, change places with the set below it.
        temp = self.villages[index]
        self.villages[index] = self.villages[index+1]
        self.villages[index+1] = temp

        temp = self.sets[index]
        self.sets[index] = self.sets[index+1]
        self.sets[index+1] = temp

        temp = self.setHomes[index]
        self.setHomes[index] = self.setHomes[index+1]
        self.setHomes[index+1] = temp

        temp = self.setTimes[index]
        self.setTimes[index] = self.setTimes[index+1]
        self.setTimes[index+1] = temp

        # Refresh the GUI.
        self.resetSetListBox()
        self.set_list.SetSelection(index+1)

    def addSet(self, e):
        ''' Adds a new set. '''
        # Request a new set name from the user.
        name = "Set_name"
        box = wx.TextEntryDialog(None, "New Attack Set Name:", "Choose attack set name", "Attack Set Name")
        if box.ShowModal() == wx.ID_OK:
            name = box.GetValue()
        else:
            # If the user presses cancel, don't add anything.
            return

        # Add the set to the list of sets and initialize its values.
        self.sets.append(name)
        self.setHomes.append(('500', '500'))
        self.setTimes.append(-1)
        self.villages.append([])

        # Refresh the GUI.
        self.resetSetListBox()
        self.set_list.SetSelection(len(self.sets)-1)
        self.onSetListBox(None)

    def remSet(self, e):
        ''' Deletes the selected set.'''
        # Ask the user if they are sure.
        dlg = wx.MessageDialog(self,
            "Do you really want to delete this set?",
            "Confirm Deletion", wx.OK|wx.CANCEL|wx.ICON_QUESTION)
        result = dlg.ShowModal()
        dlg.Destroy()
        if result == wx.ID_OK:
            # If they are, find the selected set.
            selected_set = self.set_list.GetSelection()

            # If this is the last set, don't delete it.
            if len(self.villages) <= 1:
                return

            # Delete the set along with all its attacks and the attacking village coordinates.
            del self.villages[selected_set]
            del self.sets[selected_set]
            del self.setHomes[selected_set]
            del self.setTimes[selected_set]

            # Refresh the GUI.
            self.resetSetListBox()
            self.set_list.SetSelection(0)
            self.onSetListBox(None)

    def resetSetListBox(self):
        ''' Refreshes the set list GUI. '''
        self.set_list.Destroy()
        self.set_list = wx.ListBox(self.panel, 2, pos=wx.Point(10, 25), size=(180, 280),
                                   choices=self.sets, name='Sets')
        self.set_list.Bind(wx.EVT_LISTBOX, self.onSetListBox, id=2)
        self.set_list.SetSelection(len(self.villages) - 1)

    def onSetListBox(self, e, resetTexts=True):
        ''' Refreshes the list of attacks of a set GUI.'''
        self.vil_list.Destroy()
        selected_set = self.set_list.GetSelection()

        self.homeCoordText.Destroy()
        self.homeCoordText2.Destroy()
        self.homeCoordText = wx.TextCtrl(self.panel, -1, str(self.setHomes[selected_set][0]), pos=(105, 5), size=(40, 16))
        self.homeCoordText.Bind(wx.EVT_TEXT, self.saveHome)
        self.homeCoordText2 = wx.TextCtrl(self.panel, -1, str(self.setHomes[selected_set][1]), pos=(150, 5), size=(40, 16))
        self.homeCoordText2.Bind(wx.EVT_TEXT, self.saveHome)

        self.vil_list = wx.ListBox(self.panel, 3, pos=wx.Point(210, 25), size=(250, 280),
                                   choices=[str(each) for each in self.villages[selected_set]], name='Villages')
        self.vil_list.Bind(wx.EVT_LISTBOX, self.onVilListBox, id=3)
        self.timeRepeat.SetValue(str(self.setTimes[selected_set]))
        if (len(self.villages[selected_set])<1):
            self.newAttack(None)
        self.vil_list.SetSelection(0)
        if resetTexts:
            self.resetTexts()

    def onVilListBox(self, e):
        self.resetTexts()

    def resetTexts(self):
        ''' Resets all the text on screen that needs to be refreshed. '''
        selected_vil = self.vil_list.GetSelection()
        set = self.set_list.GetSelection()

        self.coordText.Destroy()
        self.coordText2.Destroy()
        self.presetText.Destroy()
        self.attackNum.Destroy()
        self.presetNum.Destroy()

        self.coordText = wx.TextCtrl(self.panel, -1, str(self.villages[set][selected_vil].pos[0]), pos=(480, 40), size=(40, 16))
        self.coordText2 = wx.TextCtrl(self.panel, -1, str(self.villages[set][selected_vil].pos[1]), pos=(530, 40), size=(40, 16))
        self.presetText = wx.TextCtrl(self.panel, -1, str(self.villages[set][selected_vil].preset), pos=(515, 60), size=(16, 16))
        self.coordText.Bind(wx.EVT_TEXT, self.saveAttack)
        self.coordText2.Bind(wx.EVT_TEXT, self.saveAttack)
        self.presetText.Bind(wx.EVT_TEXT, self.saveAttack)
        self.attackNum = wx.StaticText(self.panel, -1, "Number of attacks: " + str(len(self.villages[set])), pos=(210, 305))
        self.presetNum = wx.StaticText(self.panel, -1, self.makePresetText(), pos=(210, 335))

    def makePresetText(self):
        ''' Calculates how many of each preset a set has and makes it into a single string variable. '''
        set = self.set_list.GetSelection()
        text = "Presets Used:"
        for each in ['-1', '1', '2', '3', '4', '5', '6', '7', '8', '9']:
            num = 0
            for vil in self.villages[set]:
                if str(vil.preset) == each:
                    num += 1
            if num>0:
                text += " " + each + "->" + str(num) + " | "
        return text

    def onClose(self, e):
        ''' Runs when the user tries to close the program. '''
        dlg = wx.MessageDialog(self,
            "Do you really want to close?",
            "Confirm Exit?", wx.OK|wx.CANCEL|wx.ICON_QUESTION)
        result = dlg.ShowModal()
        dlg.Destroy()
        if result == wx.ID_OK:
            self.save_data()
            self.closing = True
            self.thread.stop()
            while threading.activeCount() > 1:
                time.sleep(0.5)
            self.Destroy()
            sys.exit(0)

    def save_data(self):
        with open('data.pkl', 'wb') as output:
            data = []
            for i in range(len(self.sets)):
                data.append((self.sets[i], self.setHomes[i],  self.villages[i], self.setTimes[i]))
            pickle.dump(data, output)

    def load_data(self):
        with open('data.pkl', 'rb') as input:
            data = pickle.load(input)
            input.close()
        for each in data:
            self.sets.append(each[0])
            self.setHomes.append(each[1])
            self.villages.append(each[2])
            try:
                self.setTimes.append(each[3])
            except IndexError:
                self.setTimes.append(-1)
        return

def doneFunc(orig, each):
    if orig.closing:
        return
    try:
        orig.runButton.SetLabelText("Run Set")
        orig.vil_list.SetSelection(each)
        orig.timeLeft.SetLabelText("00:00")
    except:
        return
    return

def timerFunc(orig, time):
    if time < 0:
        return
    minutes = str(int(time)/60)
    if len(minutes)==1:
        minutes = "0" + minutes
    seconds = str(int(time)%60)
    if len(seconds) == 1:
        seconds = "0" + seconds
    orig.timeLeft.SetLabelText(minutes + ":" + seconds)
    return

def timerFuncPlus(orig, activeSets):
    selected_set = orig.set_list.GetSelection()
    for set in activeSets:
        if selected_set == set[0]:
            time = set[2] - set[3]
            if time < 0:
                return
            minutes = str(int(time) / 60)
            if len(minutes) == 1:
                minutes = "0" + minutes
            seconds = str(int(time) % 60)
            if len(seconds) == 1:
                seconds = "0" + seconds
            orig.timeLeft.SetLabelText(minutes + ":" + seconds)
            return
        orig.timeLeft.SetLabelText("00:00")
    return

if __name__ == '__main__':
    app = wx.App()
    top = BotGUI()
    top.Show()
    app.MainLoop()