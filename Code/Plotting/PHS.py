import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd
from matplotlib.colors import LogNorm
from Plotting.HelperFunctions import filter_clusters


# ============================================================================
# PHS (1D)
# ============================================================================


def PHS_1D_plot(clusters, window):
    def PHS_1D_plot_bus(clusters, typeCh, sub_title, number_bins):
        # Plot
        plt.title(sub_title)
        plt.xlabel('Collected charge [ADC channels]')
        plt.ylabel('Counts')
        plt.grid(True, which='major', zorder=0)
        plt.grid(True, which='minor', linestyle='--', zorder=0)
        plt.yscale('log')
        if wg == 'g':
            adcs = clusters['gADC_1'].append(clusters['gADC_2'])
        else:
            adcs = clusters['wADC_1']
        plt.hist(adcs, bins=number_bins, range=[0, 4095], histtype='step',
                 color='black', zorder=5)
    # Intial filter
    clusters = filter_clusters(clusters, window)
    # Declare parameters
    number_bins = int(window.phsBins.text())
    wg_list = ['w', 'g']
    grids_or_wires = {'w': 'Wires', 'g': 'Grids'}
    # Prepare figure
    fig = plt.figure()
    title = 'PHS (1D)\n(%s, ...)' % window.data_sets.splitlines()[0]
    fig.suptitle(title, x=0.5, y=1.03)
    fig.set_figheight(4)
    fig.set_figwidth(10)
    # Plot figure
    for i, wg in enumerate(wg_list):
        plt.subplot(1, 2, i+1)
        sub_title = grids_or_wires[wg]
        PHS_1D_plot_bus(clusters, wg, sub_title, number_bins)
    plt.tight_layout()
    return fig

# =============================================================================
# PHS (2D)
# =============================================================================


def PHS_2D_plot(clusters, window):
    def PHS_2D_plot_bus(clusters, wg, limit, bins, sub_title, vmin, vmax):
        plt.xlabel('Channel')
        plt.ylabel('Charge [ADC channels]')
        plt.title(sub_title)
        if wg == 'g':
            channels = clusters['gCh_1'].append(clusters['gCh_2'])
            adcs = clusters['gADC_1'].append(clusters['gADC_2'])
        else:
            channels = clusters['wCh_1']
            adcs = clusters['wADC_1']
        plt.hist2d(channels, adcs,
                   bins=[bins, 120],
                   range=[limit, [0, 4095]], norm=LogNorm(),
                   #vmin=vmin, vmax=vmax,
                   cmap='jet')
        plt.colorbar()
    # Initial filter
    clusters = filter_clusters(clusters, window)
    # Declare parameters
    wg_list = ['w', 'g']
    limits = [[-0.5, 79.5], [-0.5, 11.5]]
    bins = [80, 12]
    grids_or_wires = {'w': 'Wires', 'g': 'Grids'}
    # Prepare figure
    fig = plt.figure()
    title = 'PHS (2D) - MG\n(%s, ...)' % window.data_sets.splitlines()[0]
    fig.suptitle(title, x=0.5, y=1.03)
    vmin = 1
    vmax = clusters.shape[0] // 1000 + 100
    fig.set_figheight(4)
    fig.set_figwidth(10)
    # Plot figure
    for i, (wg, limit, bins) in enumerate(zip(wg_list, limits, bins)):
        # Filter events based on wires or grids
        plt.subplot(1, 2, i+1)
        sub_title = grids_or_wires[wg]
        PHS_2D_plot_bus(clusters, wg, limit, bins, sub_title, vmin, vmax)
    plt.tight_layout()
    return fig
