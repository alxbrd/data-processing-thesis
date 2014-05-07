import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import random
import csv
import matplotlib.lines as lines
from os import listdir
from os.path import isfile, join

def pareto3dplot():    # Plots the 3d pareto fronts achieved by the optimisation algorithms
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    handles = []
    colors = ['blue', 'red']
    markers = ['o', 'v']
    latency = []
    sr = []
    nrg = []

    folders = ['NSGA', 'Random']

    for (counter, folder) in enumerate(folders):
        folder = folder + "/"
        
        onlyfiles = [ f for f in listdir(folder) if isfile(join(folder,f)) ]

        for item in onlyfiles:
            filename = folder + item
            ## print filename
            csv_file = csv.DictReader(open(filename, 'rb'), delimiter=',', quotechar='"')
            for row in csv_file:
                latency.append(float(row['ResponseTime']))
                sr.append(float(row['NetworkLatency']))
                nrg.append(float(row['Energy']))
            
        ax.scatter(latency, sr, nrg, s = 70, c = colors[counter], marker = markers[counter], label = str(folder))
        handles.append(lines.Line2D([0],[0], linestyle="none", c = colors[counter], marker = markers[counter]))
        
    print("handles = ", len(handles))

    ax.legend(handles, folders, numpoints = 1)

    plt.show()
    return