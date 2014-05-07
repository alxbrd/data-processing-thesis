'''
    Declares the parameters that are common among all the experiments.
'''

import csv
import numpy as np
import scipy as sp
import matplotlib.pyplot as plt
import matplotlib.lines as lines
from os import listdir
from os.path import isfile, join, exists
import tests
import utils

#
# Visualisation Parameters
#
indicators = 4                                          # Number of performance assessment indicators
indicators_names = ['Hypervolume Indicator ($I_{HV}$)', 'Generational Distance ($I_{GD}$)', 'Spread Indicator ($\Delta$)', 'Cardinality ($I_{C}$)']
digits = 3                                              # Number of digits for rounding the results
objectives = 3   
colors = ['blue', 'red', 'cyan', 'lightgreen', 'lightblue']
markers = ['.', 'x', '.', 'x']
linestyle = ['bo-', 'rx-', 'co-', 'gx-']
output_folder = "output/"