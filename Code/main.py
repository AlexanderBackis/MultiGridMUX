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

from cluster import cluster_data, save_data, load_data
from Plotting.PHS import PHS_1D_plot, PHS_2D_plot
from Plotting.Coincidences import Coincidences_2D_plot, Coincidences_3D_plot
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
    """
    def cluster_action(self):
        # Declare parameters
        file_paths = QFileDialog.getOpenFileNames()[0]
        ADC_to_Ch_dict = get_ADC_to_Ch_dict()
        if len(file_paths) > 0:
            # Iterate through all files
            for i, file_path in enumerate(file_paths):
                # Import data
                with open(file_path, mode='rb') as bin_file:
                    content = bin_file.read()
                    data = struct.unpack('I' * (len(content)//(4)), content)
                # Cluster data
                subset_clusters = cluster_data(data, ADC_to_Ch_dict, self)
                subset_20_layers, subset_16_layers = subset_clusters
                self.Clusters_20_layers = self.Clusters_20_layers.append(subset_20_layers)
                self.Clusters_16_layers = self.Clusters_20_layers.append(subset_16_layers)
                print(str(i) + '/' + str(len(file_paths)))
            # Add data set name
            self.data_sets += file_path.rsplit('/', 1)[-1]
            self.data_sets_browser.setText(self.data_sets)
        """

    def cluster_action(self):
        # Declare parameters
        folder_path = str(QFileDialog.getExistingDirectory(self, "Select Directory"))
        ADC_to_Ch_dict = get_ADC_to_Ch_dict()
        if folder_path != '':
            # Iterate through all files in folder
            file_names = [f for f in os.listdir(folder_path) if f[-4:] == '.bin']
            file_paths = append_folder_and_files(folder_path + '/', file_names)
            for file_path in file_paths:
                # Import data
                with open(file_path, mode='rb') as bin_file:
                    content = bin_file.read()
                    data = struct.unpack('I' * (len(content)//4), content)
                # Cluster data
                subset_clusters = cluster_data(data, ADC_to_Ch_dict, self)
                subset_20_layers, subset_16_layers = subset_clusters
                self.Clusters_20_layers = self.Clusters_20_layers.append(subset_20_layers)
                self.Clusters_16_layers = self.Clusters_16_layers.append(subset_16_layers)
            # Add data set to list of data sets
            self.data_sets += folder_path.rsplit('/', 1)[-1]
            # Assign data set name
            self.data_sets_browser.setText(self.data_sets)
            self.update()
            self.update()
            self.app.processEvents()
            self.update()
            self.refresh_window()

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
            fig = PHS_1D_plot(self.Clusters, self)
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

    def help_action(self):
        print("HELP!!!!")
        gethelp()
    """
    def select_module_action(self):
        if (self.module_button_16.isChecked() == True and self.module_button_20.isChecked() == True):
            print("selecting both modules")
        elif self.module_button_16.isChecked() == True:
            print("selecting module 1, 16 by 4")
        elif self.module_button_20.isChecked():
            print("selecting module 2, 20 by 4") == True
    """

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
