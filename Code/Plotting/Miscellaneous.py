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
    def channels_plot_bus(events, sub_title, number_bins):
        # Plot
        plt.title(sub_title)
        plt.xlabel('Collected charge [ADC channels]')
        plt.ylabel('Counts')
        plt.grid(True, which='major', zorder=0)
        plt.grid(True, which='minor', linestyle='--', zorder=0)
        plt.yscale('log')
        plt.hist(events, bins=number_bins, #range=[0, 1050],
                 histtype='step', color='black', zorder=5)
    # Declare parameters
    attributes = ['gCh_1', 'gCh_2', 'wCh_1', 'wCh_2']
    number_bins = int(window.chBins.text())
    # Prepare figure
    fig = plt.figure()
    title = 'Channels (1D)\n(%s, ...)' % window.data_sets.splitlines()[0]
    fig.suptitle(title, x=0.5, y=1.03)
    fig.set_figheight(8)
    fig.set_figwidth(10)
    # Plot figure
    for i, attribute in enumerate(attributes):
        events_attribute = events[attribute]
        plt.subplot(2, 2, i+1)
        sub_title = attribute
        channels_plot_bus(events_attribute, sub_title, number_bins)
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














