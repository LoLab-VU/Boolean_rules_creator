# Boolean_rules_creator

The optimization.py file is the most important run file that includes
  * the execution of the rule creation from the file rule_creator.py using the function creationg_rules()
  * the translation of the newly created rules to C++ and the compilation of the resulting file based on the template c_simluator.cpp_template
  * the execution of the DEAP based genetic algorithm to find an optimal model
  
To call on the expert knowledge optimization, run the file opt_human.py, which bases its model selection on the elimination of dependencies.

The repository contains the following files:

EMT_incbw_ruleX.txt ... the list of each transitions in the full backward model -> these files are are a starting point to setup the expert knowledge optimization.

EMT_paper.json ... This is the data file that describes the end point of the simulation results from the original model. This is the file to which we compare our automatically generated models.

EMT_userguided_ruleX.txt ... these files are obtained by running sort_list.py with the EMT_incbw_ruleX.txt files. Since the elimination of dependencies that are not self-dependencies are unique, these files are already sorted out in the according way. The optimizer therefore only reads the transitions where it needs to still decide, whether transitions to remove or not, according to the self-dependency selection.

c_simulator.cpp_template ... a template file on which the corresponding C++ file gets created: Each model creates a different rule set. To quickly execute the asynchronous updating simulation, the new ruleset gets compiled into its own temporary C++ file and runs outside of the python environment. The results are used for the optimizer in the optimization.py file or the opt_human.py

file_comparison.py ... this file performs the comparison between two json files: the EMT_paper.json file and the files generated by the temp files created from c_simulator.cpp_template. It returns the root mean square error between the dynamics given in those files

opt_human.py ... runfile that performs the optimization based on the expert knowledge. This code needs the input files EMT_userguided_ruleX.txt, since the removal of non-self dependencies are unique, and the optimizer only has to decide on the removal of transitions regarding self-dependencies.

optimization.py ... runfile that performs the unsupervised optimization over the whole possible search space

rule_creator.py ... executes the creation of the Boolean rules and also includes the algorithm for the expert knowledge inclusion, where the states are filtered by their appearance in the rule formulation

sort_list.py ... takes the files EMT_incbw_ruleX.txt as input and removes the desired dependencies (excluding self-dependencies) which are then saved in the files EMT_userguided_ruleX.txt. If we translate these files into rules, the resulting string would no longer include the species that are eliminated in this file. Self-dependencies, however, are still possible in these lists and are then eliminated in the opt_human.py file.

----------------------------------------------------------------------------------------

To execute these optimizations, we need the python packages deap, json, copy, intertools, math, os, numpy, ast, time, joblib, multiprocessing, and random. 
The parallel setup is determined by the variable parallel_sims and num_cores, which defines the number of cores used for the simulation.
To be able to run the C++ compiler, please make sure to have a current version of g++ on your computer, and link to the correct libraries in your system.

once the environment is set up, the code can be run using

    python optimization.py

or 

    python opt_human.py
    
The output is a folder "optimization_output" that stores the results for each created model: 
 * the files "fitness-XXX-XXX.txt" contains the information for each created model. The first three numbers determine the generation of the genetic algorithm, the second three numbers determine the individual of the population. The file itself contains the various random executions of the genetic algorithm (equivalent to the variable parallel_sims).
Each entry in these files starts with the computed fitness value, then it displays the determined rules that result in this fitness value in a way such that it can be used to be read by Boolean2Rules. Next, the simulation result for every initial condition is given (this is the same information as is stored and used by the json-files). Finally, we also include the transition list for every rule.
 * the files "run-XXX-XXX.json" are the corrsponding json files.
outside of the "optimization_output" folder, there will also be created an additional file "rms_fit.txt", that stores the rms values for each simulation for quick access.
