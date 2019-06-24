import numpy as np

# =============================================================================
# Filter
# =============================================================================

def filter_clusters(clusters, window):
    # Declare parameters
    parameters = {'wADC_1': [window.wADC_min.value(),
                             window.wADC_max.value(),
                             window.wADC_filter.isChecked()],
                  'gADC_1': [window.gADC_min.value(),
                             window.gADC_max.value(),
                             window.gADC_filter.isChecked()],
                  'ToF':  [float(window.ToF_min.text()),
                           float(window.ToF_max.text()),
                           window.ToF_filter.isChecked()],
                  'wCh_1': [window.wCh_min.value(),
                            window.wCh_max.value(),
                            window.wCh_filter.isChecked()],
                  'gCh_1': [window.gCh_min.value(),
                            window.gCh_max.value(),
                            window.gCh_filter.isChecked()],
                  }
    # Only include the filters that we want to use
    ce_red = clusters
    for par, (min_val, max_val, filter_on) in parameters.items():
        if filter_on:
            ce_red = ce_red[(ce_red[par] >= min_val) & (ce_red[par] <= max_val)]
    return ce_red
