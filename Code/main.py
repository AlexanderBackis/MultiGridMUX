from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5 import uic
import sys
import os
import zipfile
import shutil
import numpy as np
import struct
import pandas as pd
import time
from contextlib import ExitStack

from cluster import cluster_data, save_data, load_data
from Plotting.PHS import PHS_1D_plot, PHS_2D_plot
from Plotting.Coincidences import (Coincidences_2D_plot, Coincidences_3D_plot,
                                   Coincidences_Front_Top_Side_plot)
from Plotting.Miscellaneous import ToF_histogram, Channels_plot, ADC_plot
from Plotting.HelpMessage import gethelp
from Plotting.HelperFunctions import get_ADC_to_Ch_dict

# =============================================================================
# Windows
# =============================================================================

class MainWindow(QMainWindow):
    def __init__(self, app, parent=None):
        super(MainWindow, self).__init__(parent)
        dir_name = os.path.dirname(__file__)
        title_screen_path = os.path.join(dir_name, '../Windows/mainwindow.ui')
        self.ui = uic.loadUi(title_screen_path, self)
        self.app = app
        self.measurement_time = 0
        self.data_sets = ''
        self.Clusters_20_layers = pd.DataFrame()
        self.Clusters_16_layers = pd.DataFrame()
        self.save_progress.close()
        self.load_progress.close()
        self.show()
        self.refresh_window()

    # =========================================================================
    # File handling
    # =========================================================================

    def cluster_action(self):
        # Declare time testing
        opening_time = 0
        clustering_time = 0
        append_time = 0
        # Declare parameters
        folder_path = str(QFileDialog.getExistingDirectory(self,
                                                           "Select Directory",
                                                           "../Data"))
        first_time = time.time()
        ADC_to_Ch_dict = get_ADC_to_Ch_dict()
        grid_di_20 = ADC_to_Ch_dict['20_layers']['Grids']
        grid_di_16 = ADC_to_Ch_dict['16_layers']['Grids']
        wire_di_20 = ADC_to_Ch_dict['20_layers']['Wires']
        wire_di_16 = ADC_to_Ch_dict['16_layers']['Wires']
        if folder_path != '':
            start_time = time.time()
            # Iterate through all files in folder
            file_names = [f for f in os.listdir(folder_path) if f[-4:] == '.bin']
            file_paths = append_folder_and_files(folder_path + '/', file_names)
            # Import all data to be clustered
            start_time = time.time()
            data_files = [None]*len(file_paths)
            size = 0
            # Import data
            for i, file_path in enumerate(file_paths):
                data_files[i] = np.fromfile(file_path, dtype=np.dtype('u4'))
                size += (len(data_files[i]) // 14)
            opening_time = (time.time() - start_time)
            print('Importing: %f [s]' % opening_time)
            # Declare masks
            start_time = time.time()
            TimeStampMask = 0x3FFFFFFF
            ADCMask = 0x00003FFF
            # Declare all vectors needed
            clusters = np.array([np.zeros([size], dtype=int),   # 0, wADC_m1_16
                                 np.zeros([size], dtype=int),   # 1, wADC_m2_16
                                 np.zeros([size], dtype=int),   # 4, wADC_Ch_m1_16
                                 np.zeros([size], dtype=int),   # 5, wADC_Ch_m2_16
                                 np.zeros([size], dtype=int),   # 8, wADC_m1_20
                                 np.zeros([size], dtype=int),   # 9, wADC_m2_20
                                 np.zeros([size], dtype=int),   # 10, wADC_Ch_m1_20
                                 np.zeros([size], dtype=int),   # 11, wADC_Ch_m2_20
                                 np.zeros([size], dtype=int),   # 2, gADC_m1
                                 np.zeros([size], dtype=int),   # 3, gADC_m2
                                 np.zeros([size], dtype=int),   # 6, gADC_Ch_m1
                                 np.zeros([size], dtype=int),   # 7, gADC_Ch_m2
                                 np.zeros([size], dtype=int)])  # 12, ToF
            start = 0
            for i, data_file in enumerate(data_files):
                length = len(data_file)//14
                matrix_T = np.reshape(data_file, (length, 14))
                matrix = np.transpose(matrix_T)
                clusters[0:12, start:(start+length)] = matrix[1:13, :] & ADCMask
                clusters[12, start:(start+length)] = matrix[13, :] & TimeStampMask
                start += length
            # Perform channel mapping
            wCh_m1_16 = pd.DataFrame({'a': clusters[4]})['a'].map(wire_di_16).values
            gCh_m1_16 = pd.DataFrame({'a': clusters[6]})['a'].map(grid_di_16).values
            gCh_m2_16 = pd.DataFrame({'a': clusters[7]})['a'].map(grid_di_16).values
            wCh_m1_20 = pd.DataFrame({'a': clusters[10]})['a'].map(wire_di_20).values
            gCh_m1_20 = pd.DataFrame({'a': clusters[6]})['a'].map(grid_di_20).values
            gCh_m2_20 = pd.DataFrame({'a': clusters[7]})['a'].map(grid_di_20).values
            # Create DataFrames
            self.Clusters_16_layers = pd.DataFrame({'wADC_m1': clusters[0],
                                                    'wADC_m2': clusters[1],
                                                    'wChADC_m1': clusters[4],
                                                    'wChADC_m2': clusters[5],
                                                    'wCh_m1': wCh_m1_16,
                                                    'gADC_m1': clusters[2],
                                                    'gADC_m2': clusters[3],
                                                    'gChADC_m1': clusters[6],
                                                    'gChADC_m2': clusters[7],
                                                    'gCh_m1': gCh_m1_16,
                                                    'gCh_m2': gCh_m2_16,
                                                    'ToF': clusters[12]})
            self.Clusters_20_layers = pd.DataFrame({'wADC_m1': clusters[8],
                                                    'wADC_m2': clusters[9],
                                                    'wChADC_m1': clusters[10],
                                                    'wChADC_m2': clusters[11],
                                                    'wCh_m1': wCh_m1_20,
                                                    'gADC_m1': clusters[2],
                                                    'gADC_m2': clusters[3],
                                                    'gChADC_m1': clusters[6],
                                                    'gChADC_m2': clusters[7],
                                                    'gCh_m1': gCh_m1_20,
                                                    'gCh_m2': gCh_m2_20,
                                                    'ToF': clusters[12]})
            clustering_time = (time.time() - start_time)
            print('Clustering: %f [s]' % clustering_time)
            start_time = time.time()
            # Add data set to list of data sets
            self.data_sets = folder_path.rsplit('/', 1)[-1]
            # Assign data set name
            self.data_sets_browser.setText(self.data_sets)
            self.update()
            self.update()
            self.app.processEvents()
            self.update()
            self.refresh_window()
            window_update_time = (time.time() - start_time)
            print('Window update: %f [s]' % window_update_time)
            #print(self.Clusters_20_layers)
        print('Total time')
        print((time.time() - first_time))

    def save_action(self):
        save_path = QFileDialog.getSaveFileName()[0]
        if save_path != '':
            save_data(save_path, self)

    def load_action(self):
        load_path = QFileDialog.getOpenFileName()[0]
        if load_path != '':
            load_data(load_path, self)

    # =========================================================================
    # Plotting
    # =========================================================================

    def PHS_1D_action(self):
        if self.data_sets != '':
            fig = PHS_1D_plot(self)
            fig.show()

    def PHS_2D_action(self):
        if self.data_sets != '':
            fig = PHS_2D_plot(self)
            fig.show()

    def ToF_action(self):
        if self.data_sets != '':
            fig = ToF_histogram(self)
            fig.show()

    def Channels_action(self):
        if self.data_sets != '':
            fig = Channels_plot(self)
            fig.show()

    def ADC_action(self):
        if self.data_sets != '':
            fig = ADC_plot(self)
            fig.show()

    def Coincidences_2D_action(self):
        if self.data_sets != '':
            fig = Coincidences_2D_plot(self)
            fig.show()

    def Coincidences_3D_action(self):
        if self.data_sets != '':
            Coincidences_3D_plot(self)

    def Coincidences_Front_Top_Side_action(self):
        if self.data_sets != '':
            fig = Coincidences_Front_Top_Side_plot(self)
            fig.show()

    def help_action(self):
        print("HELP!!!!")
        gethelp()


    # ========================================================================
    # Helper Functions
    # ========================================================================

    def setup_buttons(self):
        # File handling
        self.cluster_button.clicked.connect(self.cluster_action)
        self.save_button.clicked.connect(self.save_action)
        self.load_button.clicked.connect(self.load_action)
        # Plotting
        self.PHS_1D_button.clicked.connect(self.PHS_1D_action)
        self.PHS_2D_button.clicked.connect(self.PHS_2D_action)
        self.Coincidences_2D_button.clicked.connect(self.Coincidences_2D_action)
        self.Coincidences_3D_button.clicked.connect(self.Coincidences_3D_action)
        self.Coincidences_Front_Top_Side_button.clicked.connect(self.Coincidences_Front_Top_Side_action)
        self.ToF_button.clicked.connect(self.ToF_action)
        self.Channels_button.clicked.connect(self.Channels_action)
        self.ADC_button.clicked.connect(self.ADC_action)
        # Help
        self.help_button.clicked.connect(self.help_action)

    def refresh_window(self):
        self.app.processEvents()
        self.update()
        self.app.processEvents()
        self.update()
        self.app.processEvents()
        self.app.processEvents()
        self.app.processEvents()


# =============================================================================
# Helper Functions
# =============================================================================

def mkdir_p(mypath):
    '''Creates a directory. equivalent to using mkdir -p on the command line'''

    from errno import EEXIST
    from os import makedirs, path

    try:
        makedirs(mypath)
    except OSError as exc:
        if exc.errno == EEXIST and path.isdir(mypath):
            pass
        else:
            raise

def append_folder_and_files(folder, files):
    folder_vec = np.array(len(files)*[folder])
    return np.core.defchararray.add(folder_vec, files)

# =============================================================================
# Start GUI
# =============================================================================

app = QApplication(sys.argv)
main_window = MainWindow(app)
main_window.setAttribute(Qt.WA_DeleteOnClose, True)
main_window.setup_buttons()
sys.exit(app.exec_())

print('I am in master')
