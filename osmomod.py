
import wx
import random
import numpy as np

from HypoModPy.hypomods import *
from HypoModPy.hypoparams import *
from HypoModPy.hypodat import *
from HypoModPy.hypogrid import *

#ID_heatflag = wx.NewIdRef()



class OsmoMod(Mod):
    def __init__(self, mainwin, tag):
        Mod.__init__(self, mainwin, tag)

        if mainwin.modpath != "": self.path = mainwin.modpath + "/Osmo"
        else: self.path = "Osmo"

        if os.path.exists(self.path) == False: 
            os.mkdir(self.path)

        self.mainwin = mainwin

        self.protobox = OsmoProtoBox(self, "proto", "Input Protocols", wx.Point(0, 0), wx.Size(320, 500))
        self.gridbox = GridBox(self, "Data Grid", wx.Point(0, 0), wx.Size(320, 500), 100, 20)
        self.osmobox = OsmoBox(self, "osmo", "Osmo", wx.Point(0, 0), wx.Size(320, 500))

        # link mod owned boxes
        mainwin.gridbox = self.gridbox

        self.modtools[self.osmobox.boxtag] = self.osmobox
        self.modtools[self.protobox.boxtag] = self.protobox
        self.modtools[self.gridbox.boxtag] = self.gridbox

        self.osmobox.Show(True)
        self.modbox = self.osmobox

        mainwin.toolset.AddBox(self.osmobox)  
        mainwin.toolset.AddBox(self.protobox)  
        mainwin.toolset.AddBox(self.gridbox)  

        self.ModLoad()
        print("Osmo Model OK")

        self.osmodata = OsmoDat()
        self.PlotData()
        self.graphload = True

        for i in range(1, 100):
            self.osmodata.water[i] = 100


    ## PlotData() defines all the available plots, each linked to a data array in osmodata
    ##
    def PlotData(self):
        # Data plots
        #
        # AddPlot(PlotDat(data array, xfrom, xto, yfrom, yto, label string, plot type, bin size, colour), tag string)
        # ----------------------------------------------------------------------------------
        self.plotbase.AddPlot(PlotDat(self.osmodata.water, 0, 2000, 0, 5000, "water", "line", 1, "blue"), "water")
        self.plotbase.AddPlot(PlotDat(self.osmodata.salt, 0, 2000, 0, 100, "salt", "line", 1, "red"), "salt")
        self.plotbase.AddPlot(PlotDat(self.osmodata.osmo, 0, 2000, 0, 100, "osmo", "line", 1, "green"), "osmo")
        self.plotbase.AddPlot(PlotDat(self.osmodata.vaso, 0, 2000, 0, 100, "vaso", "line", 1, "purple"), "vaso")


    def DefaultPlots(self):
        if len(self.mainwin.panelset) > 0: self.mainwin.panelset[0].settag = "water"
        if len(self.mainwin.panelset) > 1: self.mainwin.panelset[1].settag = "salt"
        if len(self.mainwin.panelset) > 2: self.mainwin.panelset[2].settag = "osmo"


    def OnModThreadComplete(self, event):
        #runmute->Lock();
        #runflag = 0;
        #runmute->Unlock();

        # plot store test code
        # for i in range(1, 100):
        #     self.osmodata.water[i] = 200
        #self.osmodata.water.label = "plot test"

        self.mainwin.scalebox.GraphUpdateAll()
        #DiagWrite("Model thread OK\n\n")


    def OnModThreadProgress(self, event):
        self.osmobox.SetCount(event.GetInt())


    def RunModel(self):
        self.mainwin.SetStatusText("Osmo Model Run")
        modthread = OsmoModel(self)
        modthread.start()



class OsmoDat():
    def __init__(self):
        self.storesize = 10000

        # initialise arrays for recording model variables (or any model values)
        self.water = datarray(self.storesize + 1)
        self.salt = pdata(self.storesize + 1)
        self.osmo = pdata(self.storesize + 1)
        self.vaso = pdata(self.storesize + 1)



class OsmoBox(ParamBox):
    def __init__(self, mod, tag, title, position, size):
        ParamBox.__init__(self, mod, title, position, size, tag, 0, 1)

        self.autorun = True

        # Initialise Menu 
        self.InitMenu()

        # Model Flags
        ID_randomflag = wx.NewIdRef()   # request a new control ID
        self.AddFlag(ID_randomflag, "randomflag", "Fixed Random Seed", 0)         # menu accessed flags for switching model code


        # Parameter controls
        #
        # AddCon(tag string, display string, initial value, click increment, decimal places)
        # ----------------------------------------------------------------------------------
        self.paramset.AddCon("runtime", "Run Time", 2000, 1, 0)
        self.paramset.AddCon("hstep", "h Step", 1, 0.1, 1)
        self.paramset.AddCon("waterloss", "Water Loss", 0, 0.00001, 5)

        self.ParamLayout(2)   # layout parameter controls in two columns

        # ----------------------------------------------------------------------------------

        runbox = self.RunBox()
        paramfilebox = self.StoreBoxSync()

        ID_Proto = wx.NewIdRef()
        self.AddPanelButton(ID_Proto, "Proto", self.mod.protobox)
        ID_Grid = wx.NewIdRef()
        self.AddPanelButton(ID_Grid, "Grid", self.mod.gridbox)

        self.mainbox.AddSpacer(5)
        self.mainbox.Add(self.pconbox, 1, wx.ALIGN_CENTRE_HORIZONTAL|wx.ALIGN_CENTRE_VERTICAL|wx.ALL, 0)
        self.mainbox.AddStretchSpacer(5)
        self.mainbox.Add(runbox, 0, wx.ALIGN_CENTRE_HORIZONTAL|wx.ALIGN_CENTRE_VERTICAL|wx.ALL, 0)
        self.mainbox.AddSpacer(5)
        self.mainbox.Add(paramfilebox, 0, wx.ALIGN_CENTRE_HORIZONTAL|wx.ALIGN_CENTRE_VERTICAL|wx.ALL, 0)	
        #self.mainbox.AddStretchSpacer()
        self.mainbox.Add(self.buttonbox, 0, wx.ALIGN_CENTRE_HORIZONTAL | wx.ALIGN_CENTRE_VERTICAL | wx.ALL, 0)
        self.mainbox.AddSpacer(5)
        #self.mainbox.AddSpacer(2)
        self.panel.Layout()



class OsmoProtoBox(ParamBox):
    def __init__(self, mod, tag, title, position, size):
        ParamBox.__init__(self, mod, title, position, size, tag, 0, 1)

        self.autorun = True

        # Initialise Menu 
        #self.InitMenu()

        # Model Flags
    

        # Parameter controls
        #
        # AddCon(tag string, display string, initial value, click increment, decimal places)
        # ----------------------------------------------------------------------------------
        self.paramset.AddCon("drinkstart", "Drink Start", 0, 1, 0)
        self.paramset.AddCon("drinkstop", "Drink Stop", 0, 1, 0)
        self.paramset.AddCon("drinkrate", "Drink Rate", 10, 1, 0)

        self.ParamLayout(3)   # layout parameter controls in two columns

        # ----------------------------------------------------------------------------------

        self.mainbox.AddSpacer(5)
        self.mainbox.Add(self.pconbox, 1, wx.ALIGN_CENTRE_HORIZONTAL|wx.ALIGN_CENTRE_VERTICAL|wx.ALL, 0)
        self.mainbox.AddStretchSpacer(5)
        self.mainbox.AddSpacer(2)
        self.panel.Layout()



class OsmoModel(ModThread):
    def __init__(self, mod):
        ModThread.__init__(self, mod.modbox, mod.mainwin)

        self.mod = mod
        self.osmobox = mod.osmobox
        self.mainwin = mod.mainwin
        self.scalebox = mod.mainwin.scalebox

    ## run() is the thread entry function, used to initialise and call the main Model() function 
    ##    
    def run(self):
        # Read model flags
        self.randomflag = self.osmobox.modflags["randomflag"]      # model flags are useful for switching elements of the model code while running

        if self.randomflag: random.seed(0)
        else: random.seed(datetime.now().microsecond)

        self.Model()
        wx.QueueEvent(self.mod, ModThreadEvent(ModThreadCompleteEvent))


    ## Model() reads in the model parameters, initialises variables, and runs the main model loop
    ##
    def Model(self):
        osmodata = self.mod.osmodata
        osmobox = self.mod.osmobox
        osmoparams = self.mod.osmobox.GetParams()
        protoparams = self.mod.protobox.GetParams()

        # Read parameters
        runtime = int(osmoparams["runtime"])
        waterloss = osmoparams["waterloss"]

        # Initialise variables
        water = 50
        salt = 2000
        osmo = salt / water
        vaso = 0

        # Initialise model variable recording arrays
        osmodata.water.clear()
        osmodata.salt.clear()
        osmodata.osmo.clear()
        osmodata.vaso.clear()

        # Initialise model variables
        osmodata.water[0] = water
        osmodata.salt[0] = salt
        osmodata.osmo[0] = osmo
        osmodata.vaso[0] = vaso
        osmo_thresh = 280
        v_grad = 0.2
        v_max = 20

        # Run model loop
        for i in range(1, runtime + 1):

            if i%100 == 0: osmobox.SetCount(i * 100 / runtime)     # Update run progress % in model panel

            water = water - (water * waterloss)
            salt = salt
            osmo = salt / water
            if osmo < osmo_thresh: vaso = 0
            else: 
                vaso = v_grad * (osmo - osmo_thresh)
                if vaso > v_max: vaso = v_max

            # Record model variables
            osmodata.water[i] = water
            osmodata.salt[i] = salt
            osmodata.osmo[i] = osmo
            osmodata.vaso[i] = vaso


        # Set plot time range
        osmodata.water.xmax = runtime * 1.1
        osmodata.salt.xmax = runtime * 1.1
        osmodata.osmo.xmax = runtime * 1.1
        osmodata.vaso.xmax = runtime * 1.1






