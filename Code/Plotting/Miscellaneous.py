import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
import plotly as py
import numpy as np
import plotly.graph_objs as go
import pandas as pd
import plotly.io as pio
import os


# =============================================================================
# Channels
# =============================================================================


def Channels_plot(events, window):
    def channels_plot_bus(events, sub_title, number_bins, delimiters):
        # Plot
        plt.title(sub_title)
        plt.xlabel('Collected charge [ADC channels]')
        plt.ylabel('Counts')
        plt.grid(True, which='major', zorder=0)
        plt.grid(True, which='minor', linestyle='--', zorder=0)
        plt.yscale('log')
        plt.hist(events, bins=number_bins, range=[0, 4100],
                 histtype='step', color='black', zorder=5)
        for i, delimiter in enumerate(delimiters[:-1]):
            plt.axvline(delimiter, color='red', zorder=5)
            for small_delimiter in np.linspace(delimiter, delimiters[i+1], 16):
                plt.axvline(small_delimiter, color='blue',
                            linestyle='--', zorder=3)

    # Declare parameters
    if window.MG_CNCS.isChecked():
        attributes = ['gCh_1', 'gCh_2', 'wCh_1', 'wCh_2']
        rows = 2
        cols = 2
        height = 8
        width = 10
    else:
        attributes = ['gCh_1', 'gCh_2', 'wCh_1',
                      'wCh_2', 'wCh_3', 'wCh_4']
        rows = 3
        cols = 2
        height = 12
        width = 10
    number_bins = int(window.chBins.text())
    delimiter_table = import_delimiter_table()
    # Prepare figure
    fig = plt.figure()
    fig.set_figheight(height)
    fig.set_figwidth(width)
    title = 'Channels (1D)\n(%s, ...)' % window.data_sets.splitlines()[0]
    fig.suptitle(title, x=0.5, y=1.03)
    # Plot figure
    for i, attribute in enumerate(attributes):
        events_attribute = events[attribute]
        plt.subplot(rows, cols, i+1)
        sub_title = attribute
        if sub_title[0] == 'g':
            delimiters = delimiter_table['Grids']
        else:
            delimiters = delimiter_table['Wires']
        channels_plot_bus(events_attribute, sub_title, number_bins, delimiters)
    plt.tight_layout()
    return fig


# =============================================================================
# ToF
# =============================================================================


def ToF_histogram(df, window):
    # Get parameters
    number_bins = int(window.tofBins.text())
    # Produce histogram and plot
    fig = plt.figure()
    plt.hist(df.ToF, bins=number_bins,
             log=True, color='black', zorder=4,
             histtype='step', label='MG'
             )
    plt.title('ToF - histogram\n%s' % window.data_sets)
    plt.xlabel('ToF [TDC channels]')
    plt.ylabel('Counts')
    plt.grid(True, which='major', linestyle='--', zorder=0)
    plt.grid(True, which='minor', linestyle='--', zorder=0)
    plt.yscale('log')
    return fig


# =============================================================================
# Helper Functions
# =============================================================================

def import_delimiter_table():
    dirname = os.path.dirname(__file__)
    path = os.path.join(dirname, '../../Tables/Histogram_delimiters.xlsx')
    matrix = pd.read_excel(path).values
    delimiter_table = {'Wires': [], 'Grids': []}
    for row in matrix:
        delimiter_table['Wires'].append(row[0])
        if not np.isnan(row[1]):
            delimiter_table['Grids'].append(row[1])
    return delimiter_table









