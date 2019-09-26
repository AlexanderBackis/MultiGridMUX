import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
import plotly as py
import numpy as np
import plotly.graph_objs as go
import pandas as pd
import plotly.io as pio
import os
from Plotting.HelperFunctions import import_delimiter_table, filter_clusters


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

# ============================================================================
# Channels rates plot
# ============================================================================

def Channels_rates_plot(window, measurement_time):
    """plots neutron event rate for each channel"""
    def channel_rates_plot_bus(events, subtitle, typeCh, name, wires):
        plt.xlabel('grid channel')
        plt.ylabel('Rate of total counts')
        plt.grid(True, which='major', zorder=0)
        plt.grid(True, which='minor', linestyle='--', zorder=0)
        plt.title("Grid rates")
        #print("Grid channel \t rate")
        gChs = []
        g_rates = []
        if typeCh == 'gCh':
            for gCh in np.arange(0, 12, 1):
                counts = 0
                vals = clusters_dict[name]['g'].values
                for val in vals:
                    if val == gCh:
                        counts += 1
                rate = counts/((measurement_time))
                gChs.append(gCh)
                g_rates.append(rate)
                #print(gCh, "\t", rate, "Hz")
            plt.scatter(gChs, g_rates, color="darkorange", zorder=2)
            plt.title(sub_title)

        #print("Wire channel \t rate")
        wChs = []
        w_rates = []
        if typeCh == 'wCh':
            for wCh in np.arange(0, wires, 1):
                counts = 0
                vals = clusters_dict[name]['w'].values
                for val in vals:
                    if val == wCh:
                        counts += 1
                rate = counts/((measurement_time))
                wChs.append(wCh)
                w_rates.append(rate)
                #print(wCh, "\t", rate, "Hz")
            plt.scatter(wChs, w_rates, color="crimson", zorder=2)
            plt.title(sub_title)

    # Import data
    ce_20 = window.Clusters_20_layers
    ce_16 = window.Clusters_16_layers
    # Filter
    ce_red_20 = filter_clusters(ce_20, window)
    ce_red_16 = filter_clusters(ce_16, window)
    clusters_20 = ce_red_20#.shape[0]
    clusters_16 = ce_red_16#.shape[0]
    clusters_vec = [clusters_20, clusters_16]
    clusters_dict = {'ce_20': {'w': None, 'g': None},
                     'ce_16': {'w': None, 'g': None}}
    # Select grids with highest collected charge
    for clusters, name in zip(clusters_vec, ['ce_20', 'ce_16']):
        channels_g1 = clusters[clusters['gADC_m1'] > clusters['gADC_m2']]['gCh_m1']
        channels_w1 = clusters[clusters['gADC_m1'] > clusters['gADC_m2']]['wCh_m1']
        channels_g2 = clusters[clusters['gADC_m1'] <= clusters['gADC_m2']]['gCh_m2']
        channels_w2 = clusters[clusters['gADC_m1'] <= clusters['gADC_m2']]['wCh_m1']
        clusters_dict[name]['g'] = channels_g1.append(channels_g2)
        clusters_dict[name]['w'] = channels_w1.append(channels_w2)

    typeChs = ['gCh', 'wCh']
    grids_or_wires = {'wCh': 'Wires', 'gCh': 'Grids'}
    # plot
    fig = plt.figure()
    fig.set_figheight(5)
    fig.set_figwidth(10)
    plt.suptitle('Total rate per channel \n%s' % window.data_sets.splitlines()[0])

    # for 20 layers
    for i, typeCh in enumerate(typeChs):
        sub_title = "%s -- 20 layers" % grids_or_wires[typeCh]
        wires = 80
        name = 'ce_20'
        plt.subplot(2,2,i+1)
        channel_rates_plot_bus(clusters_20, sub_title, typeCh, name, wires)

    # for 16 layers
    for i, typeCh in enumerate(typeChs):
        sub_title = "%s -- 16 layers" % grids_or_wires[typeCh]
        name = 'ce_16'
        plt.subplot(2,2,i+3)
        wires = 64
        channel_rates_plot_bus(clusters_16, sub_title, typeCh, name, wires)

    plt.subplots_adjust(left=0.1, right=0.98, top=0.86, bottom=0.09, wspace=0.25, hspace=0.45)
    return fig
