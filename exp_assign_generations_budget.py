'''
    What is the best performing surrogate model for the same generations budget?
    Compare the results achieved by NSGA-II optimisation algorithm when using 
    the expensive function and the four surrogate functions (LR, CART, MARS, RF)
    and when assigning the same time budget to the optimisation algorithm.
'''

print('Experiment - Comparison of surrogate models by assigning to them the same generations budget')

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
end_run = 18                                    
algorithms = ['NSGAIInew']                                      # MOEA algorithm name
functions = ['ExpensiveFunction', 'LR', 'MARS', 'CART', 'RF']   # Fitness functions
approaches = ['Expensive', 'LR', 'MARS', 'CART', 'RF']          # Name of approaches to be printed in Latex tables
model = 'Decentralised'                                         # Composition model
folder = "files/"                                               # Results folder

[referencePoint, utopiaPoint, referenceSet] = pareto.initialise(start_run, end_run, model, functions, algorithms, folder)

#
# Step 1
#
print('#### Step 1')
experiment_folder = parameters.output_folder +  "Exp_Gen_Budget/"
if os.path.exists(experiment_folder):
    shutil.rmtree(experiment_folder)
os.makedirs(experiment_folder)

pdf_names = ['HV.pdf', 'IGD.pdf', 'Delta.pdf', 'Cardinality.pdf']
for i in range(0, len(pdf_names)):
    pdf_names[i] = experiment_folder + "boxplots_" + pdf_names[i]
    
plotting.boxplotIndicators(start_run, end_run, parameters.indicators, parameters.indicators_names, model, algorithms, functions, approaches, referencePoint, utopiaPoint, referenceSet, pdf_names, folder)

#
# Step 2
#
print('#### Step 2')
header = "\\begin{tabular}{@{}c c c c c c c c c@{}} \\toprule" + "\n" 
header = header + "\\multicolumn{1}{c}{\\textbf{Fitness}} & \\multicolumn{2}{c}{$\\mathbf{I_{HV}}$} & \\multicolumn{2}{c}{$\\mathbf{I_{C}}$} & \\multicolumn{2}{c}{$\\mathbf{\Delta}$} & \\multicolumn{2}{c}{$\\mathbf{I_{GD}}$} \\\\ \\cmidrule{2-3} \\cmidrule{4-5} \\cmidrule{6-7} \\cmidrule{8-9}" + "\n"
header = header + "\\multicolumn{1}{c}{\\textbf{Function}} & \\textbf{Mean} & $\\mathbf{\\sigma}$ & \\textbf{Mean} & $\\mathbf{\sigma}$ & \\textbf{Mean} & $\\mathbf{\\sigma}$ & \\textbf{Mean} & $\\mathbf{\\sigma}$ \\\\ \midrule"
caption = "Quality indicator values when assigning the same generations budget for all the surrogate-assisted optimisation techniques."
label = "tab:surrogates_generations_ind" 
table_file = experiment_folder + 'Indicators.txt'
table = estimating.Table(header, "", caption,label, table_file)  

table = estimating.calculateIndicators(start_run, end_run, parameters.indicators, parameters.indicators_names, model, algorithms, functions, approaches, referencePoint, utopiaPoint, referenceSet, label, folder, table)
print(table.latex)

header = "\\begin{tabular}{@{}c c c c@{}} \\toprule" + "\n" 
header = header + "\multicolumn{1}{c}{\\textbf{Fitness}} & \multicolumn{1}{c}{$\mathbf{t_{exec}}$ \\textbf{(seconds)}} & \multicolumn{1}{c}{\\textbf{Quality}} & \multicolumn{1}{c}{\\textbf{Execution}} \\\\" + "\n"
header = header + "\\textbf{Function} & $\mathbf{\mu}$ & \\textbf{Degradation} & \\textbf{Speed-up}  \\\\ \\midrule"
caption = "Execution time per generation for the various surrogate models."
label = "tab:surrogates_generations_time" 
table_file = experiment_folder + 'Time.txt'
table = estimating.Table(header, "", caption,label, table_file)  

table = estimating.calculateExecutionTime(start_run, end_run, parameters.indicators, parameters.indicators_names, model, functions, algorithms, approaches, referencePoint, utopiaPoint, referenceSet, folder, table)
print(table.latex)

#
# Step 3
#
print('#### Step 3')
header = "\\begin{tabular}{@{}c l c c c c c c@{}} \\toprule " + "\n"
header = header + "& & \multicolumn{5}{c}{\\textbf{Fitness Function}} & \\\\ \\cmidrule{3-7} " + "\n"
header = header + "\\textbf{QoS Metric} & \\textbf{Statistic} & \\textbf{Expensive} & \\textbf{LR} & \\textbf{MARS} & \\textbf{CART} & \\textbf{RF} & \\textbf{p-value}\\\\ \\midrule"
caption = "QoS values when assigning the same generations budget for all the surrogate-assisted optimisation techniques."
label = "tab:surrogates_generations_QoS" 
table_file = experiment_folder + 'QoS.txt'
table = estimating.Table(header, "", caption,label, table_file)  

table = estimating.averageQoS(start_run, end_run, model, algorithms, functions, approaches, referencePoint, utopiaPoint, referenceSet, folder, table)
print(table.latex)