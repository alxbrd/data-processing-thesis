import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import random
import csv
import matplotlib.lines as lines
import fnmatch
import os
from os import listdir
from os.path import isfile, join, exists
from mayavi import mlab
from pylab import *
import utils
import estimating

# Global Variables
display = 0             # Print (1) or not (0) the produced figures in files

def ApplyFont(ax):
    '''
    This method applies a set of predefined fonts to a figure. 
    We call this method before printing any figure for producing figures of the same font style.
    
    Args:
        ax: The current axes of the figure for which we want to change the font style.
    '''
    
    matplotlib.rcParams['ps.useafm'] = True
    matplotlib.rcParams['pdf.use14corefonts'] = True
    matplotlib.rcParams['text.usetex'] = True
    
    ticks = ax.get_xticklabels() + ax.get_yticklabels()

    text_size = 18

    for t in ticks:
        t.set_fontname('Times New Roman')
        t.set_fontsize(text_size)

    txt = ax.get_xlabel()
    txt_obj = ax.set_xlabel(txt)
    txt_obj.set_fontname('Times New Roman')
    txt_obj.set_fontsize(text_size)

    txt = ax.get_ylabel()
    txt_obj = ax.set_ylabel(txt)
    txt_obj.set_fontname('Times New Roman')
    txt_obj.set_fontsize(text_size)

    txt = ax.get_title()
    txt_obj = ax.set_title(txt)
    txt_obj.set_fontname('Times New Roman')
    txt_obj.set_fontsize(text_size)
    
def pareto2dplot(folders, approaches, colors, markers): 
    '''
    This method plots the 3D Pareto fronts achieved by the optimisation algorithms 
    where the third dimension (success rate) is indicated by the size of the points.
    
    Args:
        folders: Folders that contain the Pareto fronts in comparison.
        approaches: The names of the approaches used to be printed into the figures.
        colors: The colors used for indicating the various approaches on the figures.
        markers: The markers used for indicating the various approaches on the figures.
    '''
    
    fig = plt.figure()
    ax = fig.add_subplot(111)

    offsetSize = 30
    
    handles = []
    
    for (counter, folder) in enumerate(folders):
        latency = []
        sr = []
        nrg = []
        s = []
        folder = folder + "/"
        
        onlyfiles = [ f for f in listdir(folder) if isfile(join(folder,f)) ]

        for item in onlyfiles:
            filename = folder + item

            csv_file = csv.DictReader(open(filename, 'rb'), delimiter=',', quotechar='"')
            for row in csv_file:
                latency.append(float(row['ResponseTime']))
                sr.append(float(row['NetworkLatency']))
                nrg.append(float(row['Energy']))
                s.append(math.pow((100 - float(row['Energy'])),1.5) + offsetSize)
                
        ax.scatter(latency, sr, s = s, c = colors[counter], marker = markers[counter], label = str(folder))
        handles.append(lines.Line2D([0],[0], linestyle="none", c = colors[counter], marker = markers[counter]))
    
    ax.set_xlabel('Network Latency')
    ax.set_ylabel('Energy Consumption')
    ax.legend(handles, approaches, numpoints = 1)

    ApplyFont(plt.gca())
    plt.savefig("Pareto2D.pdf")
    
    # Draw the plot to the screen
    if display == 1:
        plt.show()
        
    return

def pareto3dplot(folders, approaches, colors, markers):  
    '''
    This method plots the 3D Pareto fronts achieved by the optimisation algorithms
    
    Args:
        folders: Folders that contain the Pareto fronts in comparison.
        approaches: The names of the approaches used to be printed into the figures.
        colors: The colors used for indicating the various approaches on the figures.
        markers: The markers used for indicating the various approaches on the figures.
    '''
    
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    handles = []
    
    for (counter, folder) in enumerate(folders):
        latency = []
        sr = []
        nrg = []
        folder = folder + "/"
        
        onlyfiles = [ f for f in listdir(folder) if isfile(join(folder,f)) ]

        for item in onlyfiles:
            filename = folder + item

            csv_file = csv.DictReader(open(filename, 'rb'), delimiter=',', quotechar='"')
            for row in csv_file:
                latency.append(float(row['ResponseTime']))
                sr.append(float(row['NetworkLatency']))
                nrg.append(float(row['Energy']))
    
        ax.scatter(latency, sr, nrg, s = 100, c = colors[counter], marker = markers[counter], label = str(folder))
        handles.append(lines.Line2D([0],[0], linestyle="none", c = colors[counter], marker = markers[counter]))
    
    ax.set_xlabel('Network Latency')
    ax.set_ylabel('Energy Consumption')
    ax.set_zlabel('100 - Success Ratio')
    ax.legend(handles, approaches, numpoints = 1)
    
    # Save the figure in a separate file
    plt.savefig('Pareto3D.pdf')

    # Draw the plot to the screen
    if display == 1:
        plt.show()
    
    return

def boxplotIndicators(start_run, end_run, indicators, indicators_names, model, fixed, variables, approaches, referencePoint, utopiaPoint, referenceSet, pdf_names, folder):
    '''
    This method boxplots for the quality indicator values for each of the methods in comparison.
    
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
        pdf_names: The name of the pdf files for storing the produced figures.
        folder: The folder of the experiments.
    '''    
    
    x = range(1, len(approaches) + 1)
        
    for i in range(0, indicators):
        counter = 0
        
        fig = plt.figure(i)
        ax = fig.add_subplot(111)
        ax.set_xlim([1, len(approaches) + 1])
        data_all = []
        index = 0
        
        for variable in variables:
            results_total = []  
            data = []
            local = 0

            for run in range(start_run, end_run + 1):
                
                dir_name = folder + str(run) + "/" + model + "/" + variable + "/" + str(fixed[0])
            
                # Find the right variation point (fitness function or optimisation algorithm)
                if exists(dir_name):    
                    final_generation = utils.find_final_generation(run, model, variable, fixed[0], folder)
                    dir_name = folder + str(run) + "/" + model + "/" + variable + "/" + str(fixed[0]) + "/Pareto/Generation" + str(final_generation) + "/"
                    # Results in the form of: hv_mean, hv_std, gd_mean, gd_std, delta_mean, delta_std
                    results = estimating.calculate_indicators(run, model, variable, str(fixed[0]), referencePoint, utopiaPoint, referenceSet, folder)
                else:     
                    final_generation = utils.find_final_generation(run, model, fixed[0], variable, folder)
                    dir_name = folder + str(run) + "/" + model + "/" + str(fixed[0]) + "/" + variable + "/Pareto/Generation" + str(final_generation) + "/"
                    # Results in the form of: hv_mean, hv_std, gd_mean, gd_std, delta_mean, delta_std
                    results = estimating.calculate_indicators(run, model, str(fixed[0]),  variable, referencePoint, utopiaPoint, referenceSet, folder)
                    
                results_total.append(results)
                local = local + len(approaches)
            index = index + 1
    
            # Store the results for a quality indicator for all the fitness functions used
            for j in range(0, end_run - start_run):
                data.append(float(results_total[j][i]))
            
            data_all.append(np.asarray(data))
                    
        ax.set_ylabel(indicators_names[i])
        plt.xticks(x, approaches)
        
        for item in ([ax.title, ax.xaxis.label, ax.yaxis.label] + ax.get_xticklabels() + ax.get_yticklabels()):
            item.set_fontsize(20)
            
        ## add patch_artist=True option to ax.boxplot() 
        ## to get fill color
        bp = ax.boxplot([data_all[item] for item in range(0, len(variables))], patch_artist=True)
        print(bp.keys())
        ## change outline color, fill color and linewidth of the boxes
        for box in bp['boxes']:
            # change outline color
            box.set(color= 'black', linewidth=2)
            # change fill color
            box.set(facecolor = 'black' , alpha=0.2)

        ## change color and linewidth of the whiskers
        for whisker in bp['whiskers']:
            whisker.set(color='black', linewidth=2)

        ## change color and linewidth of the caps
        for cap in bp['caps']:
            cap.set(color='black', linewidth=2)

        ## change color and linewidth of the medians
        for median in bp['medians']:
            median.set(color='black', linewidth=2)

        ## change the style of fliers and their fill
        for flier in bp['fliers']:
            flier.set(marker='o', color='black', alpha=0.5)

        # Save the figure in a separate file
        plt.savefig(pdf_names[i])
        
        # Draw the plot to the screen
        if display == 1:
            plt.show()
            
def printEvolution(start_run, end_run, indicators, indicators_names, model, functions, algorithms, approaches, referencePoint, utopiaPoint, referenceSet, pdf_names, colors, markers, linestyle, folder):
    '''
    This method visualises the evolution of the quality indicator values for each of the methods in comparison.
    
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
        pdf_names: The name of the pdf files for storing the produced figures.
        colors: The colors used for indicating the various approaches on the figures.
        markers: The markers used for indicating the various approaches on the figures.
        linestyle: The style of lines used for indicating the various approaches on the figures.
        folder: The folder of the experiments.
    '''   
    
    final_generation = utils.find_final_generation(end_run, model, functions[0], algorithms[0], folder)
    
    for i in range(0, indicators):
        fig = plt.figure(i)
        ax = fig.add_subplot(111)
        ax.set_xlim([1, final_generation])
        x = range(1, final_generation + 1)

        handles = []
        counter = 0
        
        for algorithm in algorithms:
            # Results in the form of: hv_mean, hv_std, gd_mean, gd_std, delta_mean, delta_std
            results = estimating.evolve_indicators(end_run, model, str(functions[0]), algorithm, referencePoint, utopiaPoint, referenceSet, folder)
            # Plot the data errors bars (std)
            plt.errorbar(x, results[i*2], yerr = results[i*2+1], ecolor = colors[counter])
            # Plot the data (mean)
            plt.plot(x, results[i*2], linestyle[counter])
            # For the legends
            ax.scatter(x, results[i*2], s = 90, c = colors[counter], marker = markers[counter], label = str(approaches[counter]))
            handles.append(lines.Line2D([0],[0], linestyle="none", c = colors[counter], marker = markers[counter]))
            counter = counter + 1
        
        ax.set_ylabel(indicators_names[i])
        ax.set_xlabel('# of Generation')
        ax.legend(handles, approaches, numpoints = 1, loc = 4)
        
        for item in ([ax.title, ax.xaxis.label, ax.yaxis.label] + ax.get_xticklabels() + ax.get_yticklabels()):
            item.set_fontsize(20)
            
        # Save the figure in a separate file
        plt.savefig(pdf_names[i])   

        # Draw the plot to the screen
        if display == 1:
            plt.show()