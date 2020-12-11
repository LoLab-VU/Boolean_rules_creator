from scipy.optimize import differential_evolution, minimize, basinhopping, dual_annealing
from deap import base, creator, tools
import file_comparison
import json
import copy
import itertools as it
import math
import os
import numpy as np
#from rule_simulator import rule_sim_run
from rule_creator import creating_rules
import ast
from time import time
from joblib import Parallel, delayed
import multiprocessing
import random

'''
def fitness(alpha,ref=False):
  # ....
  return fit

def clbk(xk,convergence):
    print('clbk: ',xk)
    return convergence
+
bounds = [(0.5,2.0),(0.1,1.0),(1.05,1.4),(0.6,0.95)]
res = differential_evolution(fitness, bounds, disp=True, callback=clbk, popsize=15)
'''


#def fitness(alpha, ref=False):


#problem_size: 8
fn_original = 'EMT_paper.json'
symbols = ['NICD', 'Notch', 'TP53', 'TP63TP73', 'miRNA', 'EMTreg', 'ECM', 'DNAdam']

#problem_size: 4
#fn_original = 'original_data.json'
#symbols = ['x1', 'x2', 'x3', 'x4']



(N, idx_freq) = file_comparison.map_freqs(fn_original)

print(N)
bounds = np.array([(0, 100)]*N)
x0 = np.random.rand(N)*100
#print(x0)
#exit()

pop_size = 5#150
generation = 0
counter = 0
parallel_sims = 50
'''
pop_size = 2
generation = 0
counter=0
parallel_sims = 5
'''
def randomized_runs():
    str_rules, rule_list, file_name = creating_rules("modified_freq.json", symbols)
    exe_file = '{}.bin'.format(file_name)
    json_file = '{}.json'.format(file_name)
    os.system('time g++ -DOUTPUT_FILE=\\"{2}\\" /home/martina/jsoncpp-master/jsoncpp-master/dist/jsoncpp.cpp -I/home/martina/jsoncpp-master/jsoncpp-master/dist/json  -O3 -fopenmp -x c++ {0} -o {1} && {1}'.format(file_name,exe_file,json_file))
    with open(json_file) as fs:
        freq_multiple_ss = json.load(fs)
    fs.close()

    os.remove(file_name)
    os.remove(exe_file)
    os.remove(json_file)

    return file_comparison.comparator(freq_multiple_ss, fn_original), freq_multiple_ss, str_rules, rule_list

def fitness(freq_to_change):
    global counter, generation

    #print('here')
    # take params and write file
    # ==========================
    with open(fn_original) as f2:
        orig_data = json.load(f2)

    number_of_combinations = len(ast.literal_eval(next(iter(orig_data)))) #int(math.sqrt(len(orig_data)))
    changed_freq = copy.deepcopy(orig_data)
    key_list = list(it.product([0, 1], repeat=number_of_combinations))
    key_list = [list(k) for k in key_list]
    freq_map = 0

    # update the frequencies in the json file according to the frequencies found in the optimizer
    for ividx, ivct in idx_freq:
        print(ividx, ivct)
        if ivct > 1:
            print(ividx, ivct)
            # print(ividx, ivct, key_list[ividx])
            for fr in range(0, ivct):
                changed_freq[str(key_list[ividx])][fr][1] = freq_to_change[freq_map]*100  # 100 since the freq_to_change here are only within 0 and 1
                #print(freq_to_change)
                #exit()
                print(str(key_list[ividx]), fr, freq_to_change[freq_map])
                #print(freq_map)
                freq_map = freq_map + 1

    with open("modified_freq.json", "w") as fs:
        fs.write(json.dumps(changed_freq, indent=4))

    # run SSA
    # =======
    rms = 100.0

    #num_cores = int(multiprocessing.cpu_count()/2)
    num_cores = 50
    print('using {} cores'.format(num_cores))
    a = time()
    results = Parallel(n_jobs=num_cores)(delayed(randomized_runs)() for i in range(parallel_sims))
    print('parallel region took {}'.format(time()-a))
    #print(results)

    fs_fitrules = open("optimization_output/fitness-{}-{}.txt".format(str(generation).zfill(3),str(counter).zfill(3)),"w")


    #for __run in range(0, parallel_sims):
    """    
        #os.system('python rule_creator.py')
        str_rules, rule_list = creating_rules("modified_freq.json", symbols)
        os.system('time g++ -O3 -fopenmp c_simulator.cpp -ljsoncpp && ./a.out')
        os.remove("c_simulator.cpp")
        with open('simulation_cpp.json') as fs:
            freq_multiple_ss = json.load(fs)
        fs.close()
        #freq_multiple_ss = rule_sim_run()
        print(freq_multiple_ss)

        rms_new = file_comparison.comparator(freq_multiple_ss)
    """

    for rms_new, freq_multiple_ss, str_rules, rule_list in results:
        rms_file.write('  {}\n'.format(rms_new))
        rms_file.flush()

        fs_fitrules.write('{}\n'.format(rms_new))
        fs_fitrules.write('{}'.format(str_rules))
        for freq_iv in freq_multiple_ss:
            fs_fitrules.write('{} -> '.format(freq_iv[0]))
            is_first = True
            for ss_freq in freq_iv[1]:
                if is_first == True:
                    fs_fitrules.write('{} {}\n'.format(ss_freq[0], ss_freq[1]))
                    is_first = False
                else:
                    fs_fitrules.write('{:>15} {} {}\n'.format('', ss_freq[0], ss_freq[1]))
        for idx, rule in zip(range(1,len(rule_list)+1),rule_list):
            fs_fitrules.write("{}: {}\n".format(idx,rule))
        fs_fitrules.write('\n\n')

        if rms_new < rms:
            rms = rms_new

    fs_fitrules.close()
    os.rename("modified_freq.json", "optimization_output/run-{}-{}.json".format(str(generation).zfill(3), str(counter).zfill(3)))

    rms_file.write('{}\t{}\n'.format(counter,rms))

    counter += 1
    if counter % pop_size == 0:
        counter = 0
        generation += 1
        rms_file.write('\n')

    rms_file.flush()

    return rms,


def clbk(xk,convergence):
    print("CLBK: ", xk);
    return convergence

def clbk3(xk,f,context):
    print('clbk: ',xk, f, context)
    counter = 0
    rms_file.write('iteration done\n')
    return False

def clbk2(xk):
    global counter
    print('generation finished')
    counter=0
    rms_file.write('iteration done\n')
    return False


#res = minimize(fitness, x0, method='Nelder-Mead', jac='2-point', callback=clbk2, options={'disp':True,'xtol':1.0, 'ftol':1.0})
#res = basinhopping(fitness, bounds, stepsize=20, minimizer_kwargs={'method':'Nelder-Mead'})

# ==================perform the optimization here!!!!!!========================

# using DEAP optimizer
creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
creator.create("Individual", list, fitness=creator.FitnessMin)

toolbox = base.Toolbox()
#initializer for the starting generation - each individual starts with this setup
toolbox.register("attr_float", random.random)  # the frequency starts with a random number between 0 and 100
toolbox.register("individual", tools.initRepeat, creator.Individual, toolbox.attr_float, N) # an individual has a list of N random numbers that will be changed by the optimizer
toolbox.register("population", tools.initRepeat, list, toolbox.individual)

#set up genetic optimizer functions
toolbox.register("evaluate", fitness)
toolbox.register("mate", tools.cxTwoPoint)
#toolbox.register("mate", tools.cxUniform, indpb=0.5)
#toolbox.register("mutate", tools.mutFlipBit, indpb=0.05)
toolbox.register("mutate", tools.mutPolynomialBounded, low=0.0, up=1.0, eta=20.0, indpb=0.1)
#toolbox.register("mutate", tools.mutUniformInt, low=0, up=100, indpb=0.05)
toolbox.register("select", tools.selTournament, tournsize=15)


def do_the_opt_dance():
    pop = toolbox.population(n=pop_size)  # note: here the population is only between 0 and 1 - this will be multiplied by 100 at the assignment in the fitness fct
    fitnesses = list(map(toolbox.evaluate, pop))  # map evaluation fct with every individual

    for ind, fit in zip(pop, fitnesses):
        ind.fitness.values = fit

    CXPB = 0.9  # probability with which two individuals are crossed
    MUTPB = 0.2  # probability for mutating and individual

    fits = [ind.fitness.values[0] for ind in pop]

    fs_min = open('fs_min_list.txt','w')
    fs_max = open('fs_max_list.txt','w')

    # Variable keeping track of the number of generations
    g = 0
    # Begin the evolution
    while min(fits) > 0 and g < 100:
        # A new generation
        g = g + 1
        print("-- Generation %i --" % g)

        # evolution: selecting, mating and mutating the individuals in the population
        # step 1: Select the next generation individuals
        offspring = toolbox.select(pop, len(pop))
        # Clone the selected individuals
        offspring = list(map(toolbox.clone, offspring)) # offspring list is an exact copy of the selected individuals. toolbox.clone ensures that we don't use a reference to the individuals but a completely independent instance

        # simple example, step 2&3: Apply crossover and mutation on the offspring
        for child1, child2 in zip(offspring[::2], offspring[1::2]):
            if random.random() < CXPB:
                toolbox.mate(child1, child2) # mating with Uniform distribution -> set probability to mate to 25%
                del child1.fitness.values
                del child2.fitness.values
        # the mutation of the prdocut children with a certain probability of CXPB and MUTPB.
        for mutant in offspring:
            if random.random() < MUTPB:
                toolbox.mutate(mutant)
                del mutant.fitness.values #the del statement will invalidate the fitness of the modified offspring

        # Content of some of our offspring changed during last step -> need to re-evaluate their fitnesses (just map those offspring with fitnesses where marked invalid)
        # Evaluate the individuals with an invalid fitness
        invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
        #print(invalid_ind)
        #exit()
        fitnesses = map(toolbox.evaluate, invalid_ind)
        for ind, fit in zip(invalid_ind, fitnesses):
            ind.fitness.values = fit
        # Replace the old population by the offspring
        pop[:] = offspring
        ind_min = 10000
        ind_max = 0
        for ind in pop:
            print('fitness tuple: ',ind.fitness.values)
            #exit()
            ind_min = min(ind_min, ind.fitness.values[0])
            ind_max = max(ind_max, ind.fitness.values[0])
        print('ind_max = ', ind_max, ' ind_min = ', ind_min)
        fs_min.write('{}\n'.format(ind_min))
        fs_max.write('{}\n'.format(ind_max))
       
        fs_min.flush()
        fs_max.flush()
 
        #exit()

    fs_min.close()
    fs_max.close()



rms_file = open("rms_fit.txt", "w+")
do_the_opt_dance()
#exit()


# old naive optimizer
#res = differential_evolution(fitness, bounds, popsize=pop_size, mutation=[0.2,0.6], disp=True, callback=clbk, polish=False, strategy='rand1exp')
#res = dual_annealing(fitness, bounds, callback=clbk3, no_local_search=True)

rms_file.close()







