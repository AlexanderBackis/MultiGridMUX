import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
import plotly as py
import numpy as np
import plotly.graph_objs as go
import pandas as pd
import plotly.io as pio
import os
from Plotting.HelperFunctions import import_delimiter_table


# =============================================================================
# ToF
# =============================================================================


def ToF_histogram(window):
    # Get parameters
    number_bins = int(window.tofBins.text())
    # Produce histogram and plot
    fig = plt.figure()
    plt.hist(window.Clusters_16_layers.ToF, bins=number_bins,
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


def Channels_plot(window):
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
    df_20 = window.Clusters_20_layers
    df_16 = window.Clusters_16_layers
    attributes_20 = ['wChADC_m1', 'wChADC_m2']
    attributes_16 = ['wChADC_m1', 'wChADC_m2']
    attributes_grids = ['gChADC_m1', 'gChADC_m2']
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
    for i, attribute in enumerate(attributes_20):
        events_attribute_20 = df_20[attribute]
        plt.subplot(rows, cols, i+1)
        sub_title = attribute
        if sub_title[0] == 'w' and sub_title[-1] == '1':
            delimiters_20 = delimiter_table['20_layers']['Wires']
        sub_title = attribute + ' -- 20 layers'
        channels_plot_bus(events_attribute_20, sub_title, number_bins, delimiters_20)

    for i, attribute in enumerate(attributes_16):
        events_attribute_16 = df_16[attribute]
        plt.subplot(rows, cols, i+3)
        sub_title = attribute
        if sub_title[0] == 'w' and sub_title[-1] == '1':
            delimiters_16 = delimiter_table['16_layers']['Wires']
        sub_title = attribute + ' -- 16 layers'
        channels_plot_bus(events_attribute_16, sub_title, number_bins, delimiters_16)

    for i, attribute in enumerate(attributes_grids):
        events_attribute_grids = df_20[attribute]
        plt.subplot(rows, cols, i+5)
        sub_title = attribute
        delimiters = []
        if sub_title[0] == 'g':
            delimiters.extend(delimiter_table['20_layers']['Grids'])
            delimiters.extend(delimiter_table['16_layers']['Grids'])
        sub_title = attribute + ' -- both layers'
        channels_plot_bus(events_attribute_grids, sub_title, number_bins, delimiters)
    print("Order of the grids might be wrong in grid channel plots")

    plt.tight_layout()
    return fig


# ============================================================================
# ADC
# ============================================================================


def ADC_plot(window):
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
    attributes = ['gADC_m1', 'gADC_m2',
                  'wADC_m1', 'wADC_m2',
                  'wChADC_m1', 'wChADC_m2',
                  'gChADC_m1', 'gChADC_m2']
    rows = 4
    cols = 4
    height = 12
    width = 10
    number_bins = int(window.chBins.text())
    # Prepare figure
    fig = plt.figure()
    fig.set_figheight(height)
    fig.set_figwidth(width)
    title = 'PHS (1D)\n(%s, ...)' % window.data_sets.splitlines()[0]
    fig.suptitle(title, x=0.5, y=1.03)
    # Plot figure - 16 layers
    for i, attribute in enumerate(attributes):
        events_attribute = window.Clusters_16_layers[attribute]
        plt.subplot(rows, cols, i+1)
        sub_title = attribute + ' (16 layers)'
        PHS_1D_plot_bus(events_attribute, sub_title, number_bins)
    for i, attribute in enumerate(attributes):
        events_attribute = window.Clusters_20_layers[attribute]
        plt.subplot(rows, cols, i+1+8)
        sub_title = attribute + ' (20 layers)'
        PHS_1D_plot_bus(events_attribute, sub_title, number_bins)
    # Plot figure - 20 layers
    for i, attribute in enumerate(attributes):
            events_attribute = window.Clusters_20_layers[attribute]
            plt.subplot(rows, cols, i+1+8)
            sub_title = attribute + ' (20 layers)'
            PHS_1D_plot_bus(events_attribute, sub_title, number_bins)
    plt.tight_layout()
    return fig
