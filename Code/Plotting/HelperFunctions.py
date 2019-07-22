import os
import numpy as np
import pandas as pd

# =============================================================================
# Filter
# =============================================================================


def filter_clusters(clusters, window):
    # Declare parameters
    parameters = {'wADC_m1': [window.wADC_min.value(),
                              window.wADC_max.value(),
                              window.wADC_filter.isChecked()],
                  'wADC_m2': [window.wADC_min.value(),
                              window.wADC_max.value(),
                              window.wADC_filter.isChecked()],
                  'gADC_m1': [window.gADC_min.value(),
                              window.gADC_max.value(),
                              window.gADC_filter.isChecked()],
                  'gADC_m2': [window.gADC_min.value(),
                              window.gADC_max.value(),
                              window.gADC_filter.isChecked()],
                  'ToF':  [float(window.ToF_min.text()),
                           float(window.ToF_max.text()),
                           window.ToF_filter.isChecked()],
                  'wCh_m1': [window.wCh_min.value(),
                             window.wCh_max.value(),
                             window.wCh_filter.isChecked()],
                  'gCh_m1': [window.gCh_min.value(),
                             window.gCh_max.value(),
                             window.gCh_filter.isChecked()],
                  'gCh_m2': [window.gCh_min.value(),
                             window.gCh_max.value(),
                             window.gCh_filter.isChecked()],
                  }
    # Only include the filters that we want to use
    ce_red = clusters
    for par, (min_val, max_val, filter_on) in parameters.items():
        if filter_on:
            ce_red = ce_red[(ce_red[par] >= min_val) & (ce_red[par] <= max_val)]
    return ce_red


# =============================================================================
# Delimiter table
# =============================================================================

def import_delimiter_table():
    # Import excel files
    dirname = os.path.dirname(__file__)
    path = os.path.join(dirname, '../../Tables/Histogram_delimiters.xlsx')
    matrix = pd.read_excel(path).values
    # Save delimiters for 16 and 20 layers in dictionary
    indices = [[0, 1, 2, 3], [4, 5, 6, 7]]
    detectors = ['20_layers', '16_layers']
    delimiters_dictionary = {'20_layers': None, '16_layers': None}
    for detector, (a, b, c, d) in zip(detectors, indices):
        wires, grids = [], []
        #print(detector)
        for row in matrix[1:]:
            if not np.isnan(row[a]):
                wires.append(np.array([row[a], row[b]]))  # 0 1
            if not np.isnan(row[c]):  # 2
                grids.append(np.array([row[c], row[d]]))  # 2 3
        delimiters_dictionary[detector] = {'Wires': np.array(wires),
                                           'Grids': np.array(grids)}
        #print(delimiters_dictionary[detector])
    return delimiters_dictionary

def import_channel_mappings():
    # Import excel files
    dirname = os.path.dirname(__file__)
    path = os.path.join(dirname, '../../Tables/Grid_Wire_Channel_Mapping.xlsx')
    matrix = pd.read_excel(path).values
    # Save channel mappings for 16 and 20 layers in dictionary
    indices = [[1, 3], [5, 7]]
    detectors = ['20_layers', '16_layers']
    channel_mapping_table = {'20_layers': None, '16_layers': None}
    for detector, (a, b), layers in zip(detectors, indices, [20, 16]):
        wires, grids = {}, {}
        #print(detector)
        for row in matrix[1:]:
            if not np.isnan(row[a]):
                if layers == 16:
                    row_start = (row[a-1]//layers)*layers
                    value = row[a-1]  #(3*layers - row_start) + (row[a-1] - row_start)
                else:
                    value = row[a-1]
                wires.update({row[a]: value })
            if not np.isnan(row[b]):
                grids.update({row[b]: row[b-1]})
        channel_mapping_table[detector] = {'Wires': wires,
                                           'Grids': grids}
        #print(channel_mapping_table[detector])
    return channel_mapping_table


def get_ADC_to_Ch_dict():
    # Declare parameters
    detectors = ['20_layers', '16_layers']
    layers_dict = {'Wires': 16, 'Grids': 12}
    delimiters_dictionary = import_delimiter_table()
    channel_mapping_dictionary = import_channel_mappings()
    ADC_to_Ch_dict = {'20_layers': None, '16_layers': None}
    for detector in detectors:
        # Get values for current detector
        delimiters_table = delimiters_dictionary[detector]
        channel_mapping = channel_mapping_dictionary[detector]
        # Prepare storage of mapping for current detector
        ADC_to_Ch = {'Wires': {i: -1 for i in range(4096)},
                     'Grids': {i: -1 for i in range(4096)}}
        print(detector)
        print('--')
        for key, delimiters in delimiters_table.items():
            layers = layers_dict[key]
            for i, (start, stop) in enumerate(delimiters):
                # Get channel mapping and delimiters
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
            ADC_to_Ch_dict[detector] = ADC_to_Ch
        #print(ADC_to_Ch_dict[detector])
    return ADC_to_Ch_dict
