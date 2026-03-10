## HypoModPython
##
## Started 5/11/18
## Continued 24/8/22
##
## Duncan MacGregor
##


import wx
from HypoModPy.hypomain import *


app = wx.App(False)
pos = wx.DefaultPosition
size = wx.Size(400, 500)
mainpath = ""
respath = ""
modname = "Osmo"
mainwin = HypoMain("HypoMod", pos, size, respath, mainpath, modname)
mainwin.Show()
mainwin.SetFocus()
mainwin.Show(True)
wx.CallAfter(mainwin.Raise)
go_foreground()
app.MainLoop()



