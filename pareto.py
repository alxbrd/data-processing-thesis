import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import random
import csv
import matplotlib.lines as lines
import fnmatch
import os
from os import listdir
from os.path import isfile, join
from mayavi import mlab
from pylab import *
import numpy as np
from os import listdir
from os.path import isfile, join, exists
import utils

def pareto_frontier(Xs, Ys, maxX = False, maxY = False):
    '''
    This method finds the elements which lie on the Pareto frontier (sorted into order) of two input equally-sized lists.
    The default behaviour is to find the maximum for both X and Y, but the option is
    available to specify maxX = False or maxY = False to find the minimum for either
    or both of the parameters.
    
    Args:
        Xs: The first list of X points.
        Ys: The second list of Y points.
        maxX: When true find the minimum for the X parameter.
        maxY: When true find the minimum for the Y parameter.
    Returns:
        A list of Pareto front points.
    '''
    
    # Sort the list in either ascending or descending order of X
    myList = sorted([[Xs[i], Ys[i]] for i in range(len(Xs))], reverse=maxX)
    # Start the Pareto frontier with the first value in the sorted list
    p_front = [myList[0]]    
    # Loop through the sorted list
    for pair in myList[1:]:
        if maxY: 
            if pair[1] >= p_front[-1][1]: # Look for higher values of Y
                p_front.append(pair) # and add them to the Pareto frontier
        else:
            if pair[1] <= p_front[-1][1]: # Look for lower values of Y
                p_front.append(pair) # and add them to the Pareto frontier
    # Turn resulting pairs back into a list of Xs and Ys
    p_frontX = [pair[0] for pair in p_front]
    p_frontY = [pair[1] for pair in p_front]
    return p_frontX, p_frontY

def pareto_frontier_multi(myArray):
    '''
    This method finds the pareto front of a multidimensional input array.
    
    Args:
        myArray: The multidimensional array of points.
    Returns:
        A list of points in the Pareto front.
    '''
    
    # Sort on first dimension
    myArray = myArray[myArray[:,0].argsort()]
    # Add first row to pareto_frontier
    pareto_frontier = myArray[0:1,:]
    # Test next row against the last row in pareto_frontier
    for row in myArray[1:,:]:
        if sum([row[x] < pareto_frontier[-1][x]
                for x in range(len(row))]) >= 1:
            # If it is better on all features add the row to pareto_frontier
            pareto_frontier = np.concatenate((pareto_frontier, [row]))
    return pareto_frontier


def initialise(start_run, end_run, model, functions, algorithms, folder):
    '''
    This method is the first step for calculating the results of an experiment.
    This step finds and returns the referencePoint, utopiaPoint, and referenceSet,
    which are necessary for calculating the quality indicators.
    
    Args:
        start_run: The first run number of the experiments.
        end_run: The last run number of the experiments.
        model: The composition model used for the experiments (Centralised or Decentralised).
        functions: The fitness function(s) used in the experiments (Expensive or Surrogate).
        algorithms: The optimisation algorithm used (Random Search or MOEA).
        folder: The folder of the experiments.
    
    Returns:
        A list of the following:
        referencePoint: The worst possible point achieved by all the experimental runs.
        utopiaPoint: The best possible point achieved by all the experimental runs.
        referenceSet: Normalised reference set according to the reference point.
    '''

    # Reference Point (RP)
    referencePoint = reference_point(start_run, end_run, model, functions, algorithms, folder)
    #print("Reference_point values = ", referencePoint)

    utopiaPoint = utopia_point(start_run, end_run, model, functions, algorithms, folder)
    #print("utopiaPoint values = ", utopiaPoint)

    # Reference Set (RS)
    referenceSet = reference_set(start_run, end_run, model, functions, algorithms, referencePoint, utopiaPoint, folder)
    #print("referenceSet size = ", len(referenceSet))  

    # Normalise RS with the RP
    for i in range(0, len(referenceSet)):
        for j in range(0, 3):
            referenceSet[i][j] = referenceSet[i][j] / referencePoint[j]
            
    return [referencePoint, utopiaPoint, referenceSet]

def reference_set(start_run, end_run, model, functions, algorithms, referencePoint, utopiaPoint, folder): 
    '''
    This method finds the Pareto set also called Reference Set (RS) 
    of all Pareto points of all the executed experiments runs..
    
    Args:
        start_run: The first run number of the experiments.
        end_run: The last run number of the experiments.
        model: The composition model used for the experiments (Centralised or Decentralised).
        functions: The fitness function(s) used in the experiments (Expensive or Surrogate).
        algorithms: The optimisation algorithm used (Random Search or MOEA).
        referencePoint: The worst possible point achieved by all the experimental runs.
        utopiaPoint: The best possible point achieved by all the experimental runs.
        folder: The folder of the experiments.
    
    Returns:
        referenceSet: The set of Pareto points of all the experimental executions.
    '''
    
    front = []

    for algorithm in algorithms:
        for function in functions:
            for run in range(start_run, end_run + 1):
                final_generation = utils.find_final_generation(run, model, function, algorithm, folder)
                dir_name = folder + str(run) + "/" + model + "/" + function + "/" + algorithm + "/Pareto/Generation" + str(final_generation) + "/"
                ##print(dir_name) 
                
                if exists(dir_name):
                    files = [ f for f in listdir(dir_name) if isfile(join(dir_name,f)) ]
                    
                    for file in files:
                        csv_file = csv.DictReader(open(dir_name + file, 'rb'), delimiter=',', quotechar='"')
                    
                        for row in csv_file:
                            front.append([(float(row['ResponseTime']) - utopiaPoint[0]) / (referencePoint[0] - utopiaPoint[0]), (float(row['NetworkLatency']) - utopiaPoint[1]) / (referencePoint[1] - utopiaPoint[1]),(float(row['Energy']) - utopiaPoint[2]) / (referencePoint[2] - utopiaPoint[2])])

    myArray = np.array(front)
    referenceSet = pareto_frontier_multi(myArray)
  
    return referenceSet

def reference_point(start_run, end_run, model, functions, algorithms, folder): 
    '''
    This method finds the worst possible Pareteo solution also called Nadir point which
    plays the role of the Reference Point (RP) for the calculations of the quality indicators.
    
    Args:
        start_run: The first run number of the experiments.
        end_run: The last run number of the experiments.
        model: The composition model used for the experiments (Centralised or Decentralised).
        functions: The fitness function(s) used in the experiments (Expensive or Surrogate).
        algorithms: The optimisation algorithm used (Random Search or MOEA).
        folder: The folder of the experiments.
    
    Returns:
        referencePoint: The worst possible Pareto solution of all the experimental executions.
    '''
    
    front = []
    
    for algorithm in algorithms:
        for function in functions:
            for run in range(start_run, end_run + 1):
                final_generation = utils.find_final_generation(run, model, function, algorithm, folder)
                dir_name = folder + str(run) + "/" + model + "/" + function + "/" + algorithm + "/QoSMetrics/Generation" + str(final_generation) + "/"
                #print(dir_name) 
                
                if exists(dir_name):
                    files = [ f for f in listdir(dir_name) if isfile(join(dir_name,f)) ]
                    
                    for file in files:
                        csv_file = csv.DictReader(open(dir_name + file, 'rb'), delimiter='	', quotechar='"')
                        
                        if file != 'population.csv':
                            for row in csv_file:
                                front.append([float(row['Delay2']), float(row['Energy']), 100 - float(row['Success_Ratio'])])                

    myArray = np.array(front)
    worst_front = pareto_frontier_multi(myArray)

    # Find the worst value for each objective
    referencePoint = [0, 0, 0]

    for i in range(0, 3):
        for j in range(0, len(worst_front)):
            if worst_front[j][i] > referencePoint[i]:
                referencePoint[i] = worst_front[j][i]
            
    return referencePoint

def utopia_point(start_run, end_run, model, functions, algorithms, folder): 
    '''
    This method finds the best possible Pareteo solution also called Utopia point.
    
    Args:
        start_run: The first run number of the experiments.
        end_run: The last run number of the experiments.
        model: The composition model used for the experiments (Centralised or Decentralised).
        functions: The fitness function(s) used in the experiments (Expensive or Surrogate).
        algorithms: The optimisation algorithm used (Random Search or MOEA).
        folder: The folder of the experiments.
    
    Returns:
        utopiaPoint: The best possible Pareto solution of all the experimental executions.
    '''
    
    front = []
    
    for algorithm in algorithms:
        for function in functions:
            for run in range(start_run, end_run + 1):
                final_generation = utils.find_final_generation(run, model, function, algorithm, folder)
                dir_name = folder + str(run) + "/" + model + "/" + function + "/" + algorithm + "/QoSMetrics/Generation" + str(final_generation) + "/"
                ##print(dir_name) 
                
                if exists(dir_name):
                    files = [ f for f in listdir(dir_name) if isfile(join(dir_name,f)) ]
                    
                    for file in files:
                        csv_file = csv.DictReader(open(dir_name + file, 'rb'), delimiter='	', quotechar='"')
                        
                        if file != 'population.csv':
                            for row in csv_file:
                                front.append([float(row['Delay2']), float(row['Energy']), 100 - float(row['Success_Ratio'])])                
        
    print("initial front size = " , len(front))
    myArray = np.array(front)
    best_front = pareto_frontier_multi(myArray)
    print("front size = ", len(best_front))

    # Find the best value for each objective
    utopiaPoint = [10000, 10000, 10000]

    for i in range(0, 3):
        for j in range(0, len(best_front)):
            if best_front[j][i] < utopiaPoint[i]:
                utopiaPoint[i] = best_front[j][i]
            
    return utopiaPoint