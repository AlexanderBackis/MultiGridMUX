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

from cluster import cluster_data
from Plotting.PHS import PHS_1D_plot
from Plotting.Miscellaneous import Channels_plot, ToF_histogram

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
        self.Clusters = pd.DataFrame()
        self.cluster_progress.close()
        self.save_progress.close()
        self.load_progress.close()
        self.show()
        self.refresh_window()

    # =========================================================================
    # Actions
    # =========================================================================

    def cluster_action(self):
        # Declare parameters
        dirname = os.path.dirname(__file__)
        unzipped_folder_path = os.path.join(dirname, '../temp_folder/')
        zipped_folder_paths = QFileDialog.getOpenFileNames()[0]
        if len(zipped_folder_paths) > 0:
            # Initiate loading bar
            self.cluster_progress.show()
            self.cluster_progress.setValue(0)
            self.refresh_window()
            # Iterate through all zipped folders
            for i, zipped_folder_path in enumerate(zipped_folder_paths):
                # Extract files from zipped file into temporary folder
                mkdir_p(unzipped_folder_path)
                with zipfile.ZipFile(zipped_folder_path, "r") as zip_ref:
                    zip_ref.extractall(unzipped_folder_path)
                # Iterate through all files in unzipped folder and cluster
                file_names = os.listdir(unzipped_folder_path)
                file_paths = append_folder_and_files(unzipped_folder_path,
                                                     file_names)
                for j, file_path in enumerate(file_paths):
                    # Import data
                    with open(file_path, mode='rb') as bin_file:
                        content = bin_file.read()
                        data = struct.unpack('I' * (len(content)//4), content)
                    # Cluster data
                    self.Clusters = self.Clusters.append(cluster_data(data))
                    # Update loading bar
                    if j % 20 == 1:
                        progress = ((i/len(zipped_folder_paths))*100
                                    + (j/(len(zipped_folder_paths)
                                       * len(file_path)))*100)
                        self.cluster_progress.setValue(progress)
                        self.refresh_window()
                shutil.rmtree(unzipped_folder_path, ignore_errors=True)
                # Add data set to list of data sets
                self.data_sets += zipped_folder_path.rsplit('/', 1)[-1]
                if len(zipped_folder_paths) > 1:
                    self.data_sets += '\n'
            # Close down loading bar and assign data set name
            self.cluster_progress.close()
            self.data_sets_browser.setText(self.data_sets)
            self.refresh_window()

    def PHS_1D_action(self):
        if self.data_sets != '':
            fig = PHS_1D_plot(self.Clusters, self)
            fig.show()

    def Channels_action(self):
        if self.data_sets != '':
            fig = Channels_plot(self.Clusters, self)
            fig.show()

    def ToF_action(self):
        if self.data_sets != '':
            fig = ToF_histogram(self.Clusters, self)
            fig.show()


    # ========================================================================
    # Helper Functions
    # ========================================================================

    def setup_buttons(self):
        # File handling
        self.cluster_button.clicked.connect(self.cluster_action)
        # Plotting
        self.PHS_1D_button.clicked.connect(self.PHS_1D_action)
        self.Channels_button.clicked.connect(self.Channels_action)
        self.ToF_button.clicked.connect(self.ToF_action)
        # Miscellaneous
        self.toogle_MG_24_MG_CNCS()

    def refresh_window(self):
        self.app.processEvents()
        self.update()
        self.app.processEvents()
        self.update()

    def toogle_MG_24_MG_CNCS(self):
        self.MG_24.toggled.connect(
            lambda checked: checked and self.MG_CNCS.setChecked(False))
        self.MG_CNCS.toggled.connect(
            lambda checked: checked and self.MG_24.setChecked(False))


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