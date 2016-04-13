import os, time, random, win32gui, sys, wx, pickle
from win32con import *
from utilities import village, WindowMgr

class BotGUI(wx.Frame):

    def __init__(self, parent=None):
        wx.Frame.__init__(self, parent, -1, 'TribalOT', size=(600, 400))
        self.Bind(wx.EVT_CLOSE, self.onClose)
        self.panel = wx.Panel(self)

        self.sets = []
        self.villages = []
        try:
            self.load_data()
        except IOError:
            self.sets.append("Default")
            self.villages.append([village((-1, -1), -1)])

        self.set_list = wx.ListBox(self.panel, 2, pos=wx.Point(10, 5), size=(180, 300),
                                   choices=self.sets, name='Sets')
        self.set_list.SetSelection(0)


        self.vil_list = wx.ListBox(self.panel, 3, pos=wx.Point(210, 5), size=(250, 300),
                                   choices=[str(each) for each in self.villages[0]], name='Villages')
        self.vil_list.SetSelection(0)

        self.set_list.Bind(wx.EVT_LISTBOX, self.onSetListBox, id=2)
        self.vil_list.Bind(wx.EVT_LISTBOX, self.onVilListBox, id=3)
        self.selected_set = 0
        self.selected_vil = 0

        self.addSetButton = wx.Button(self.panel, label="Add Set", pos=(10, 325))
        self.Bind(wx.EVT_BUTTON, self.addSet, self.addSetButton)

        self.setUpButton = wx.Button(self.panel, label="UP", pos=(110, 325), size=(32,32))
        self.Bind(wx.EVT_BUTTON,self.setUp, self.setUpButton)

        self.setDownButton = wx.Button(self.panel, label="DOWN", pos=(150, 325), size=(48,32))
        self.Bind(wx.EVT_BUTTON, self.setDown, self.setDownButton)

        self.newAttackButton = wx.Button(self.panel, label="Create New Attack", pos=(470, 5), size=(110, 25))
        self.Bind(wx.EVT_BUTTON, self.newAttack, self.newAttackButton)

        self.coordText = wx.TextCtrl(self.panel, -1, str(self.villages[0][0].pos[0]), pos=(480, 40), size=(40, 16))
        self.coordText2 = wx.TextCtrl(self.panel, -1, str(self.villages[0][0].pos[1]), pos=(530, 40), size=(40, 16))
        self.presetText = wx.TextCtrl(self.panel, -1, str(self.villages[0][0].preset), pos=(515, 60), size=(16, 16))

        self.saveAttackButton = wx.Button(self.panel, label="Save", pos=(470,90), size=(110,50))
        self.Bind(wx.EVT_BUTTON, self.saveAttack, self.saveAttackButton)

        self.deleteAttackButton = wx.Button(self.panel, label="Delete", pos=(470,150), size=(110,50))
        self.Bind(wx.EVT_BUTTON, self.deleteAttack, self.deleteAttackButton)

    def deleteAttack(self, e):
        self.selected_set = self.set_list.GetSelection()
        selected_set = self.selected_set
        self.selected_vil = self.vil_list.GetSelection()
        selected_vil = self.selected_vil

        if len(self.villages[selected_set]) == 1:
            self.newAttack(None)

        del self.villages[selected_set][selected_vil]

        self.onSetListBox(None)
        self.set_list.SetSelection(selected_set)
        self.onVilListBox(None)
        new_selection = min(selected_vil, len(self.villages[selected_set])-1)

        self.vil_list.SetSelection(new_selection)
        self.resetTexts()


    def newAttack(self, e):
        self.selected_set = self.set_list.GetSelection()
        self.villages[self.selected_set].append(village((-1, -1), -1))
        self.onSetListBox(None)
        self.set_list.SetSelection(self.selected_set)
        self.onVilListBox(None)
        self.vil_list.SetSelection(len(self.villages[self.selected_set])-1)

    def saveAttack(self, e):
        self.selected_set = self.set_list.GetSelection()
        selected_set = self.selected_set
        self.selected_vil = self.vil_list.GetSelection()
        selected_vil = self.selected_vil

        pos = (int(self.coordText.GetValue()), int(self.coordText2.GetValue()))
        preset = int(self.presetText.GetValue())
        self.villages[self.selected_set][self.selected_vil].pos = pos
        self.villages[self.selected_set][self.selected_vil].preset = preset

        self.onSetListBox(None)
        self.set_list.SetSelection(selected_set)
        self.onVilListBox(None)
        self.vil_list.SetSelection(selected_vil)
        self.resetTexts()

    def setUp(self, e):
        index = self.set_list.GetSelection()
        if index < 1:
            return

        temp = self.villages[index]
        self.villages[index] = self.villages[index-1]
        self.villages[index-1] = temp

        temp = self.sets[index]
        self.sets[index] = self.sets[index-1]
        self.sets[index-1] = temp

        self.set_list.Destroy()
        self.set_list = wx.ListBox(self.panel, 2, pos=wx.Point(10, 5), size=(180, 300),
                                   choices=self.sets, name='Sets')
        self.set_list.SetSelection(index-1)
        self.set_list.Bind(wx.EVT_LISTBOX, self.onSetListBox, id=2)

    def setDown(self,e ):
        index = self.set_list.GetSelection()
        if index >= len(self.sets)-1:
            return

        temp = self.villages[index]
        self.villages[index] = self.villages[index+1]
        self.villages[index+1] = temp

        temp = self.sets[index]
        self.sets[index] = self.sets[index+1]
        self.sets[index+1] = temp

        self.set_list.Destroy()
        self.set_list = wx.ListBox(self.panel, 2, pos=wx.Point(10, 5), size=(180, 300),
                                   choices=self.sets, name='Sets')
        self.set_list.SetSelection(index+1)
        self.set_list.Bind(wx.EVT_LISTBOX, self.onSetListBox, id=2)

    def addSet(self, e):
        name = "Default Name"
        box = wx.TextEntryDialog(None, "New Set Name:", "Choose set name", "Set Name")
        if box.ShowModal() == wx.ID_OK:
            name = box.GetValue()
        else:
            return
        self.sets.append(name)
        self.villages.append([])
        self.set_list.Destroy()
        self.set_list = wx.ListBox(self.panel, 2, pos=wx.Point(10, 5), size=(180, 300),
                                   choices=self.sets, name='Sets')
        self.set_list.Bind(wx.EVT_LISTBOX, self.onSetListBox, id=2)

    def onSetListBox(self, e):
        self.vil_list.Destroy()
        self.selected_set = self.set_list.GetSelection()
        self.vil_list = wx.ListBox(self.panel, 3, pos=wx.Point(210, 5), size=(250, 300),
                                   choices=[str(each) for each in self.villages[self.selected_set]], name='Villages')
        self.vil_list.Bind(wx.EVT_LISTBOX, self.onVilListBox, id=3)
        self.selected_vil = 0

    def onVilListBox(self, e):
        self.selected_vil = self.vil_list.GetSelection()
        self.resetTexts()

    def resetTexts(self):
        self.coordText.Destroy()
        self.coordText2.Destroy()
        self.presetText.Destroy()
        self.selected_vil = self.vil_list.GetSelection()
        set = self.set_list.GetSelection()
        self.coordText = wx.TextCtrl(self.panel, -1, str(self.villages[set][self.selected_vil].pos[0]), pos=(480, 40), size=(40, 16))
        self.coordText2 = wx.TextCtrl(self.panel, -1, str(self.villages[set][self.selected_vil].pos[1]), pos=(530, 40), size=(40, 16))
        self.presetText = wx.TextCtrl(self.panel, -1, str(self.villages[set][self.selected_vil].preset), pos=(515, 60), size=(16, 16))

    def onClose(self, e):
        dlg = wx.MessageDialog(self,
            "Do you really want to close?",
            "Confirm Exit", wx.OK|wx.CANCEL|wx.ICON_QUESTION)
        result = dlg.ShowModal()
        dlg.Destroy()
        if result == wx.ID_OK:
            self.save_data()
            self.Destroy()
            sys.exit(0)

    def save_data(self):
        with open('data.pkl', 'wb') as output:
            data = []
            for i in range(len(self.sets)):
                data.append((self.sets[i], self.villages[i]))
            pickle.dump(data, output)

    def load_data(self):
        with open('data.pkl', 'rb') as input:
            data = pickle.load(input)
            input.close()
        for each in data:
            self.sets.append(each[0])
            self.villages.append(each[1])
        return

if __name__ == '__main__':
    app = wx.App()
    top = BotGUI()
    top.Show()
    app.MainLoop()