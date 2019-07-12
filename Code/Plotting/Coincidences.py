import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
import plotly as py
import numpy as np
import plotly.graph_objs as go
import pandas as pd
import plotly.io as pio
import os
from Plotting.HelperFunctions import filter_clusters

# =============================================================================
# Coincidence Histogram (2D)
# =============================================================================


def Coincidences_2D_plot(window):
    # Declare parameters (added with condition if empty array)
    data_sets = window.data_sets.splitlines()[0]
    df_20 = window.Clusters_20_layers
    df_16 = window.Clusters_16_layers
    # Intial filter
    clusters_20 = df_20 #filter_clusters(df_20, window)
    clusters_16 = df_16 #filter_clusters(df_16, window)
    #print(clusters_20)
    clusters_vec = [clusters_20, clusters_16]
    clusters_dict = {'ce_20': {'w': None, 'g': None},
                     'ce_16': {'w': None, 'g': None}}
    # Select grids with highest collected charge
    for clusters, name in zip(clusters_vec, ['ce_20', 'ce_16']):
        #print('gADC_m1')
        #print(clusters['gADC_m1'])
        #print('gADC_m2')
        #print(clusters['gADC_m2'])
        #print('gCh_m1')
        #print(clusters['gCh_m1'])
        #print('gCh_2')
        #print(clusters['gCh_m2'])
        #print('wADC_m1')
        #print(clusters['wADC_m1'])
        #print('wCh_m1')
        #print(clusters['gCh_m1'])
        channels_g1 = clusters[clusters['gADC_m1'] > clusters['gADC_m2']]['gCh_m1']
        channels_w1 = clusters[clusters['gADC_m1'] > clusters['gADC_m2']]['wCh_m1']
        channels_g2 = clusters[clusters['gADC_m1'] <= clusters['gADC_m2']]['gCh_m2']
        channels_w2 = clusters[clusters['gADC_m1'] <= clusters['gADC_m2']]['wCh_m1']
        clusters_dict[name]['g'] = channels_g1.append(channels_g2)
        clusters_dict[name]['w'] = channels_w1.append(channels_w2)

    fig = plt.figure()
    plt.subplot(1, 2, 1)
    plt.title('16 layers')

    hist_all = plt.hist2d(clusters_dict['ce_16']['w'],
                          clusters_dict['ce_16']['g'],
                          bins=[64, 12],
                          range=[[-0.5, 63.5], [-0.5, 11.5]],
                          norm=LogNorm(), cmap='jet')
    hist = hist_all[0]
    els = []
    for row in hist:
        for i in row:
            els.append(i)
    max_16 = max(els)
    min_16 = min(els)
    if min_16 == 0:
        min_16 = 1
    plt.xlabel('Wires')
    plt.ylabel('Grids')
    plt.colorbar()
    plt.subplot(1, 2, 2)
    plt.title('20 layers')
    plt.hist2d(clusters_dict['ce_20']['w'], clusters_dict['ce_20']['g'],
               bins=[80, 12],
               range=[[-0.5, 79.5], [-0.5, 11.5]],
               norm=LogNorm(), cmap='jet', vmin=min_16, vmax=max_16)
    print("Using color axis from 16-layers plot also for 20-layers plot")
    plt.xlabel('Wires')
    plt.ylabel('Grids')
    fig.suptitle('Coincident events (2D) -- Data set(s): %s' % data_sets)
    plt.colorbar()
    plt.tight_layout()

    return fig


# =============================================================================
# Coincidence Histogram (3D)
# =============================================================================

def Coincidences_3D_plot(window):
    # Intial filter
    #df = filter_clusters(df, window)
    df_20 = window.Clusters_20_layers
    df_16 = window.Clusters_16_layers
    #print(df_20[['wCh_m1', 'gCh_m1']])
    # Intial filter
    clusters_20 = filter_clusters(df_20, window)
    clusters_16 = filter_clusters(df_16, window)
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

    # Declare max and min count
    min_count = 0
    max_count = np.inf
    # Initiate 'voxel_id -> (x, y, z)'-mapping
    MG24_ch_to_coord_20, MG24_ch_to_coord_16 = get_MG24_to_XYZ_mapping(window)
    #print(MG24_ch_to_coord_16)

    #print("20 wires", clusters_dict['ce_20']['w'].values)
    #print("20 grids", clusters_dict['ce_20']['g'].values)
    ##wires = clusters_dict['ce_20']['w']
    #print(np.array([clusters_dict['ce_20']['w'].values,
    #                clusters_dict['ce_20']['g'].values]))

    # Calculate 3D histogram
    H_20, edges_20 = np.histogramdd((clusters_dict['ce_20']['w'].values,
                                     clusters_dict['ce_20']['g'].values),
                              bins=(80, 13),
                              range=((0, 80), (0, 13)))

    # Insert results into an array
    hist_20 = [[], [], [], []]
    loc_20 = 0
    labels_20 = []
    for wCh in range(0, 80):
        for gCh in range(0, 13):
            over_min = H_20[wCh, gCh] > min_count
            under_max = H_20[wCh, gCh] <= max_count
            if over_min and under_max:
                coord = MG24_ch_to_coord_20[gCh, wCh]
                hist_20[0].append(coord['x'])
                hist_20[1].append(coord['y'])
                hist_20[2].append(coord['z'])
                hist_20[3].append(H_20[wCh, gCh])
                loc_20 += 1
                labels_20.append('Wire Channel: ' + str(wCh) + '<br>'
                              + 'Grid Channel: ' + str(gCh) + '<br>'
                              + 'Counts: ' + str(H_20[wCh, gCh])
                              )
    # for 16 layers
    H_16, edges_16 = np.histogramdd((clusters_dict['ce_16']['w'].values,
                                     clusters_dict['ce_16']['g'].values),
                              bins=(64, 13),
                              range=((0, 64), (0, 13))
                              )

    # Insert results into an array
    hist_16 = [[], [], [], []]
    loc_16 = 0
    labels_16 = []
    for wCh in range(0, 64):
        for gCh in range(0, 13):
            over_min = H_16[wCh, gCh] > min_count
            under_max = H_16[wCh, gCh] <= max_count
            if over_min and under_max:
                coord = MG24_ch_to_coord_16[gCh, wCh]
                hist_16[0].append(coord['x'])
                hist_16[1].append(coord['y'])
                hist_16[2].append(coord['z'])
                hist_16[3].append(H_16[wCh, gCh])
                loc_16 += 1
                labels_16.append('Wire Channel: ' + str(wCh) + '<br>'
                              + 'Grid Channel: ' + str(gCh) + '<br>'
                              + 'Counts: ' + str(H_16[wCh, gCh])
                              )

    #print("hist20", hist_20[3])
    #print("hist16", hist_16[3])


    labels = []
    labels.extend(labels_20)
    labels.extend(labels_16)

    # Produce 3D histogram plot
    hist = [[], [], [], []]
    hist_x_offset = [i + 100 for i in hist_20[0]]
    hist_z_offset = [i +  40 for i in hist_16[2]]
    hist[0].extend(hist_x_offset)
    hist[0].extend(hist_16[0])
    hist[1].extend(hist_20[1])
    hist[1].extend(hist_16[1])
    hist[2].extend(hist_20[2])
    hist[2].extend(hist_z_offset)
    hist[3].extend(hist_20[3])
    hist[3].extend(hist_16[3])

    #print(hist_20[0])
    #print("hist0", hist[0])
    #print("hist1", hist[1])
    #print("hist2", hist[2])
    #print("hist3", hist[3])
    MG_3D_trace = go.Scatter3d(x=hist[0],
                               y=hist[1],
                               z=hist[2],
                               mode='markers',
                               marker=dict(size=20,
                                           color=(np.log10(hist[3])),
                                           colorscale='Jet',
                                           opacity=1,
                                           colorbar=dict(thickness=20,
                                                         title='log10(counts)'
                                                         ),
                                           ),
                               text=labels,
                               name='Multi-Grid',
                               scene='scene1'
                               )
    # Introduce figure and put everything together
    fig = py.tools.make_subplots(rows=1, cols=1,
                                 specs=[[{'is_3d': True}]]
                                 )
    # Insert histogram
    fig.append_trace(MG_3D_trace, 1, 1)
    # Assign layout with axis labels, title and camera angle
    fig['layout']['scene1']['xaxis'].update(title='x [mm]')
    fig['layout']['scene1']['yaxis'].update(title='y [mm]')
    fig['layout']['scene1']['zaxis'].update(title='z [mm]')
    fig['layout'].update(title='Coincidences (3D)')
    fig.layout.showlegend = False
    # If in plot He3-tubes histogram, return traces, else save HTML and plot
    py.offline.plot(fig,
                    filename='../Results/Ce3Dhistogram.html',
                    auto_open=True)
    #pio.write_image(fig, '../Results/HTML_files/Ce3Dhistogram.pdf')


# =============================================================================
# Coincidence Histogram (Front, Top, Side)
# =============================================================================

def Coincidences_Front_Top_Side_plot(window):
    def plot_front(wires, grids, layers, vmin, vmax):
        plt.hist2d(wires // layers, grids, bins=[4, 12],
                   range=[[-0.5, 3.5], [-0.5, 11.5]], norm=LogNorm(),
                   cmap='jet', vmin=vmin, vmax=vmax)
        plt.title('Front view (%d layers)' % layers)
        plt.xlabel('Row')
        plt.ylabel('Grid')
        plt.colorbar()
    def plot_top(wires, grids, layers, vmin, vmax):
        plt.hist2d(wires // layers, wires % layers, bins=[4, layers],
                   range=[[-0.5, 3.5], [-0.5, layers-0.5]], norm=LogNorm(),
                   cmap='jet', vmin=vmin, vmax=vmax)
        plt.title('Top view (%d layers)' % layers)
        plt.xlabel('Row')
        plt.ylabel('Layer')
        plt.colorbar()
    def plot_side(wires, grids, layers, vmin, vmax):
        plt.hist2d(wires % layers, grids, bins=[layers, 12],
                   range=[[-0.5, layers-0.5], [-0.5, 11.5]], norm=LogNorm(),
                   cmap='jet', vmin=vmin, vmax=vmax)
        plt.title('Side view (%d layers)' % layers)
        plt.xlabel('Layer')
        plt.ylabel('Grid')
        plt.colorbar()

    # Declare parameters (added with condition if empty array)
    data_sets = window.data_sets.splitlines()[0]
    df_20 = window.Clusters_20_layers
    df_16 = window.Clusters_16_layers
    clusters_vec = [df_20, df_16]
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
    wires_20 = clusters_dict['ce_20']['w'].values
    grids_20 = clusters_dict['ce_20']['g'].values
    wires_16 = clusters_dict['ce_16']['w'].values
    grids_16 = clusters_dict['ce_16']['g'].values

    if len(wires_20) != 0:
        vmin = len(wires_20) // 100
        vmax = len(wires_20) // 10
    else:
        vmin = 1
        vmax = 1
    vmin = None
    vmax = None
    fig = plt.figure()
    fig.set_figheight(8)
    fig.set_figwidth(14)
    #fig.suptitle('Coincidences - Front, Top, Side')
    plt.subplot(2, 3, 1)
    plot_front(wires_20, grids_20, 20, vmin, vmax)
    plt.subplot(2, 3, 2)
    plot_top(wires_20, grids_20, 20, vmin, vmax)
    plt.subplot(2, 3, 3)
    plot_side(wires_20, grids_20, 20, vmin, vmax)
    plt.subplot(2, 3, 4)
    plot_front(wires_16, grids_16, 16, vmin, vmax)
    plt.subplot(2, 3, 5)
    plot_top(wires_16, grids_16, 16, vmin, vmax)
    plt.subplot(2, 3, 6)
    plot_side(wires_16, grids_16, 16, vmin, vmax)
    plt.tight_layout()
    return fig







# =============================================================================
# Coincidence Histogram - Side
# =============================================================================


def plot_2D_Side(bus_vec, df, fig, number_of_detectors, vmin, vmax):

    df_tot = pd.DataFrame()
    for i, bus in enumerate(bus_vec):
        df_clu = df[df.Bus == bus]
        df_clu['gCh'] += (-80 + 1)
        df_tot = pd.concat([df_tot, df_clu])
    h, *_ = plt.hist2d(df_tot['wCh'] % 20 + 1, df_tot['gCh'],
                       bins=[20, 40],
                       range=[[0.5, 20.5], [0.5, 40.5]],
                       norm=LogNorm(),
                       cmap='jet', vmin=vmin, vmax=vmax
                       )

    title = 'Side view'
    xlabel = 'Wire'
    ylabel = 'Grid'
    fig = stylize(fig, xlabel, ylabel, title=title, colorbar=True)
    plt.colorbar()
    return fig, h



# =============================================================================
# Helper Functions
# =============================================================================

def get_MG24_to_XYZ_mapping(window):
    # Declare voxelspacing in [mm]
    WireSpacing = 10
    LayerSpacing = 23.5
    GridSpacing = 23.5
    # Iterate over all channels and create mapping
    #grid_20_layers = select_grid()[0]
    #grid_16_layers = select_grid()[1]
    #if whichgrid == "layers_20":
    MG24_ch_to_coord_20 = np.empty((13, 80), dtype='object')
    for gCh in np.arange(0, 13, 1):
        for wCh in np.arange(0, 80, 1):
            x = (wCh // 20) * LayerSpacing
            y = gCh * GridSpacing
            z = (wCh % 20) * WireSpacing
            MG24_ch_to_coord_20[gCh, wCh] = {'x': x, 'y': y, 'z': z}
    #elif whichgrid == "layers_16":
    MG24_ch_to_coord_16 = np.empty((13, 64), dtype='object')
    for gCh in np.arange(0, 13, 1):
        for wCh in np.arange(0, 64, 1):
            x = (wCh // 16) * LayerSpacing
            y = gCh * GridSpacing
            z = (wCh % 16) * WireSpacing
            MG24_ch_to_coord_16[gCh, wCh] = {'x': x, 'y': y, 'z': z}
    return MG24_ch_to_coord_20, MG24_ch_to_coord_16
