import os, time, random, win32gui, sys, wx
from win32con import *
from utilities import village, WindowMgr

class BotGUI(wx.Frame):

    def __init__(self, parent=None):
        wx.Frame.__init__(self, parent, -1, 'TribalOT', size=(600, 400))
        self.Bind(wx.EVT_CLOSE, self.onClose)
        self.panel = wx.Panel(self)

        self.sets = ['Default']
        self.set_list = wx.ListBox(self.panel, 2, pos=wx.Point(10, 5), size=(180, 300),
                                   choices=self.sets, name='Sets')

        self.villages = [[village(('454', '409'), '9'),  village(('454', '412'), '9')]]
        self.vil_list = wx.ListBox(self.panel, 3, pos=wx.Point(210, 5), size=(250, 300),
                                   choices=[str(each) for each in self.villages[0]], name='Villages')

        self.set_list.Bind(wx.EVT_LISTBOX, self.onSetListBox, id=2)
        self.vil_list.Bind(wx.EVT_LISTBOX, self.onVilListBox, id=3)
        self.selected_set = 0
        self.selected_vil = 0

        self.addSetButton = wx.Button(self.panel, label="Add Set", pos=(10, 325))
        self.Bind(wx.EVT_BUTTON, self.addSet, self.addSetButton)

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

    def onClose(self, e):
        dlg = wx.MessageDialog(self,
            "Do you really want to close?",
            "Confirm Exit", wx.OK|wx.CANCEL|wx.ICON_QUESTION)
        result = dlg.ShowModal()
        dlg.Destroy()
        if result == wx.ID_OK:
            self.Destroy()
            sys.exit(0)

if __name__ == '__main__':
    app = wx.App()
    top = BotGUI()
    top.Show()
    app.MainLoop()