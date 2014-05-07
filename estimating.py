import matplotlib.pyplot as plt
import random
import csv
import matplotlib.lines as lines
import numpy
import scipy as sp
import math
from mpl_toolkits.mplot3d import Axes3D
from os import listdir
from os.path import isfile, join, exists
from hv import *
from numpy import linalg
import utils
import tests

#
# Parameters
#
digits = 3              # Number of digits for rounding the results
objectives = 3          # Number of optimisation objectives

def calculate_executiontime(start_run, end_run, model, function, algorithm, folder): 
    '''
    This method calculates the total execution time of the input optimisation approaches.
    
    Args:
        start_run: The first run number of the experiments.
        end_run: The last run number of the experiments.
        model: The composition model used for the experiments (Centralised or Decentralised).
        function: The fitness function(s) used in the experiments (Expensive or Surrogate).
        algorithm: The optimisation algorithm used (Random Search or MOEA).
        folder: The folder of the experiments.
        
    Returns:
        The generational distance indicator for the given Pareto front.
    '''
    
    total_time = 0
    counter = 0 
    temp_results = []
    
    for run in range(start_run, end_run + 1):
        dir_name = folder + str(run) + "/" + str(model) + "/" + function + "/" + algorithm + "/Results/"
        
        files = [ f for f in listdir(dir_name) if isfile(join(dir_name,f)) ]
        
        max = 0    
        # Find the max generation which has been reached by the algorithm
        for file in files:
            temp = int(file[0:-4])
            if ( temp > max ):
                max = temp
                
        for generation in range(1, max + 1):
            file = folder + str(run) + "/" + model + "/" + function + "/" + algorithm + "/Results/" + str(generation) + ".csv"
                            
            source_file = open(file, 'rb')
            csv_file = csv.DictReader(source_file, delimiter = ',')
                
            for row in csv_file:
                temp_results.append(float(row['ExecutionTime'])  / 1000)   # In seconds
  
    array = numpy.asarray(temp_results)

    mean = round(array.mean(), digits)
    std = round(numpy.std(array), digits)
            
    mean = mean
    std = std
    
    return mean, std

def calculate_indicators(run, model, function, algorithm, referencePoint, utopiaPoint, referenceSet, folder): 
    '''
    This method calculates the quality performance indicators (Hypervolume, Cardinality, Spread, and Generational Distance) of the last generation
    
    Args:
        start_run: The first run number of the experiments.
        end_run: The last run number of the experiments.
        model: The composition model used for the experiments (Centralised or Decentralised).
        function: The fitness function used in the experiments (Expensive or Surrogate).
        algorithm: The optimisation algorithm used (Random Search or MOEA).
        referencePoint: The worst possible point achieved by all the experimental runs.
        utopiaPoint: The best possible point achieved by all the experimental runs.
        referenceSet: The normalised reference set of all the experimental runs.
        folder: The folder of the experiments.
        
    Returns:
        A list containing the four indicators ((Hypervolume, Cardinality, Spread, and Generational Distance).
    '''
    
    final_generation = utils.find_final_generation(run, model, function, algorithm, folder)
    dir_name = folder + str(run) + "/" + model + "/" + function + "/" + algorithm + "/Pareto/" + "Generation" + str(final_generation) + "/"    
    
    volume = 0
    gd = 0
    spacing = 0
    card = 0
    
    if exists(dir_name):
        front_norm = []
        front = []
        files = [ f for f in listdir(dir_name) if isfile(join(dir_name,f)) ]
            
        for file in files:
            csv_file = csv.DictReader(open(dir_name + file, 'rb'), delimiter=',', quotechar='"')
               
            for row in csv_file:
                front_norm.append([(float(row['ResponseTime']) - utopiaPoint[0]) / (referencePoint[0] - utopiaPoint[0]), (float(row['NetworkLatency']) - utopiaPoint[1]) / (referencePoint[1] - utopiaPoint[1]),(float(row['Energy']) - utopiaPoint[2]) / (referencePoint[2] - utopiaPoint[2])])
                front.append([float(row['ResponseTime']), float(row['NetworkLatency']), float(row['Energy'])])                
        
        # Calculate Hypervolume indicator
        hv = HyperVolume([1, 1, 1])
        volume = hv.compute(front_norm)
               
        # Cardinality indicator
        card = len(files)
        
        # Calculate Delta indicator and Execution time
        csv_file = csv.DictReader(open(folder + str(run) + "/" + model + "/" + function + "/" + algorithm + "/Results/" + str(final_generation) + ".csv", 'rb'), delimiter=',', quotechar='"')
        for row in csv_file:
            spacing = row['Spacing']
        
        # Generational Distance indicator
        gd = calculate_gd(front_norm, referenceSet)
       
        return [volume, gd, spacing, card]

def find_mean_and_std(array):
    '''
    This method calculates the mean and the standard deviation per row for an input two-dimensional list.
    
    Args:
        array: Two-dimensional array.
        
    Returns:
        Two lists (array_mean and array_std) containing the mean and the std for each row of the input two dimensional list.
    '''

    array_mean = []
    array_std = []
    
    # Find mean and std per row
    for j in range(0, len(array[0])):
        array_temp = []
        for i in range(0, len(array)):
            array_temp.append(array[i][j])

        # Convert to array
        temp_results = numpy.array(array_temp)
        # Calculate mean
        mean = round(temp_results.mean(), 4)
        array_mean.append(mean)
        # Calculate standard deviation
        std = round(numpy.std(temp_results), 4)
        array_std.append(std)
        
    return array_mean, array_std

def evolve_indicators(runs, model, function, algorithm, referencePoint, utopiaPoint, referenceSet, folder): 
    '''
    This method prints the evolution of the performance indicators (Hypervolume, Cardinality, Spread, and Generational Distance) 
    over the generations of the optimisation algorithms.
    
    Args:
        start_run: The first run number of the experiments.
        end_run: The last run number of the experiments.
        model: The composition model used for the experiments (Centralised or Decentralised).
        function: The fitness function used in the experiments (Expensive or Surrogate).
        algorithm: The optimisation algorithm used (Random Search or MOEA).
        referencePoint: The worst possible point achieved by all the experimental runs.
        utopiaPoint: The best possible point achieved by all the experimental runs.
        referenceSet: The normalised reference set of all the experimental runs.
        folder: The folder of the experiments.
        
    Returns:
        The method returns four pairs of lists containing the mean and standard deviation values of the quality indicators.
    '''
    
    final_generation = utils.find_final_generation(runs, model, function, algorithm, folder)
    
    hv_total = []
    gd_total = []
    delta_total = []
    card_total = []

    for run in range(1, runs + 1):             
        hv_temp = [0] * (final_generation)
        gd_temp= [0] * (final_generation)
        delta_temp= [0] * (final_generation)
        card_temp= [0] * (final_generation)
        
        for generation in range(1, final_generation + 1): 
            dir_name = folder + str(run) + "/" + model + "/" + function + "/" + algorithm + "/Pareto/Generation" + str(generation) + "/"
            #print(dir_name)
            
            if exists(dir_name):
                front = []
                front_norm = []
                files = [ f for f in listdir(dir_name) if isfile(join(dir_name,f)) ]
                
                for file in files:
                    csv_file = csv.DictReader(open(dir_name + file, 'rb'), delimiter=',', quotechar='"')
                    
                    for row in csv_file:
                        # Normalise data based on the reference point
                        front_norm.append([(float(row['ResponseTime']) - utopiaPoint[0]) / (referencePoint[0] - utopiaPoint[0]), (float(row['NetworkLatency']) - utopiaPoint[1]) / (referencePoint[1] - utopiaPoint[1]),(float(row['Energy']) - utopiaPoint[2]) / (referencePoint[2] - utopiaPoint[2])])
                        front.append([float(row['ResponseTime']), float(row['NetworkLatency']), float(row['Energy'])])                

                # Calculate Hypervolume indicator
                hv = HyperVolume([1, 1, 1])
                hv_temp[generation - 1] = hv.compute(front_norm)
                #print("Generation = ", generation, " and algorithm = ", algorithm)
               
                # Generational Distance indicator
                gd = calculate_gd(front_norm, referenceSet)
                gd_temp[generation - 1] = gd;
         
                # Calculate Delta indicator
                csv_file = csv.DictReader(open(folder + str(run) + "/" + model + "/" + function + "/" + algorithm + "/Results/" + str(generation) + ".csv", 'rb'), delimiter=',', quotechar='"')
                for row in csv_file:
                    spacing = row['Spacing']
                delta_temp[generation - 1] = float(spacing)
                
                # Cardinality indicator
                card_temp[generation - 1] = len(files);
                ##print("Model = " , model , " Algorithm = ",  algorithm, "Generation = ", generation, " HV = ", volume, " Spacing = ", spacing, " GD = ", gd, " Cardinality = ", len(files))

        hv_total.append(hv_temp)
        gd_total.append(gd_temp)
        delta_total.append(delta_temp)
        card_total.append(card_temp)

    hv_mean, hv_std = find_mean_and_std(hv_total)
    gd_mean, gd_std = find_mean_and_std(gd_total)
    delta_mean, delta_std = find_mean_and_std(delta_total)   
    card_mean, card_std = find_mean_and_std(card_total)   
    
    return hv_mean, hv_std, gd_mean, gd_std, delta_mean, delta_std, card_mean, card_std

def calculate_gd(pareto_front, reference_set):
    '''
    This method calculates the generational distance of a given Pareto front from a reference set.
        
    Args:
        pareto_front: The input Pareto front.
        reference_set: The reference set based on which the indicator is calculated.
        
    Returns:
        The value of the generational distance indicator for the given Pareto front.
    '''
    
    gd = 0

    # Find the closest solution in the reference set for each solution in the Pareto front
    for i in range(0, len(pareto_front)):
        min = 10000000
        for j in range(0, len(reference_set)):
            temp_distance = distance(pareto_front[i], reference_set[j])
            if min > temp_distance: 
                min = temp_distance
        
        gd = gd + math.pow(min, 2)
    
    return math.sqrt(gd) / len(pareto_front)

def distance(a, b):
    '''
    This method calculates the euclidean distance in the objective space between a pair of solutions.
    
    Args:
        a: The objective vector of the first solution.
        b: The objective vector of the second solution.
        
    Returns:
        The euclidean distance in the objective space between a pair of solutions.
    '''
    
    distance = 0;
    
    for i in range(0, len(a)):
        distance = distance + math.pow(math.fabs(a[i] - b[i]), 2)
    
    return math.sqrt(distance)

def calculateExecutionTime(start_run, end_run, indicators, indicators_names, model, functions, algorithms, approaches, referencePoint, utopiaPoint, referenceSet, folder, table):
    '''
    This method calculates the execution time for each of the methods in comparison.
    
    Args:
        start_run: The first run number of the experiments.
        end_run: The last run number of the experiments.
        indicators: List containing the quality indicators of interest.
        indicators_names: List containing the names of the quality indicators of interest.
        model: The composition model used for the experiments (Centralised or Decentralised).
        functions: The fitness functions used in the experiments (Expensive or Surrogate).
        algorithms: The optimisation algorithms used (Random Search or MOEA).
        approaches: The names of the optimisation algorithms used to be printed into the various tables and figures.
        referencePoint: The worst possible point achieved by all the experimental runs.
        utopiaPoint: The best possible point achieved by all the experimental runs.
        referenceSet: The normalised reference set of all the experimental runs.
        folder: The folder of the experiments.
        
    Returns:
        The calculated results in the desired Latex table format.
    '''
    
    results_total = []
    array_total = []
    
    for function in functions:
        results = []
        
        for run in range(start_run, end_run + 1):
            temp = calculate_indicators(run, model, function, str(algorithms[0]), referencePoint, utopiaPoint, referenceSet, folder)
            temp_array = numpy.array(temp)
            results.append(temp_array)
            
        results2 = []

        for i in range(0, indicators):  
            temp = []

            for j in range(0, len(results)):
                temp.append(float(results[j][i]))

            temp_results = numpy.array(temp)
            mean = round(temp_results.mean(), digits)
            std = round(numpy.std(temp_results), digits)
            results2.append(mean)
            results2.append(std)
                
            # Printing results for statistical testing
            array_total.append(temp)
        
        results_total.append(results2)
        
    time_exp = 13376.5 #  & 5.661
    hv_exp = results_total[0][0]
    
    body = approaches[i] + " & 13376.5 & -  & - \\\\" + "\n" 
    
    for i in range(1, len(results_total) ):
        [exec_mean, exec_std] = calculate_executiontime(start_run, end_run, model, str(functions[i]), str(algorithms[0]), folder)
        body = body + approaches[i] + " & " + str(exec_mean) + " & " # + str(exec_std) + " & "
        body = body + str(round(results_total[i][0]/hv_exp, digits))  + ' & ' + str(int(round(time_exp/exec_mean)))
        body = body + " \\\\"  + "\n"
    
    table.body = body    
    table.store()
    return table
    
def calculateIndicators(start_run, end_run, indicators, indicators_names, model, fixed, variables, approaches, referencePoint, utopiaPoint, referenceSet, label, folder, table):
    '''
    This method calculates the quality indicator values for each of the methods in comparison.
    
    Args:
        start_run: The first run number of the experiments.
        end_run: The last run number of the experiments.
        indicators: List containing the quality indicators of interest.
        indicators_names: List containing the names of the quality indicators of interest.
        model: The composition model used for the experiments (Centralised or Decentralised).
        fixed: This indicates the fixed part of the experiment which can be either the fitness function or the optimisation algorithm used. 
        variables: This indicates the variable part of the experiment which can be either the fitness function or the optimisation algorithm used. 
        approaches: The names of the optimisation algorithms used to be printed into the various tables and figures.
        referencePoint: The worst possible point achieved by all the experimental runs.
        utopiaPoint: The best possible point achieved by all the experimental runs.
        referenceSet: The normalised reference set of all the experimental runs.
        folder: The folder of the experiments.
        
    Returns:
        The calculated results in the desired Latex table format.
    '''
    
    results_total = []
    array_total = []
    
    for variable in variables:
        results = []
        
        for run in range(start_run, end_run + 1):
            
            dir_name = folder + str(run) + "/" + model + "/" + variable + "/" + str(fixed[0])
    
            # Find the right variation point (fitness function or optimisation algorithm)
            if exists(dir_name):    
                temp = calculate_indicators(run, model, variable, str(fixed[0]), referencePoint, utopiaPoint, referenceSet, folder)
            else:  
                temp = calculate_indicators(run, model, str(fixed[0]), variable, referencePoint, utopiaPoint, referenceSet, folder)

            temp_array = numpy.array(temp)
            results.append(temp_array)
            
        results2 = []

        for i in range(0, indicators):  
            temp = []

            for j in range(0, len(results)):
                temp.append(float(results[j][i]))

            temp_results = numpy.array(temp)
            mean = round(temp_results.mean(), digits)
            std = round(numpy.std(temp_results), digits)
            results2.append(mean)
            results2.append(std)
                
            ## Store results for statistical testing
            array_total.append(temp)
        
        results_total.append(results2)
    
    print(array_total) 
    
    # Perform statistical testing of the results
    array = numpy.asarray(results_total)
    pvalues = []

    for ind in range(0, indicators):  
        for i in range(ind, len(array_total) - 1, indicators):
               
            group1 = array_total[i]
            for j in range(ind + indicators, len(array_total) - 1, indicators):
                group2 = array_total[j]
                if i/indicators != j/indicators:
                    if ind == 0:
                        print(indicators_names[ind], " ", approaches[i/indicators], " vs. ", approaches[j/indicators], " P-value = " , tests.getPValue(group1, group2))
                    pvalue = tests.getPValue(group1, group2)
                    pvalues.append(pvalue)
    
    ##
    ### Print Latex table format
    ##
    body = ""
    
    for i in range(0, len(results_total) ):
        body = body + approaches[i] + " & "
        for j in range(0, len(results_total[0]) - 1, 2):
            # Add the data without new column 
            if j == len(results_total[0]) - 2 :
                body = body + str(round(results_total[i][j], 4)) +  ' & $\pm$ ' +  str(round(results_total[i][j+1], 2))
            else:
                body = body + str(round(results_total[i][j], 4)) +  ' & $\pm$ ' +  str(round(results_total[i][j+1], 2)) + ' & '

        body = body + ' \\\\'  + "\n"

    table.body = body    
    table.store()
    return table
   
def averageQoS(start_run, end_run, model, fixed, variables, approaches, referencePoint, utopiaPoint, referenceSet, folder, table):
    '''
    This method calculates the average QoS metrics values for each of the methods in comparison.
    
    Args:
        start_run: The first run number of the experiments.
        end_run: The last run number of the experiments.
        model: The composition model used for the experiments (Centralised or Decentralised).
        fixed: This indicates the fixed part of the experiment which can be either the fitness function or the optimisation algorithm used. 
        variables: This indicates the variable part of the experiment which can be either the fitness function or the optimisation algorithm used. 
        approaches: The names of the optimisation algorithms used to be printed into the various tables and figures.
        referencePoint: The worst possible point achieved by all the experimental runs.
        utopiaPoint: The best possible point achieved by all the experimental runs.
        referenceSet: The normalised reference set of all the experimental runs.
        folder: The folder of the experiments.
        
    Returns:
        The calculated results in the desired Latex table format.
    '''

    offset = objectives * 7
    metrics = ["Q$_{RT}$", "Q$_{E}$", "Q$_{SR}$"]
    headers = ['Mean', 'SD', 'Min', '1st Qu.', 'Median', '3rd Qu.', 'Max']

    results = [] 

    for variable in variables:
        rt_temp = [] 
        sr_temp = []
        nrg_temp = []

        for run in range(start_run, end_run + 1):
            
            dir_name = folder + str(run) + "/" + model + "/" + variable + "/" + str(fixed[0])
            
            # Find the right variation point (fitness function or optimisation algorithm)
            if exists(dir_name):    
                final_generation = utils.find_final_generation(run, model, variable, fixed[0], folder)
                dir_name = folder + str(run) + "/" + model + "/" + variable + "/" + str(fixed[0]) + "/Pareto/Generation" + str(final_generation) + "/"
            else:     
                final_generation = utils.find_final_generation(run, model, fixed[0], variable, folder)
                dir_name = folder + str(run) + "/" + model + "/" + str(fixed[0]) + "/" + variable + "/Pareto/Generation" + str(final_generation) + "/"
            
            if exists(dir_name):
                files = [ f for f in listdir(dir_name) if isfile(join(dir_name,f)) ]
                
                for file in files:
                    csv_file = csv.DictReader(open(dir_name + file, 'rb'), delimiter=',', quotechar='"')
                    for row in csv_file:
                        rt_temp.append(float(row['ResponseTime']))
                        nrg_temp.append(float(row['NetworkLatency']))     
                        sr_temp.append(100 - float(row['Energy']))     

        metrics_list = [rt_temp, sr_temp, nrg_temp]
        
        for metric in metrics_list:
            results.append(round(float(format(numpy.array(metric).mean())), digits))     ##Mean 
            results.append(round(float(format(numpy.array(metric).std())), digits))      ##SD 
            results.append(round(float(format(numpy.array(metric).min())), digits))      ##Min
            results.append(round(float(numpy.percentile(metric, 25)), digits))           ##1st Qu. 
            results.append(round(float(format(sp.median(numpy.array(metric)))), digits)) ##Median
            results.append(round(float(numpy.percentile(metric, 75)), digits))           ##3rd Qu.
            results.append(round(float(format(numpy.array(metric).max())), digits))      ##Max

    ##
    ## Print Latex table format
    ##
    body = ""

    counter = 0
    print(results)
    for i in range(0, objectives): 
        body = body + "\multirow{7}{*}{" + metrics[i] + "}  & " + headers[0] 
        
        for k in range(0, len(approaches)): 
            body = body + " & " + str(results[counter + k * offset])
        body = body + " & \multirow{7}{*}{$<$2.2 10$^{-16}$} \\\\" + "\n"    

        counter = counter + 1;
        
        for j in range(1, 7):  
            body = body + " & " + headers[j]
            for k in range(0, len(approaches)): 
                body = body + " & " + str(results[counter + k * offset])
            body = body + "\\\\ \n"
            counter = counter + 1;
        
        if i < objectives - 1:
            body = body + "[2.05ex] \n"
    
    table.body = body    
    table.store()
    return table

class Table(object):
    def __init__(self, header, body, caption, label, filename):
        self.header = header
        self.body = body
        self.caption = caption
        self.label = label
        self.filename = filename
        self.latex = ""
    def create(self):
        table = "\\begin{table}[h]" + "\n"
        table = table + "\\centering" + "\n"
        table = table + "\\footnotesize\\setlength{\\tabcolsep}{2.5pt}" + "\n" 
        table = table + "\\ra{1.3}" + "\n" 
        table = table + self.header + "\n"
        table = table + self.body
        table = table + "\\bottomrule" + "\n" 
        table = table + "\\end{tabular}" + "\n"
        table = table + "\\caption{" + self.caption + "}\\label{" + self.label + "}" + "\n"
        table = table + "\\end{table}" + "\n"
        self.latex = table
    def store(self):
        f1 = open(self.filename, 'w+')
        self.create()
        f1.write(self.latex)