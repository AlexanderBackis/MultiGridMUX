import os
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
import numpy as np
import struct
import re
import zipfile
import shutil

from Plotting.Miscellaneous import import_delimiter_table

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
# CLUSTER DATA
# =============================================================================

def cluster_data(data, ADC_to_Ch, window):
    """ Clusters the imported data and stores into a data frame.

        Does this in the following fashion:
            1. Reads one word at a time
            2. Checks what type of word it is (Header, Data or EoE).
            3. When a Header is encountered, 'isOpen' is set to 'True',
               signifying that a new event has been started. Data is then
               gathered into a single coincident event.
            4. When EoE is encountered the event is formed, and timestamp is
               assigned to it.
            5. After the iteration through data is complete, the dictionary
               containing the coincident events is convereted to a DataFrame.

    Args:
        data (tuple)    : Tuple containing data, one word per element.
        ADC_to_Ch (dict): Dictionary containing the delimiters for Channels
        window (window) : Window of GUI

    Returns:
        events_df (DataFrame): DataFrame containing one event
                               per row. Each event has information about:
                               "Bus", "Time", "Channel", "ADC".

    """
    # Initiate dictionaries to store data
    size = len(data)
    if window.MG_CNCS.isChecked():
        attributes = ['wADC_1', 'wADC_2', 'wChADC_1', 'wChADC_2',
                      'gADC_1', 'gADC_2', 'gChADC_1', 'gChADC_2']
        channels = ['wCh_1', 'wCh_2', 'gCh_1', 'gCh_2']
    elif window.MG_24.isChecked():
        if window.module_button_20.isChecked():
            attributes = ['wADC_3', 'wADC_4', 'wChADC_3', 'wChADC_4',
                          'wADC_1', 'wADC_2', 'wChADC_1', 'wChADC_2',
                          'gADC_1', 'gADC_2', 'gChADC_1', 'gChADC_2']
        else: 
            attributes = ['wADC_1', 'wADC_2', 'wChADC_1', 'wChADC_2',
                          'wADC_3', 'wADC_4', 'wChADC_3', 'wChADC_4',
                          'gADC_1', 'gADC_2', 'gChADC_1', 'gChADC_2']
        channels = ['wCh_1', 'wCh_2', 'wCh_3', 'wCh_4','gCh_1', 'gCh_2']
    events = {'Module': np.zeros([size], dtype=int),
              'ToF': np.zeros([size], dtype=int)
              }
    for attribute in attributes:
        events.update({attribute: np.zeros([size], dtype=int)})
    for channel in channels:
        events.update({channel: np.zeros([size], dtype=int)})
    # Declare parameters
    wires_or_grids = {'w': 'Wires', 'g': 'Grids'}
    #Declare temporary variables
    isOpen = False
    index = 0
    #Four possibilities in each word: Header, DataEvent, DataExTs or EoE.
    for i, word in enumerate(data):
        if (word & SignatureMask) == Header:
            # Extract values
            Module = (word & ModuleMask) >> ModuleShift
            events['Module'][index] = Module
            # Adjust temporary variables
            isOpen = True
        elif ((word & SignatureMask) == Data) & isOpen:
            # Extract values
            ADC = (word & ADCMask)
            Channel = ((word & ChannelMask) >> ChannelShift)
            attribute = attributes[Channel]
            events[attribute][index] = ADC
            # Check if wire or grid
            w_or_g = wires_or_grids[attribute[:1]]
            # Get discreet channel
            if len(attribute) == 8:
                physical_Ch = ADC_to_Ch[w_or_g][ADC]
                channel_attribute = attribute[0:3] + attribute[-2:]
                events[channel_attribute][index] = physical_Ch
        elif ((word & SignatureMask) == EoE) & isOpen:
            # Extract values
            ToF = (word & TimeStampMask)
            events['ToF'][index] = ToF
            # Increase index and reset temporary variables
            isOpen = False
            index += 1

    #Remove empty elements and save in DataFrame for easier analysis
    for key in events:
        events[key] = events[key][0:index]
    events_df = pd.DataFrame(events)
    return events_df


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


def get_ADC_to_Ch(self):
    # Declare parameters
    layers_dict = {'Wires': 16, 'Grids': 12}
    delimiters_table = import_delimiter_table(self)
    channel_mapping = import_channel_mappings(self)
    print(channel_mapping['Wires'])
    ADC_to_Ch = {'Wires': {i: -1 for i in range(4096)},
                 'Grids': {i: -1 for i in range(4096)}}
    for key, delimiters in delimiters_table.items():
        layers = layers_dict[key]
        print(key)
        for i, (start, stop) in enumerate(delimiters):
            # Get channel mapping and delimiters
            channel = channel_mapping[key][i]
            small_delimiters = np.linspace(start, stop, layers+1)
            # Iterate through small delimiters
            previous_value = small_delimiters[0]
            for j, value in enumerate(small_delimiters[1:]):
                channel = channel_mapping[key][i*layers+j]
                print('i: %s, Ch: %s' % (str(i*layers+j), str(channel)))
                start, stop = int(round(previous_value)), int(round(value))
                # Assign ADC->Ch mapping for all values within interval
                for k in np.arange(start, stop, 1):
                    ADC_to_Ch[key][k] = channel
                previous_value = value
    return ADC_to_Ch


def import_channel_mappings(self):
    dirname = os.path.dirname(__file__)
    path = os.path.join(dirname, '../Tables/Grid_Wire_Channel_Mapping.xlsx')
    matrix = pd.read_excel(path).values
    wires, grids = [], []
    if self.module_button_20.isChecked():
        for row in matrix[1:]:
            wires.append(row[1])
            if not np.isnan(row[3]):
                grids.append(np.array(row[3]))
    elif self.module_button_16.isChecked():
        for row in matrix[1:]:
            if not np.isnan(row[5]):
                wires.append(row[5])
            if not np.isnan(row[7]):
                grids.append(np.array(row[7]))
    return {'Wires': np.array(wires), 'Grids': np.array(grids)}

"""
def import_delimiter_table():
    dirname = os.path.dirname(__file__)
    path = os.path.join(dirname, '../Tables/Histogram_delimiters.xlsx')
    matrix = pd.read_excel(path).values
    wires, grids = [], []
    for row in matrix[1:]:
        wires.append(np.array([row[0], row[1]])) # 0 1
        if not np.isnan(row[2]): # 2
            grids.append(np.array([row[2], row[3]])) # 2 3
    return {'Wires': np.array(wires), 'Grids': np.array(grids)}
"""
