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


def Coincidences_2D_plot(clusters, window):
    # Declare parameters (added with condition if empty array)
    data_sets = window.data_sets.splitlines()[0]
    # Intial filter
    clusters = filter_clusters(clusters, window)
    # Plot data
    fig = plt.figure()
    plt.title('Coincident events (2D)\nData set(s): %s' % data_sets)
    plt.hist2d(clusters.wCh_1, clusters.gCh_1, bins=[80, 12],
               range=[[-0.5, 79.5], [-0.5, 11.5]],
               norm=LogNorm(), cmap='jet')
    plt.xlabel('Wire [Channel number]')
    plt.ylabel('Grid [Channel number]')
    plt.colorbar()
    return fig


# =============================================================================
# Coincidence Histogram (3D)
# =============================================================================

def Coincidences_3D_plot(df, window):
    # Intial filter
    df = filter_clusters(df, window)
    # Declare max and min count
    min_count = 0
    max_count = np.inf
    # Initiate 'voxel_id -> (x, y, z)'-mapping
    MG24_ch_to_coord = get_MG24_to_XYZ_mapping()
    # Calculate 3D histogram
    H, edges = np.histogramdd(df[['wCh_1', 'gCh_1']].values,
                              bins=(80, 13),
                              range=((0, 80), (0, 13))
                              )
    # Insert results into an array
    hist = [[], [], [], []]
    loc = 0
    labels = []
    for wCh in range(0, 80):
        for gCh in range(0, 13):
            over_min = H[wCh, gCh] > min_count
            under_max = H[wCh, gCh] <= max_count
            if over_min and under_max:
                coord = MG24_ch_to_coord[gCh, wCh]
                hist[0].append(coord['x'])
                hist[1].append(coord['y'])
                hist[2].append(coord['z'])
                hist[3].append(H[wCh, gCh])
                loc += 1
                labels.append('Wire Channel: ' + str(wCh) + '<br>'
                              + 'Grid Channel: ' + str(gCh) + '<br>'
                              + 'Counts: ' + str(H[wCh, gCh])
                              )
    # Produce 3D histogram plot
    MG_3D_trace = go.Scatter3d(x=hist[0],
                               y=hist[1],
                               z=hist[2],
                               mode='markers',
                               marker=dict(size=20,
                                           color=np.log10(hist[3]),
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
# Helper Functions
# =============================================================================

def get_MG24_to_XYZ_mapping():
    # Declare voxelspacing in [mm]
    WireSpacing = 10
    LayerSpacing = 23.5
    GridSpacing = 23.5
    # Iterate over all channels and create mapping
    MG24_ch_to_coord = np.empty((13, 80), dtype='object')
    for gCh in np.arange(0, 13, 1):
        for wCh in np.arange(0, 80, 1):
            x = (wCh // 20) * LayerSpacing
            y = gCh * GridSpacing
            z = (wCh % 20) * WireSpacing
            MG24_ch_to_coord[gCh, wCh] = {'x': x, 'y': y, 'z': z}
    return MG24_ch_to_coord












