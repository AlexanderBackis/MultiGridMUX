import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd
from matplotlib.colors import LogNorm
from Plotting.HelperFunctions import filter_clusters


# ============================================================================
# PHS (1D)
# ============================================================================


def PHS_1D_plot(window):
    def PHS_1D_plot_bus(clusters, typeCh, sub_title, number_bins):
        # Plot
        plt.title(sub_title)
        plt.xlabel('Collected charge [ADC channels]')
        plt.ylabel('Counts')
        plt.grid(True, which='major', zorder=0)
        plt.grid(True, which='minor', linestyle='--', zorder=0)
        plt.yscale('log')
        if wg == 'g':
            adcs = clusters['gADC_m1'].append(clusters['gADC_m2'])
        else:
            adcs = clusters['wADC_m1']
        plt.hist(adcs, bins=number_bins, range=[0, 4095], histtype='step',
                 color='black', zorder=5)
    # Import data
    df_20 = window.Clusters_20_layers
    df_16 = window.Clusters_16_layers
    # Intial filter
    clusters_20 = filter_clusters(df_20, window)
    clusters_16 = filter_clusters(df_16, window)

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

    # Plot figure for 20 layers
    for i, wg in enumerate(wg_list):
        plt.subplot(2, 2, i+1)
        sub_title = grids_or_wires[wg] + " -- 20 layers"
        PHS_1D_plot_bus(clusters_20, wg, sub_title, number_bins)
    plt.tight_layout()

    # Plot figure for 16 layers
    for i, wg in enumerate(wg_list):
        plt.subplot(2, 2, i+3)
        sub_title = grids_or_wires[wg] + " -- 16 layers"
        PHS_1D_plot_bus(clusters_16, wg, sub_title, number_bins)
    plt.tight_layout()

    return fig

# =============================================================================
# PHS (2D)
# =============================================================================


def PHS_2D_plot(window):
    def PHS_2D_plot_bus(clusters, wg, limit, bins, sub_title, vmin, vmax):
        plt.xlabel('Channel')
        plt.ylabel('Charge [ADC channels]')
        plt.title(sub_title)
        if wg == 'g':
            channels = clusters['gCh_m1'].append(clusters['gCh_m2'])
            adcs = clusters['gADC_m1'].append(clusters['gADC_m2'])
        else:
            channels = clusters['wCh_m1']
            adcs = clusters['wADC_m1']
        plt.hist2d(channels, adcs,
                   bins=[bins, 120],
                   range=[limit, [0, 4095]], norm=LogNorm(),
                   #vmin=vmin, vmax=vmax,
                   cmap='jet')
        plt.colorbar()

    # Import data
    df_20 = window.Clusters_20_layers
    df_16 = window.Clusters_16_layers
    # Intial filter
    clusters_20 = filter_clusters(df_20, window)
    clusters_16 = filter_clusters(df_16, window)

    # Declare parameters
    wg_list = ['w', 'g']
    limits_16 = [[-0.5, 63.5], [-0.5, 11.5]]
    bins_16   = [64, 12]
    limits_20 = [[-0.5, 79.5], [-0.5, 11.5]]
    bins_20   = [80, 12]
    grids_or_wires = {'w': 'Wires', 'g': 'Grids'}

    # Prepare figure
    fig = plt.figure()
    title = 'PHS (2D) - MG\n(%s, ...)' % window.data_sets.splitlines()[0]
    fig.suptitle(title, x=0.5, y=1.03)
    vmin = 1
    vmax_16 = clusters_16.shape[0] // 1000 + 100
    vmax_20 = clusters_20.shape[0] // 1000 + 100
    fig.set_figheight(4)
    fig.set_figwidth(10)
    # Plot figure
    for i, (wg, limit_16, bins_16) in enumerate(zip(wg_list, limits_16, bins_16)):
        # Filter events based on wires or grids
        plt.subplot(2, 2, i+1)
        sub_title = grids_or_wires[wg] + " -- 16 layers"
        PHS_2D_plot_bus(clusters_16, wg, limit_16, bins_16, sub_title, vmin, vmax_16)
    plt.tight_layout()

    for i, (wg, limit_20, bins_20) in enumerate(zip(wg_list, limits_20, bins_20)):
        # Filter events based on wires or grids
        plt.subplot(2, 2, i+3)
        sub_title = grids_or_wires[wg] + " -- 20 layers"
        PHS_2D_plot_bus(clusters_20, wg, limit_20, bins_20, sub_title, vmin, vmax_20)
    plt.tight_layout()

    return fig

# =============================================================================
# PHS (Individual Channels)
# =============================================================================

def PHS_Individual_plot(window):
    # Import data
    df_20 = window.Clusters_20_layers
    df_16 = window.Clusters_16_layers
    # Intial filter
    clusters_16 = filter_clusters(df_16, window)
    clusters_20 = filter_clusters(df_20, window)
    # Declare parameters
    clusters_vec = [clusters_16, clusters_20]
    detectors = ['16_layers', '20_layers']
    layers_vec = [16, 20]
    dir_name = os.path.dirname(__file__)
    folder_path = os.path.join(dir_name, '../../Results/PHS/')
    number_bins = int(window.phsBins.text())
    # Save all PHS
    for clusters, detector, layers in zip(clusters_vec, detectors, layers_vec):
        # Save wires PHS
        for wCh in np.arange(0, layers*4, 1):
            print('%s, Wires: %d/%d' % (detector, wCh, layers*4-1))
            # Get ADC values
            adcs = clusters[clusters.wCh_m1 == wCh]['wADC_m1']
            # Plot
            fig = plt.figure()
            plt.hist(adcs, bins=number_bins, range=[0, 4095], histtype='step',
                     color='black', zorder=5)
            plt.grid(True, which='major', zorder=0)
            plt.grid(True, which='minor', linestyle='--', zorder=0)
            plt.xlabel('Collected charge [ADC channels]')
            plt.ylabel('Counts')
            plt.title('PHS wires - Channel %d\nData set: %s' % (wCh, window.data_sets))
            # Save
            output_path = '%s/%s/Wires/Channel_%d.pdf' % (folder_path, detector, wCh)
            fig.savefig(output_path, bbox_inches='tight')
            plt.close()
        # Save grids PHS
        for gCh in np.arange(0, 12, 1):
            print('%s, Grids: %d/11' % (detector, gCh))
            # Get ADC values
            adcs_1 = clusters[clusters.gCh_m1 == gCh]['gADC_m1']
            adcs_2 = clusters[clusters.gCh_m2 == gCh]['gADC_m2']
            adcs = adcs_1.append(adcs_2)
            # Plot
            fig = plt.figure()
            plt.hist(adcs, bins=number_bins, range=[0, 4095], histtype='step',
                     color='black', zorder=5)
            plt.grid(True, which='major', zorder=0)
            plt.grid(True, which='minor', linestyle='--', zorder=0)
            plt.xlabel('Collected charge [ADC channels]')
            plt.ylabel('Counts')
            plt.title('PHS grids - Channel %d\nData set: %s' % (gCh, window.data_sets))
            # Save
            output_path = '%s/%s/Grids/Channel_%d.pdf' % (folder_path, detector, gCh)
            fig.savefig(output_path, bbox_inches='tight')
            plt.close()
