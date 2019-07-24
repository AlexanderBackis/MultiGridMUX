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
