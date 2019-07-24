# Multi-Grid Analysis: Mesytec Mux-32 and Mux-64 

Application for analysis of Multi-Grid data taken with the Mesytec Mux-32 and Mux-64 read-out system.
The program consists of a GUI Interface which allows the user to cluster and analyse data using different tools, such as:

- Event gating
- PHS (Cumulative or individual channel)
- Coincidences (2D and 3D)
- ToF
- Raw output visualization (Charge and Channel)

## Requisties
- Python3 (https://www.python.org/downloads/)
- Anaconda (https://www.anaconda.com/distribution/)

## Installation
Install dependencies:
```
conda install -c anaconda pyqt 
conda install -c plotly plotly
```

Clone the repository:
```
git clone https://github.com/AlexanderBackis/MultiGridMUX.git
```

## Execution
Navigate to MultiGridMUX->Code and enter:
```
python main.py
```
## Notes

The code requires two excel-documents to work:
- Grid_Wire_Channel_Mapping.xlsx
- Histogram_delimiters.xlsx

These can be found in the 'Tables'-folder in the repository, and the files can be manipulated according to the specific conditions of the measurement.
