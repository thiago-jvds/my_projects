from __future__ import division
import sys
import random
import numpy as np
import networkx as nx
import util
import matplotlib.pyplot as plt

def divergence(dist1, dist2):
    s = 0
    for state in dist1.keys():
        if dist1[state] == 0 or dist2[state]== 0: continue
        s+= dist1[state]*np.log2(dist1[state]/dist2[state])
    return s

def approx_markov_chain_steady_state(conditional_distribution, N_samples, iterations_between_samples):
    """
    Computes the steady-state distribution by simulating running the Markov
    chain. Collects samples at regular intervals and returns the empirical
    distribution of the samples.

    Inputs
    ------
    conditional_distribution : A dictionary in which each key is an state,
                               and each value is a Distribution over other
                               states.

    N_samples : the desired number of samples for the approximate empirical
                distribution

    iterations_between_samples : how many jumps to perform between each collected
                                 sample

    Returns
    -------
    An empirical Distribution over the states that should approximate the
    steady-state distribution.
    """
    empirical_distribution = util.Distribution()

    # -------------------------------------------------------------------------
    # YOUR CODE GOES HERE FOR PART (a)
    
    possibleStates = list(conditional_distribution.keys())
    state = random.choice(possibleStates)
    
    i = 0
    samplesCollected = 0
    
    while samplesCollected != N_samples:
        
        EPS = random.random()
        
        if EPS <= 0.1:
            state = random.choice(possibleStates)
        else:
            state = conditional_distribution[state].sample()
                
        if i % iterations_between_samples == 0 and i != 0:
            empirical_distribution[state] += 1
            samplesCollected += 1
             
        i += 1
            
    empirical_distribution.normalize()
    # END OF YOUR CODE FOR PART (a)
    # -------------------------------------------------------------------------

    return empirical_distribution

def get_graph_distribution(filename):
    G = nx.read_gml(filename)
    d = nx.to_dict_of_dicts(G)
    cond_dist = util.Distribution({k: util.Distribution({k_: v_['weight'] for k_,v_ in v.items()}) for k,v in d.items()})
    return cond_dist

def run_pagerank(data_filename, N_samples, iterations_between_samples):
    """
    Runs the PageRank algorithm, and returns the empirical
    distribution of the samples.

    Inputs
    ------
    data_filename : a file with the weighted directed graph on which to run the Markov Chain

    N_samples : the desired number of samples for the approximate empirical
                distribution

    iterations_between_samples : how many jumps to perform between each collected
                                 sample

    Returns
    -------
    An empirical Distribution over the states that should approximate the
    steady-state distribution.
    """
    conditional_distribution = get_graph_distribution(data_filename)

    steady_state = approx_markov_chain_steady_state(conditional_distribution,
                            N_samples,
                            iterations_between_samples)

    pages = conditional_distribution.keys()
    top = sorted( (((steady_state[page]), page) for page in pages), reverse=True )

    values_to_show = min(20, len(steady_state))
    print("Top %d pages from empirical distribution:" % values_to_show)
    for i in range(0, values_to_show):
        print("%0.6f: %s" %top[i])
    return steady_state

if __name__ == '__main__':
    if len(sys.argv) != 4:
        print("Usage: python markovChain.py <data file> <samples> <iterations between samples>")
        sys.exit(1)
    data_filename = sys.argv[1]
    N_samples = int(sys.argv[2])
    iterations_between_samples = int(sys.argv[3])
    conditional_dis = get_graph_distribution(data_filename)
    dist1 = approx_markov_chain_steady_state(conditional_dis, N_samples, iterations_between_samples)
    dist2 = approx_markov_chain_steady_state(conditional_dis, N_samples, iterations_between_samples)

    div = divergence(dist1, dist2)
    print(div)
    
    # total_samples = [2**i for i in range(7,14)]
    
    # res = []
    # conditional_distribution = get_graph_distribution(data_filename)

    
    # for n_s in total_samples:
        
    #     dist1 = approx_markov_chain_steady_state(conditional_distribution, n_s, 1000)
        
    #     dist2 = approx_markov_chain_steady_state(conditional_distribution, n_s, 1000)
        
    #     res.append(divergence(dist1, dist2))
        
    # plt.plot(total_samples, res)
    # plt.savefig("plot_div2.png")
        
        
