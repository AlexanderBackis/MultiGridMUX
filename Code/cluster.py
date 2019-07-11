import os
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
import numpy as np
import struct
import re
import zipfile
import shutil

# =============================================================================
# Masks
# =============================================================================

SignatureMask    = 0xC0000000    # 1100 0000 0000 0000 0000 0000 0000 0000
SubSignatureMask = 0x3FE00000    # 0011 1111 1110 0000 0000 0000 0000 0000

ModuleMask       = 0x00FF0000    # 0000 0000 1111 1111 0000 0000 0000 0000
ChannelMask      = 0x001F0000    # 0000 0000 0001 1111 0000 0000 0000 0000
ADCMask          = 0x00003FFF    # 0000 0000 0000 0000 0011 1111 1111 1111
ExTsMask         = 0x0000FFFF    # 0000 0000 0000 0000 1111 1111 1111 1111
TimeStampMask 	 = 0x3FFFFFFF    # 0011 1111 1111 1111 1111 1111 1111 1111
WordCountMask  	 = 0x00000FFF    # 0000 0000 0000 0000 0000 1111 1111 1111


# =============================================================================
# Dictionary
# =============================================================================

Header        	 = 0x40000000    # 0100 0000 0000 0000 0000 0000 0000 0000
Data          	 = 0x00000000    # 0000 0000 0000 0000 0000 0000 0000 0000
EoE           	 = 0xC0000000    # 1100 0000 0000 0000 0000 0000 0000 0000

DataEvent        = 0x04000000    # 0000 0100 0000 0000 0000 0000 0000 0000
DataExTs         = 0x04800000    # 0000 0100 1000 0000 0000 0000 0000 0000


# =============================================================================
# Bit shifts
# =============================================================================

ChannelShift     = 16
ModuleShift      = 16
ExTsShift        = 30

# =============================================================================
# SAVE DATA
# =============================================================================

def save_data(path, window):
    # Initiate loading bar
    window.save_progress.setValue(0)
    window.save_progress.show()
    window.refresh_window()
    # Save clusters
    window.Clusters.to_hdf(path, 'Clusters', complevel=9)
    window.save_progress.setValue(50)
    window.refresh_window()
    # Save parameters
    data_sets = pd.DataFrame({'data_sets': [window.data_sets]})
    measurement_time = pd.DataFrame({'measurement_time': [window.measurement_time]})
    data_sets.to_hdf(path, 'data_sets', complevel=9)
    measurement_time.to_hdf(path, 'measurement_time', complevel=9)
    window.save_progress.setValue(100)
    window.refresh_window()
    window.save_progress.close()
    window.refresh_window()


# =============================================================================
# LOAD DATA
# =============================================================================


def load_data(path, window):
    # Initiate loading bar
    window.load_progress.setValue(0)
    window.load_progress.show()
    window.refresh_window()
    # Load clusters
    Clusters = pd.read_hdf(path, 'Clusters')
    window.load_progress.setValue(50)
    window.refresh_window()
    # Load parameters
    measurement_time_df = pd.read_hdf(path, 'measurement_time')
    measurement_time = measurement_time_df['measurement_time'].iloc[0]
    data_sets_df = pd.read_hdf(path, 'data_sets')
    data_sets = data_sets_df['data_sets'].iloc[0]
    # Write or append
    window.Clusters = Clusters
    window.measurement_time = measurement_time
    window.data_sets = data_sets
    # Reset index on clusters and events
    window.Clusters.reset_index(drop=True, inplace=True)
    # Update text browser and close loading bar
    window.load_progress.setValue(100)
    window.refresh_window()
    window.load_progress.close()
    window.data_sets_browser.setText(window.data_sets)
    window.refresh_window()


# =============================================================================
# Helper Functions
# =============================================================================

def mkdir_p(mypath):
    '''Creates a directory. equivalent to using mkdir -p on the command line'''

    from errno import EEXIST
    from os import makedirs, path

    try:
        makedirs(mypath)
    except OSError as exc:
        if exc.errno == EEXIST and path.isdir(mypath):
            pass
        else:
            raise
