import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
import plotly as py
import numpy as np
import plotly.graph_objs as go
import pandas as pd
import plotly.io as pio
import os


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
        for delimiter in delimiters:
            plt.axvline(delimiter[0], color='red', zorder=5)
            plt.axvline(delimiter[1], color='red', zorder=5)
            if sub_title[0] == 'g':
                spacings = 11
            else:
                spacings = 15
            for small_delimiter in np.linspace(delimiter[0], delimiter[1],
                                               spacings+2):
                plt.axvline(small_delimiter, color='blue', zorder=2)

    # Declare parameters
    if window.MG_CNCS.isChecked():
        attributes = ['gChADC_1', 'gChADC_2', 'wChADC_1', 'wChADC_2']
        rows = 2
        cols = 2
        height = 8
        width = 10
    else:
        attributes = ['wChADC_1', 'wChADC_2', 'gChADC_1',
                      'gChADC_2', 'wChADC_3', 'wChADC_4']
        rows = 3
        cols = 2
        height = 12
        width = 10
    number_bins = int(window.chBins.text())
    delimiter_table = import_delimiter_table(window)
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


# ============================================================================
# ADC
# ============================================================================


def ADC_plot(events, window):
    def PHS_1D_plot_bus(events, sub_title, number_bins):
        # Plot
        plt.title(sub_title)
        plt.xlabel('Collected charge [ADC channels]')
        plt.ylabel('Counts')
        plt.grid(True, which='major', zorder=0)
        plt.grid(True, which='minor', linestyle='--', zorder=0)
        plt.yscale('log')
        plt.hist(events, bins=number_bins, range=[0, 4095],
                 histtype='step', color='black', zorder=5)
    # Declare parameters
    if window.MG_CNCS.isChecked():
        attributes = ['gADC_1', 'gADC_2', 'wADC_1', 'wADC_2']
        rows = 2
        cols = 2
        height = 8
        width = 10
    else:
        attributes = ['gADC_1', 'gADC_2', 'wADC_1',
                      'wADC_2', 'wADC_3', 'wADC_4']
        rows = 3
        cols = 2
        height = 12
        width = 10
    number_bins = int(window.phsBins.text())
    # Prepare figure
    fig = plt.figure()
    fig.set_figheight(height)
    fig.set_figwidth(width)
    title = 'PHS (1D)\n(%s, ...)' % window.data_sets.splitlines()[0]
    fig.suptitle(title, x=0.5, y=1.03)
    # Plot figure
    for i, attribute in enumerate(attributes):
        events_attribute = events[attribute]
        plt.subplot(rows, cols, i+1)
        sub_title = attribute
        PHS_1D_plot_bus(events_attribute, sub_title, number_bins)
    plt.tight_layout()
    return fig




# =============================================================================
# Helper Functions
# =============================================================================

def import_delimiter_table(self):
    dirname = os.path.dirname(__file__)
    path = os.path.join(dirname, '../../Tables/Histogram_delimiters.xlsx')
    matrix = pd.read_excel(path).values
    wires, grids = [], []
    if self.module_button_20.isChecked():
        for row in matrix[1:]:
            wires.append(np.array([row[0], row[1]])) # 0 1
            if not np.isnan(row[2]): # 2
                grids.append(np.array([row[2], row[3]])) # 2 3
    elif self.module_button_16.isChecked():
        for row in matrix[1:]:
            if not np.isnan(row[4]):
                wires.append(np.array([row[4], row[5]])) # 0 1
            if not np.isnan(row[6]): # 2
                grids.append(np.array([row[6], row[7]])) # 2 3
    return {'Wires': np.array(wires), 'Grids': np.array(grids)}
