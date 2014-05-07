import plotting
import estimating
import numpy

runs = 1 # Total number of experiments runs
##composition_models = ['Decentralised']
composition_models = ['Centralised', 'Decentralised']
objective_functions = ['ExpensiveFunction']
algorithms = ['NSGAIInew']
##algorithms = ['NSGAII','RandomSearch']
final_generation = 30
threshold_sc = 100

##
## 1.
## Calculate the average performance indicators for the centralised and the proposed composition models
##
longstring = """\n\n*****************************************
*
* Step 1/5
* Calculate Performance Indicators for Centralised and Proposed Composition Model
*
*****************************************
"""
print longstring

runs = 3 
referencePoint = [30, 2, 100]
composition_models = ['Centralised']
algorithms = ['NSGAIInew']
        
for model in composition_models:
    metrics = []
    
    for i in range(1, runs + 1):
        temp = estimating.calculate_indicators(i, model, 'ExpensiveFunction', algorithms, final_generation, threshold_sc, referencePoint)
        metrics.append(temp)
        print("Run = ", i, temp)
            
    array = numpy.array(metrics)
    print("Runs = ", i, "Objective Function = " , 'ExpensiveFunction', " Model = " , model , " HV Mean = ", round(float(array[:,0].mean()), 4), " HV Std = ", round(float(numpy.std(array[:,0])), 4), " Cardinality = ",  round(float(array[:,1].mean()), 4), " Cardinality Std = ",  round(float(numpy.std(array[:,1])), 4), " Spacing = ", round(float(array[:,2].mean()),  4),  " Spacing Std = ", round(float(numpy.std(array[:,2])),  4))

##
## 2.
## Calculate the average QoS achieved by the composition models in comparison
##
longstring = """\n\n*****************************************
*
* Step 2/5
* Calculate Average Execution Times
*
*****************************************
"""
print longstring

runs = 1 # Total number of experiments runs
composition_models = ['Centralised', 'Decentralised']

for model in composition_models:

    results = []

    print("Model = " , model)
    for i in range(1, runs + 1):
        temp = estimating.calculate_qos(i, model, 'ExpensiveFunction', algorithms, final_generation, threshold_sc)
        temp_array = numpy.array(temp)
        results.append(temp_array)

    print(results)
    
    headers = ["Average Latency", "Average Energy", "Average Success Ratio", "Latency std", "Energy std", "Success Ratio std"]

    for i in range(0, len(temp_array[0])):
        print("D: ", headers[i], " = ", round(temp_array[:,i].mean(), 4))

##
## 3.
## Plot 3D Pareto Surfaces of composition models in comparison
##
longstring = """\n\n*****************************************
*
* Step 3/5
* Plot 3D Pareto Surfaces
*
*****************************************
"""
print longstring

##folders = ['1/Centralised/ExpensiveFunction/NSGAIInew/Pareto/Generation30', '1/Decentralised/ExpensiveFunction/NSGAIInew/Pareto/Generation30']
##plotting.pareto3dplot(folders)

##
## 4.
## Plot the average execution time of the various objective functions used
##
longstring = """\n\n*****************************************
*
* Step 4/5
* Calculate Average Execution Times
*
*****************************************
"""
print longstring

objective_functions = ['ExpensiveFunction', 'LR', 'MARS', 'CART', 'RF']

for function in objective_functions:
    exec_time = []
    temp = 0
    for i in range(1, runs + 1):
        temp = temp + estimating.calculate_executiontime(i, 'Decentralised', function, algorithms, final_generation)
    exec_time.append(temp)
    print("Average Total Execution time of Function - ", function, " is ", numpy.mean(exec_time) / 1000, " seconds.")

##
## 5.
## Calculate Performance Indicators for Expensive and Approximation Models
##
longstring = """\n\n*****************************************
*
* Step 5/5
* Calculate Performance Indicators for Expensive and Approximation Models
*
*****************************************
"""
print longstring

objective_functions = ['ExpensiveFunction', 'LR', 'MARS', 'CART', 'RF']

for function in objective_functions:

    results = []

    for i in range(1, runs + 1):
        temp = estimating.calculate_qos(i, 'Decentralised', function, algorithms, final_generation, threshold_sc)
        temp_array = numpy.array(temp)
        results.append(temp_array)

    headers = ["Average Latency", "Average Energy", "Average Success Ratio", "Latency std", "Energy std", "Success Ratio std"]

    print("Objective Function = " , function)
    for j in range(0, len(temp_array[0])):
        print("D: ", headers[j], " = ", round(temp_array[:,j].mean(), 4))

##
## 6.
## Calculate Performance Indicators for Expensive and Approximation Models
##
longstring = """\n\n*****************************************
*
* Step 6/6
* Calculate Performance Indicators for Expensive and Approximation Models
*
*****************************************
"""
print longstring

objective_functions = ['ExpensiveFunction', 'LR', 'MARS', 'CART', 'RF']

for function in objective_functions:
    metrics = []
    
    for i in range(1, runs + 1):
        metrics = estimating.calculate_indicators(i, 'Decentralised', function, algorithms, final_generation, threshold_sc, referencePoint)
        ##print("Run = ", i, "Objective Function = " , function, " Model = " , model , " Algorithm = ",  algorithms, "Generation = ", final_generation, " HV = ", round(float(metrics[i-1][0]), 4), " Cardinality = ",  round(float(metrics[i-1][1]), 4), " Spacing = ", round(float(metrics[i-1][2]), 4))
