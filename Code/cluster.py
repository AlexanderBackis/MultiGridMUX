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
# CLUSTER DATA
# =============================================================================

def cluster_data(data, ADC_to_Ch_dict, window):
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
    def create_events_dictionary(size):
        events = {'ToF': np.zeros([size], dtype=int),
                  'wADC_m1': np.zeros([size], dtype=int),
                  'wADC_m2': np.zeros([size], dtype=int),
                  'wChADC_m1': np.zeros([size], dtype=int),
                  'wChADC_m2': np.zeros([size], dtype=int),
                  'gADC_m1': np.zeros([size], dtype=int),
                  'gADC_m2': np.zeros([size], dtype=int),
                  'gChADC_m1': np.zeros([size], dtype=int),
                  'gChADC_m2': np.zeros([size], dtype=int),
                  'wCh_m1': np.zeros([size], dtype=int),
                  'wCh_m2': np.zeros([size], dtype=int),
                  'gCh_m1': np.zeros([size], dtype=int),
                  'gCh_m2': np.zeros([size], dtype=int)
                  }
        return events
    # Initiate dictionaries to store data
    size = len(data)
    attributes = ['wADC_m1', 'wADC_m2', 'wChADC_m1', 'wChADC_m2',
                  'wADC_m1', 'wADC_m2', 'wChADC_m1', 'wChADC_m2',
                  'gADC_m1', 'gADC_m2', 'gChADC_m1', 'gChADC_m2']
    channels = {'wChADC_m1': 'wCh_m1',
                'wChADC_m2': 'wCh_m2',
                'gChADC_m1': 'gCh_m1',
                'gChADC_m2': 'gCh_m2'
                }
    events_20_layers = create_events_dictionary(size)
    events_16_layers = create_events_dictionary(size)
    #Declare temporary variables
    index = 0
    #Four possibilities in each word: Header, DataEvent, DataExTs or EoE.
    for i, word in enumerate(data):
        if (word & SignatureMask) == Header:
            pass
            #print('START')
        elif ((word & SignatureMask) == Data):
            # Extract values
            ADC = (word & ADCMask)
            Channel = ((word & ChannelMask) >> ChannelShift)
            #print(Channel)
            attribute = attributes[Channel]
            # Extract data and insert into our different detectors
            if 0 <= Channel <= 1:
                #print('wADC_16')
                #print(attribute)
                events_16_layers[attribute][index] = ADC
            elif 2 <= Channel <= 3:
                #print('wADC_16')
                events_16_layers[attribute][index] = ADC
                Ch_ID = channels[attribute]
                #print('Attribute: %s' % attribute)
                #print('Ch_ID: %s' % Ch_ID)
                physical_Ch = ADC_to_Ch_dict['16_layers']['Wires'][ADC]
                events_16_layers[Ch_ID][index] = physical_Ch
            elif 4 <= Channel <= 5:
                #print('wADC_20')
                #print(attribute)
                events_20_layers[attribute][index] = ADC
            elif 6 <= Channel <= 7:
                #print('wADC_20')
                events_20_layers[attribute][index] = ADC
                Ch_ID = channels[attribute]
                #print('Attribute: %s' % attribute)
                #print('Ch_ID: %s' % Ch_ID)
                physical_Ch = ADC_to_Ch_dict['20_layers']['Wires'][ADC]
                events_20_layers[Ch_ID][index] = physical_Ch
            elif 8 <= Channel <= 9:
                #print('gADC_20 and gADC_16')
                #print(attribute)
                events_20_layers[attribute][index] = ADC
                events_16_layers[attribute][index] = ADC
            else:
                #print('gADC_Ch_20 and gADC_16')
                Ch_ID = channels[attribute]
                #print('Attribute: %s' % attribute)
                #print('Ch_ID: %s' % Ch_ID)
                # Assign 20 layers
                events_20_layers[attribute][index] = ADC
                physical_Ch = ADC_to_Ch_dict['20_layers']['Grids'][ADC]
                events_20_layers[Ch_ID][index] = physical_Ch
                # Assign 16 layers
                events_16_layers[attribute][index] = ADC
                physical_Ch = ADC_to_Ch_dict['16_layers']['Grids'][ADC]
                events_16_layers[Ch_ID][index] = physical_Ch
        elif ((word & SignatureMask) == EoE):
            # Extract values
            ToF = (word & TimeStampMask)
            events_20_layers['ToF'][index] = ToF
            events_16_layers['ToF'][index] = ToF
            # Increase index
            index += 1
    #Remove empty elements and save in DataFrame for easier analysis
    for key in events_20_layers:
        events_20_layers[key] = events_20_layers[key][0:index]
    for key in events_16_layers:
        events_16_layers[key] = events_16_layers[key][0:index]
    events_20_layers_df = pd.DataFrame(events_20_layers)
    events_16_layers_df = pd.DataFrame(events_16_layers)
    #print(events_16_layers_df)
    #print(events_20_layers_df.shape[0])
    #print('20 layers wires multiplicity 1')
    #print(events_20_layers_df[events_20_layers_df['wCh_m1'] > -1].shape[0])
    #print('20 layers grids multiplicity 1')
    #print(events_20_layers_df[events_20_layers_df['gCh_m1'] > -1].shape[0])
    #print(events_20_layers_df[])
    return events_20_layers_df, events_16_layers_df


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
