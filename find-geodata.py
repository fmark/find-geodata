#!/usr/bin/env python

import os
import subprocess
import sys
import wx

from threading import Thread
from wx.lib.pubsub import setuparg1 # Needed for py2exe
from wx.lib.pubsub import pub as Publisher
                
import geofind

def shell_open_file(path):
    if sys.platform == 'win32':
        os.startfile(path)
    elif sys.platform == 'darwin':
        subprocess.call(('open', path))
    elif sys.platform == 'linux2':
        subprocess.call(('xdg-open', path))


class FinderThread(Thread):
    """Finder Worker Thread Class."""
 
    #----------------------------------------------------------------------
    def __init__(self, search_path):
        """Finder Worker Thread Class."""
        Thread.__init__(self)
        self.search_path = search_path
        self.start()    # start the thread
 
    #----------------------------------------------------------------------
    def run(self):
        """Run Worker Thread."""
        # This is the code executing in the new thread.
        finder = geofind.finder(self.search_path)
        items = finder.search()
        wx.CallAfter(Publisher.sendMessage, "searchdone", items)
 

class FindGeodata(wx.Frame):
    def __init__(self, parent, id, title):
        wx.Frame.__init__(self, parent, id, title, size=(600, 350))
        panel = wx.Panel(self, -1)

        font = wx.SystemSettings_GetFont(wx.SYS_DEFAULT_GUI_FONT)
        font.SetPointSize(9)

        vbox = wx.BoxSizer(wx.VERTICAL)

        hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        st1 = wx.StaticText(panel, -1, 'Select the directory to search for geodata files in:')
        st1.SetFont(font)
        hbox1.Add(st1, 0, wx.RIGHT, 8)
        vbox.Add(hbox1, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 10)

        vbox.Add((-1, 10))

        hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        self.root_dir_tc = wx.TextCtrl(panel, -1, size=(240, 30))
        self.root_dir_tc.SetValue(os.path.expanduser('~'))
        hbox2.Add(self.root_dir_tc, 1)
        hbox2.Add((10, 0))
        browse_btn = wx.Button(panel, -1, 'Browse...', size=(70, 30))
        browse_btn.Bind(wx.EVT_BUTTON,  self.OnBrowseClick, id=browse_btn.GetId())
        hbox2.Add(browse_btn, 0)
        hbox2.Add((10, 0))
        self.search_btn = wx.Button(panel, -1, 'Search...', size=(70, 30))
        self.search_btn.Bind(wx.EVT_BUTTON,  self.OnSearchClick, id=self.search_btn.GetId())
        hbox2.Add(self.search_btn, 0)
        hbox2.Add((10, 0))
        self.status_text = wx.StaticText(panel, -1, '')
        font2 = wx.SystemSettings_GetFont(wx.SYS_DEFAULT_GUI_FONT)
        font2.SetPointSize(9)
        font2.SetStyle(wx.FONTSTYLE_ITALIC)
        self.status_text.SetFont(font2)
        hbox2.Add(self.status_text, 0, wx.RIGHT, 8)
        vbox.Add(hbox2, 0, wx.LEFT | wx.TOP, 10)

        vbox.Add((-1, 10))

        hbox3 = wx.BoxSizer(wx.HORIZONTAL)
        st2 = wx.StaticText(panel, -1, 'Tick the candidate items you want to include in your list:')
        st2.SetFont(font)
        hbox3.Add(st2, 0, wx.RIGHT, 8)
        vbox.Add(hbox3, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 10)

        vbox.Add((-1, 10))

        hbox4 = wx.BoxSizer(wx.HORIZONTAL)
        self.geodata_listbox = wx.CheckListBox(panel, -1)
        hbox4.Add(self.geodata_listbox, 1, wx.EXPAND)
        vbox.Add(hbox4, 1, wx.LEFT | wx.RIGHT | wx.EXPAND, 10)

        vbox.Add((-1, 25))

        # hbox5 = wx.BoxSizer(wx.HORIZONTAL)
        # cb1 = wx.CheckBox(panel, -1, 'Case Sensitive')
        # cb1.SetFont(font)
        # hbox5.Add(cb1)
        # cb2 = wx.CheckBox(panel, -1, 'Nested Classes')
        # cb2.SetFont(font)
        # hbox5.Add(cb2, 0, wx.LEFT, 10)
        # cb3 = wx.CheckBox(panel, -1, 'Non-Project classes')
        # cb3.SetFont(font)
        # hbox5.Add(cb3, 0, wx.LEFT, 10)
        # vbox.Add(hbox5, 0, wx.LEFT, 10)

        # vbox.Add((-1, 25))

        hbox6 = wx.BoxSizer(wx.HORIZONTAL)
        btn1 = wx.Button(panel, -1, 'Create List...', size=(90, 30))
        btn1.Bind(wx.EVT_BUTTON,  self.OnCreateListClick, id=btn1.GetId())
        hbox6.Add(btn1, 0)
        btn2 = wx.Button(panel, -1, 'Quit', size=(70, 30))
        btn2.Bind(wx.EVT_BUTTON,  self.OnQuitClick, id=btn2.GetId())
        hbox6.Add(btn2, 0, wx.LEFT | wx.BOTTOM , 5)
        vbox.Add(hbox6, 0, wx.ALIGN_RIGHT | wx.RIGHT, 10)

        Publisher.subscribe(self.searchDone, "searchdone")

        panel.SetSizer(vbox)
        self.Centre()
        self.Show(True)

    def OnQuitClick(self, event):
        self.Close(True)

    def OnCreateListClick(self, event):
        # if at least one item is checked
        save_items = self.geodata_listbox.GetCheckedStrings()
        if len(save_items) > 0:
            dialog = wx.FileDialog ( None, 
                                     message = "Save list",
                                     defaultFile="geodata_list.rtf",
                                     wildcard = "Rich text documents (*.rtf)|*.rtf|" \
                                         "All files (*.*)|*.*",
                                     style = wx.SAVE | wx.OVERWRITE_PROMPT )
            if dialog.ShowModal() == wx.ID_OK:
                saver = geofind.saver(save_items)
                saver.save(dialog.GetPath())
                dial = wx.MessageDialog(None, 'List saved successfully. Would you like to edit it now?',
                                        'Edit list', wx.OK | wx.CANCEL | wx.ICON_QUESTION)
                if dial.ShowModal() ==  wx.ID_OK:
                    shell_open_file(dialog.GetPath())
                dial.Destroy()
            dialog.Destroy()
        else:
            self.UserError("You must select at least one item to create a list.")
    
    def OnBrowseClick(self, event):
        dialog = wx.DirDialog(None, "Please choose the directory to search in:",
                              style=1 ,defaultPath=self.root_dir_tc.GetValue(), pos = (10,10))
        if dialog.ShowModal() == wx.ID_OK:
            self.root_dir_tc.SetValue(dialog.GetPath())

    def UserError(self, msg):
        dial = wx.MessageDialog(None, msg, 'Error', wx.OK | 
                                wx.ICON_ERROR)
        dial.ShowModal()
        dial.Destroy()


    def OnSearchClick(self, event):
        if os.path.isdir(self.root_dir_tc.GetValue()):
            self.search_btn.Disable()
            self.status_text.SetLabel("Searching...")
            FinderThread(self.root_dir_tc.GetValue())
        else:
            self.UserError('"%s" is not a folder.' % 
                           self.root_dir_tc.GetValue())
    def searchDone(self, msg):
        items = msg.data
        self.search_btn.Enable()
        self.geodata_listbox.InsertItems(items=items, pos=0)
        self.status_text.SetLabel("Found %d item%s" % (len(items), "" if len(items) == 1 else "s"))

            
app = wx.App()
FindGeodata(None, -1, 'Find geodata')
app.MainLoop()
