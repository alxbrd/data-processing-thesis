import csv
import numpy as np
import scipy as sp
import estimating
import matplotlib.pyplot as plt
import matplotlib.lines as lines
import plotting
from os import listdir
from os.path import isfile, join, exists

def find_final_generation(run, model, function, algorithm, folder):
    '''
    This method finds the maximum number of generation achived by an experimental run.
    
    Args:
        run: The total number of runs of the experiments.
        model: The composition model used for the experiments (Centralised or Decentralised).
        function: The fitness function(s) used in the experiments (Expensive or Surrogate).
        algorithm: The optimisation algorithm used (Random Search or MOEA).
        folder: The folder of the experiments.
        
    Returns:
        The maximum number of generation achived by an experimental run.
    '''
    
    dir_name = folder + str(run) + "/" + str(model) + "/" + str(function) + "/" + str(algorithm) + "/Results/"
    
    files = [ f for f in listdir(dir_name) if isfile(join(dir_name,f)) ]
    
    max = 0    
    
    # Find the max generation which has been reached by the algorithm
    for file in files:
        temp = int(file[0:-4])
        if ( temp > max ):
            max = temp
    
    return max;