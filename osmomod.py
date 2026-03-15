
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

        self.osmodata = OsmoDat(100000)
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
        self.plotbase.AddPlot(PlotDat(self.osmodata.water_ECF, 0, 2000, 0, 5000, "water ECF", "line", 1, "green"), "water_ECF")
        self.plotbase.AddPlot(PlotDat(self.osmodata.water_ICF, 0, 2000, 0, 5000, "water ICF", "line", 1, "red"), "water_ICF")
        self.plotbase.AddPlot(PlotDat(self.osmodata.salt_ECF, 0, 2000, 0, 100, "salt ECF", "line", 1, "lightred"), "salt_ECF")
        self.plotbase.AddPlot(PlotDat(self.osmodata.salt_ICF, 0, 2000, 0, 100, "salt ICF", "line", 1, "lightblue"), "salt_ICF")
        self.plotbase.AddPlot(PlotDat(self.osmodata.osmo_ECF, 0, 2000, 0, 100, "osmo ECF", "line", 1, "lightgreen"), "osmo_ECF")
        self.plotbase.AddPlot(PlotDat(self.osmodata.osmo_ICF, 0, 2000, 0, 100, "osmo ICF", "line", 1, "lightblue"), "osmo_ICF")
        self.plotbase.AddPlot(PlotDat(self.osmodata.urine_water, 0, 2000, 0, 5000, "urine water", "line", 1, "yellow"), "urine_water")


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
        DiagWrite("Model thread OK\n\n")


    def OnModThreadProgress(self, event):
        self.osmobox.SetCount(event.GetInt())


    def RunModel(self):
        self.mainwin.SetStatusText("Osmo Model Run")
        modthread = OsmoModel(self)
        modthread.start()



class OsmoDat():
    def __init__(self, storesize):
        self.storesize = storesize

        # initialise arrays for recording model variables (or any model values)
        self.water = pdata(self.storesize + 1)
        self.salt = pdata(self.storesize + 1)
        self.osmo = pdata(self.storesize + 1)
        self.vaso = pdata(self.storesize + 1)
        self.water_ECF = pdata(self.storesize + 1)
        self.water_ICF = pdata(self.storesize + 1)
        self.salt_ECF = pdata(self.storesize + 1)
        self.salt_ICF = pdata(self.storesize + 1)
        self.osmo_ECF = pdata(self.storesize + 1)
        self.osmo_ICF = pdata(self.storesize + 1)
        self.urine_water = pdata(self.storesize + 1)
        self.urine_salt = pdata(self.storesize + 1)
        self.V2 = pdata(self.storesize + 1)


    def reset_all(self):
        for value in vars(self).values():
            if isinstance(value, pdata): value.reset()


class OsmoBox(ParamBox):
    def __init__(self, mod, tag, title, position, size):
        ParamBox.__init__(self, mod, title, position, size, tag, 0, 1)

        self.autorun = True

        # Initialise Menu 
        self.InitMenu()

        # Model Flags
        self.AddFlag("randomflag", "Fixed Random Seed", 0)         # menu accessed flags for switching model code


        # Parameter controls
        #
        # AddCon(tag string, display string, initial value, click increment, decimal places)
        # ----------------------------------------------------------------------------------
        self.paramset.AddCon("runtime", "Run Time", 2000, 1, 0)
        self.paramset.AddCon("hstep", "h Step", 1, 0.1, 1)
        self.paramset.AddCon("waterloss", "Water Loss", 0, 1, 4)
        self.paramset.AddCon("water_init", "Water Init", 40000, 1, 2)
        self.paramset.AddCon("salt_ECF_init", "Salt ECF Init", 100, 0.1, 2)
        self.paramset.AddCon("salt_ICF_init", "Salt ICF Init", 80, 0.1, 2)
        self.paramset.AddCon("ktrans", "ktrans", 0, 0.1, 4)

        self.paramset.AddCon("urine_min", "Urine Min", 400, 1, 1)
        self.paramset.AddCon("urine_max", "Urine Max", 15000, 1, 1)
        self.paramset.AddCon("osmo_thresh", "Osmolality Threshold", 282, 1, 1)
        self.paramset.AddCon("k_V", "k_V", 0.4, 0.01, 4)
        self.paramset.AddCon("R_n", "R_n", 2, 0.1, 4)
        self.paramset.AddCon("R_k", "R_k", 2, 0.1, 4)

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
        water_init = osmoparams["water_init"]
        #salt_init = osmoparams["salt_init"]
        salt_ECF_init = osmoparams["salt_ECF_init"]
        salt_ICF_init = osmoparams["salt_ICF_init"]
        ktrans = osmoparams["ktrans"]

        urine_min = osmoparams["urine_min"]
        urine_max = osmoparams["urine_max"]
        osmo_thresh = osmoparams["osmo_thresh"]
        k_V = osmoparams["k_V"]
        R_n = osmoparams["R_n"]
        R_k = osmoparams["R_k"]

        # Initialise variables
        water = water_init
        #salt = salt_init
        #osmo = (salt * 34.2) / (water / 1000)
        water_ECF = water_init * 0.33
        water_ICF = water_init * 0.67
        salt_ECF = salt_ECF_init
        salt_ICF = salt_ICF_init
        osmo_ECF = (salt_ECF * 34.2) / (water_ECF / 1000)
        osmo_ICF = salt_ICF / (water_ICF / 1000)
        water_trans = 0

        # Convert from ml/hour to ml/second
        waterloss = waterloss / 86400
        urine_min = urine_min / 86400
        urine_max = urine_max / 86400

        # Record initial values
        osmodata.water_ECF[0] = water_ECF
        osmodata.water_ICF[0] = water_ICF
        osmodata.salt_ECF[0] = salt_ECF
        osmodata.salt_ICF[0] = salt_ICF
        osmodata.osmo_ECF[0] = osmo_ECF
        osmodata.osmo_ICF[0] = osmo_ICF
        osmodata.urine_water[0] = urine_min * 86400   # Record minimum urine output at time 0
        osmodata.vaso[0] = 0

        DiagWrite(f"starting model loop, runtime {runtime}\n")

        # Run model loop
        for i in range(1, runtime + 1):

            #if i%100 == 0: osmobox.SetCount(i * 100 / runtime)     # Update run progress % in model panel
            if i%100 == 0:
                progevent = ModThreadEvent(ModThreadProgressEvent)
                progevent.SetInt(int(i * 100 / runtime)) 
                wx.QueueEvent(self.mod, progevent)                        # Update run progress % in model panel

            osmo_ECF = (salt_ECF * 34.2) / (water_ECF / 1000)
            osmo_ICF = salt_ICF / (water_ICF / 1000)
            water_trans = ktrans * (osmo_ECF - osmo_ICF)

            if osmo_ECF > osmo_thresh: vaso = k_V * (osmo_ECF - osmo_thresh)
            else: vaso = 0

            R_V2 = pow(vaso, R_n) / (pow(R_k, R_n) + pow(vaso, R_n))
            urine_water = urine_min + (1 - R_V2) * (urine_max - urine_min)
            water_ECF = water_ECF - waterloss + water_trans - urine_water
            water_ICF = water_ICF - water_trans
            if water_ECF < 0: water_ECF = 0

            #salt = salt
            #osmo = (salt * 34.2) / (water / 1000)

            # Record model variables
            osmodata.water_ECF[i] = water_ECF
            osmodata.water_ICF[i] = water_ICF
            osmodata.salt_ECF[i] = salt_ECF
            osmodata.salt_ICF[i] = salt_ICF
            osmodata.osmo_ECF[i] = osmo_ECF
            osmodata.osmo_ICF[i] = osmo_ICF
            osmodata.urine_water[i] = urine_water * 86400
            osmodata.vaso[i] = vaso

        DiagWrite("model loop ok\n")

        # Set plot time range
        osmodata.water_ECF.xmax = runtime * 1.1
        osmodata.water_ICF.xmax = runtime * 1.1
        osmodata.salt_ECF.xmax = runtime * 1.1
        osmodata.salt_ICF.xmax = runtime * 1.1
        osmodata.osmo_ECF.xmax = runtime * 1.1
        osmodata.osmo_ICF.xmax = runtime * 1.1
        osmodata.urine_water.xmax = runtime * 1.1
        osmodata.vaso.xmax = runtime * 1.1






