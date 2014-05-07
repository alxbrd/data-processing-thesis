'''
    Experiment performing a basic sanity check by comparing the results 
    achieved by the Random Search and the NSGA-II optimisation algorithm.
'''

print('Experiment - Comparison of NSGA-II with Random Search')

import parameters
import pareto
import estimating
import plotting
import os
import shutil

#
# Definition of the experimental specific parameters
#
start_run = 1
end_run = 30
algorithms = ['RandomSearch', 'NSGAIInew']              # MOEA algorithm name
approaches = ['Random Search', 'NSGA-II']               # Names to be printed into figures
model = 'Decentralised'                                 # Composition model
functions = ['ExpensiveFunction']                       # Fitness function
folder = "files/"                                       # Results folder

[referencePoint, utopiaPoint, referenceSet] = pareto.initialise(start_run, end_run, model, functions, algorithms, folder)

#
# Step 1
#
print('#### Step 1')
experiment_folder = parameters.output_folder +  "Exp_Comp_Random/"
if os.path.exists(experiment_folder):
    shutil.rmtree(experiment_folder)
os.makedirs(experiment_folder)

pdf_names = ['HV.pdf', 'IGD.pdf', 'Delta.pdf', 'Cardinality.pdf']
for i in range(0, len(pdf_names)):
    pdf_names[i] = experiment_folder + "evolution_" + pdf_names[i]
    
plotting.printEvolution(start_run, end_run, parameters.indicators, parameters.indicators_names, model, functions, algorithms, approaches, referencePoint, utopiaPoint, referenceSet, pdf_names, parameters.colors, parameters.markers, parameters.linestyle, folder)

#
# Step 2
#
print('#### Step 2')
header = "\\begin{tabular}{@{}c c c c c c c c c@{}} \\toprule" + "\n" 
header = header + "\\multicolumn{1}{c}{\\textbf{Fitness}} & \\multicolumn{2}{c}{$\\mathbf{I_{HV}}$} & \\multicolumn{2}{c}{$\\mathbf{I_{C}}$} & \\multicolumn{2}{c}{$\\mathbf{\Delta}$} & \\multicolumn{2}{c}{$\\mathbf{I_{GD}}$} \\\\ \\cmidrule{2-3} \\cmidrule{4-5} \\cmidrule{6-7} \\cmidrule{8-9}" + "\n"
header = header + "\\multicolumn{1}{c}{\\textbf{Function}} & \\textbf{Mean} & $\\mathbf{\\sigma}$ & \\textbf{Mean} & $\\mathbf{\sigma}$ & \\textbf{Mean} & $\\mathbf{\\sigma}$ & \\textbf{Mean} & $\\mathbf{\\sigma}$ \\\\ \midrule"
caption = "Quality indicator values when assigning the same generations budget for all the surrogate-assisted optimisation techniques."
label = "tab:nsga_random_ind" 
table_file = experiment_folder + 'Indicators.txt'
table = estimating.Table(header, "", caption,label, table_file)  

table = estimating.calculateIndicators(start_run, end_run, parameters.indicators, parameters.indicators_names, model, functions, algorithms, approaches, referencePoint, utopiaPoint, referenceSet, label, folder, table)
print(table.latex)


#
# Step 3
#
print('#### Step 3')
header = "\\begin{tabular}{@{}c l c c c@{}} \\toprule " + "\n"
header = header + "& & \multicolumn{2}{c}{\\textbf{Fitness Function}} & \\\\ \\cmidrule{3-4} " + "\n"
header = header + "\\textbf{QoS Metric} & \\textbf{Statistic} & \\textbf{Random Search} & \\textbf{NSGA-II} & \\textbf{p-value}\\\\ \\midrule"
caption = "QoS metric values achieved by the MOEAs in comparison."
label = "tab:MOEAs_ind" 
table_file = experiment_folder + 'QoS.txt'
table = estimating.Table(header, "", caption,label, table_file)  

table = estimating.averageQoS(start_run, end_run, model, functions, algorithms, approaches, referencePoint, utopiaPoint, referenceSet, folder, table)
print(table.latex)

#
# Step 4
#
print('#### Step 4')
## Plot 3D Pareto Surfaces of composition models in comparison
folders = ['files/1/Decentralised/ExpensiveFunction/RandomSearch/Pareto/Generation30', 'files/1/Decentralised/ExpensiveFunction/NSGAIInew/Pareto/Generation30']
plotting.pareto2dplot(folders, approaches, parameters.colors, parameters.markers)