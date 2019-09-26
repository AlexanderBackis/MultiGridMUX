from PyQt5.QtWidgets import *

# =============================================================================
# Help message
# =============================================================================

def gethelp():
    msg = QMessageBox()
    msg.setStyleSheet("QLabel{min-width: 600px; min-height: 50px; font-size: 14px;}")
    msg.setText("How to use this program:")
    msg.setInformativeText("1. Click the import button and select a data file to be analysed. \n\n2. Apply filters and choose which type of plot.\n     PHS: Pulse Height Spectrum in \n\t1D (counts vs collected charge), \n\t2D (charge vs channel) \n\tfor wires and grids \n     Coincidences:\n\tcoincidence events in \n\t2D (grid vs wire channel number)\n\t3D (spatial) \n     Misc: \n\tToF (time of flight, counts vs TDC channels), \n\tChannels (collected charge vs counts for grids and wires),\n\tADC (collected charge vs counts for grids and wires), \n\tRate: prints total neutron rate, \n\tChannel rates: rates for each channel \n\nFilters: \n     Charge: number of wires, number of grids, ToF \n     Coordinates: number of modules, wCH (number of wire channels), gCH (number of grid channels) \n\nBins: select the number of bins for ToF, PHS and Channels plots")
    msg.setWindowTitle("Help")
    msg.setStandardButtons(QMessageBox.Ok)
    msg.exec_()
