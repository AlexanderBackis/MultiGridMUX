import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd
from matplotlib.colors import LogNorm

# ============================================================================
# PHS (1D)
# ============================================================================


def PHS_1D_plot(events, window):
    def PHS_1D_plot_bus(events, sub_title, number_bins):
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
    attributes = ['gADC_1', 'gADC_2', 'wADC_1', 'wADC_2']
    number_bins = int(window.phsBins.text())
    # Prepare figure
    fig = plt.figure()
    title = 'PHS (1D)\n(%s, ...)' % window.data_sets.splitlines()[0]
    fig.suptitle(title, x=0.5, y=1.03)
    fig.set_figheight(8)
    fig.set_figwidth(10)
    # Plot figure
    for i, attribute in enumerate(attributes):
        events_attribute = events[attribute]
        plt.subplot(2, 2, i+1)
        sub_title = attribute
        PHS_1D_plot_bus(events_attribute, sub_title, number_bins)
    plt.tight_layout()
    return fig












