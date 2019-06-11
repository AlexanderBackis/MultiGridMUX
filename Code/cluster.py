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

def cluster_data(data, ILL_buses=[], progressBar=None, dialog=None, app=None):
    """ Clusters the imported data and stores it two data frames: one for 
        individual events and one for coicident events (i.e. candidate neutron 
        events). 
        
        Does this in the following fashion for coincident events:
            1. Reads one word at a time
            2. Checks what type of word it is (Header, BusStart, DataEvent,
               DataExTs or EoE).
            3. When a Header is encountered, 'isOpen' is set to 'True',
               signifying that a new event has been started. Data is then
               gathered into a single coincident event until a different bus is
               encountered (unless ILL exception), in which case a new event is
               started.
            4. When EoE is encountered the event is formed, and timestamp is 
               assigned to it and all the created events under the current 
               Header. This event is placed in the created dictionary.
            5. After the iteration through data is complete, the dictionary
               containing the coincident events is convereted to a DataFrame.
           
    Args:
        data (tuple)    : Tuple containing data, one word per element.
        ILL_buses (list): List containg all ILL buses
            
    Returns:
        data (tuple): A tuple where each element is a 32 bit mesytec word
        
        events_df (DataFrame): DataFrame containing one event (wire or grid) 
                               per row. Each event has information about:
                               "Bus", "Time", "Channel", "ADC".
        
    """
    # Initiate dictionaries to store data
    size = len(data)
    events = {'Module': np.zeros([size], dtype=int),
              'ToF': np.zeros([size], dtype=int),
              'gADC_1': np.zeros([size], dtype=int),
              'gCh_1': np.zeros([size], dtype=int),
              'gADC_2': np.zeros([size], dtype=int),
              'gCh_2': np.zeros([size], dtype=int),
              'wADC_1': np.zeros([size], dtype=int),
              'wCh_1': np.zeros([size], dtype=int),
              'wADC_2': np.zeros([size], dtype=int),
              'wCh_2': np.zeros([size], dtype=int),
              }
    #Declare variables
    index = 0
    attributes = ['gADC_1', 'gADC_2', 'gCh_1', 'gCh_2',
                  'wADC_1', 'wADC_2', 'wCh_1', 'wCh_2']
    #Declare temporary variables
    isOpen = False
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




