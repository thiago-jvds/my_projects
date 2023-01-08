#!/usr/bin/env python
# inference.py
# Base code by George H. Chen (georgehc@mit.edu)
# updated 10/05/2021 by Gary Lee (Fall 2021)
#
# Modified by: <your name here!>


# use this to enable/disable graphics
enable_graphics = True

from email.mime import message
from pyexpat.errors import messages
import sys
import numpy as np
import robot
from robot import Distribution

if enable_graphics:
    import graphics


#-----------------------------------------------------------------------------
# Functions for you to implement
#

def getNeighbors(observation):
    
    x,y = observation
    
    L = []
    
    for i in range(-1,2):
        for j in range(-1,2):
            
            if 0 <= x+i <= 11 and 0 <= y +j <= 7:
                L.append((x+i, y+j))
                
    return set(L)

def forward_backward(all_possible_hidden_states,
                     all_possible_observed_states,
                     prior_distribution,
                     transition_model,
                     observation_model,
                     observations):
    """
    Inputs
    ------
    all_possible_hidden_states: a list of possible hidden states

    all_possible_observed_states: a list of possible observed states

    prior_distribution: a distribution over states

    transition_model: a function that takes a hidden state and returns a
        Distribution for the next state

    observation_model: a function that takes a hidden state and returns a
        Distribution for the observation from that hidden state

    observations: a list of observations, one per hidden state
        (a missing observation is encoded as None)

    Output
    ------
    A list of marginal distributions at each time step; each distribution
    should be encoded as a Distribution (see the Distribution class in
    robot.py and see how it is used in both robot.py and the function
    generate_data() above, and the i-th Distribution should correspond to time
    step i
    """

    num_time_steps = len(observations)
    forward_messages = [None] * num_time_steps
    forward_messages[0] = prior_distribution
    # TODO: Compute the forward messages
    
    
    for time in range(1,num_time_steps):        
        
        forward_messages[time] = Distribution()
        
        for currentState in all_possible_hidden_states:
            
            S = 0
            
            x,y, _ = currentState
            
            if (observations[time] is not None) and (x,y) not in getNeighbors(observations[time]): continue
            
            for previousState in all_possible_hidden_states:
            
                if observations[time-1] is None: phiTilda = 1.0
                else: phiTilda = observation_model(previousState)[observations[time-1]]
                
                previousMessage = forward_messages[time-1][previousState]
                psi = transition_model(previousState)[currentState]
                
                if phiTilda * previousMessage * psi == 0: continue
                
                S += phiTilda * previousMessage * psi
                
            if S != 0: forward_messages[time][currentState] = S

        forward_messages[time].renormalize()

    backward_messages = [None] * num_time_steps
    # TODO: Compute the backward messages
    
    for time in range(num_time_steps-1, -1, -1):
        
        backward_messages[time] = Distribution()
                    
        for currentState in all_possible_hidden_states:
            
            S = 0
            
            for previousState, psi in transition_model(currentState).items():
            
                
                if time == num_time_steps - 1:
                    previousMessage = 1.0
                    phiTilda = 1.0

                else:
                    previousMessage = backward_messages[time+1][previousState]
                    
                    if observations[time+1] is None: phiTilda = 1.0
                    else: phiTilda = observation_model(previousState)[observations[time+1]]
                
                
                if phiTilda * previousMessage * psi == 0: continue
                
                S += phiTilda * previousMessage * psi
                
            if S != 0: backward_messages[time][currentState] = S
        
        backward_messages[time].renormalize()
                
            

    marginals = [None] * num_time_steps # remove this
    # TODO: Compute the marginals
    
    for time in range(num_time_steps):
        
        marginals[time] = Distribution()
        
        for state in all_possible_hidden_states:
            
            psiTilda = observation_model(state)[observations[time]]
            forward_message = forward_messages[time][state]
            backward_message = backward_messages[time][state]
            
            if psiTilda * forward_message * backward_message == 0:
                continue
                
            marginals[time][state] = psiTilda * forward_message * backward_message
                                
        marginals[time].renormalize()
    
    return marginals

def Viterbi(all_possible_hidden_states,
            all_possible_observed_states,
            prior_distribution,
            transition_model,
            observation_model,
            observations):
    """
    Inputs
    ------
    See the list inputs for the function forward_backward() above.

    Output
    ------
    A list of esimated hidden states, each encoded as a tuple
    (<x>, <y>, <action>)
    """

    # TODO: This is for you to implement

    num_time_steps = len(observations)
    estimated_hidden_states = [None] * num_time_steps # remove this
    
    # at index i, T i -> (i-1)
    trace_back = [None] * num_time_steps
    
    # at index i, M (i-1) -> i
    messages = [None] * num_time_steps
    
    for time in range(num_time_steps):
        
        messages[time] = Distribution()
        trace_back[time] = {}
        
        for currentState in all_possible_hidden_states:
            
            vals = []
            states = []
            
            x,y, _ = currentState
            
            # observation_model(currentState)[observations[time]] == 0
            if observations[time] and (x,y) not in getNeighbors(observations[time]): continue
            
            for previousState in all_possible_hidden_states:
                if time == 0:
                    
                    previousMessage = 1.0
                    
                    phi = prior_distribution[previousState]
               

                    
                else:
                    
                    previousMessage = messages[time-1][previousState]
                    
                    if observations[time-1] is None: phi = 1.0
                    else: phi = observation_model(previousState)[observations[time-1]]
                    
                psi = transition_model(previousState)[currentState]
                
                states.append(previousState)
                vals.append(phi*psi*previousMessage)
            
            if len(states) != 0:
                max_index = np.argmax(vals)
                trace_back[time][currentState] = states[max_index]
                messages[time][currentState] = vals[max_index]

                
                
                        
        
    # compute the MPC
    
    for time in range(num_time_steps-1, -1, -1):
        
        if time == num_time_steps-1:
            
            vals_states = {}
            
            for state in all_possible_hidden_states:
                
                if observations[time] is None: phi = 1.0
                else: phi = observation_model(state)[observations[time]]
                                
                vals_states[state] = phi*messages[time][state]
                
            if len(vals_states) != 0:
                max_state = max(vals_states, key = vals_states.get)
                estimated_hidden_states[time] = max_state
            
        else:
            i_hat = estimated_hidden_states[time+1]
                        
            estimated_hidden_states[time] = trace_back[time+1][i_hat]         

    return estimated_hidden_states

def second_best(all_possible_hidden_states,
                all_possible_observed_states,
                prior_distribution,
                transition_model,
                observation_model,
                observations):
    """
    Inputs
    ------
    See the list inputs for the function forward_backward() above.

    Output
    ------
    A list of esimated hidden states, each encoded as a tuple
    (<x>, <y>, <action>)
    """

    # TODO: This is for you to implement

    num_time_steps = len(observations)
    estimated_hidden_states = [None] * num_time_steps # remove this

    return estimated_hidden_states


#-----------------------------------------------------------------------------
# Generating data from the hidden Markov model
#

def generate_data(initial_distribution, transition_model, observation_model,
                  num_time_steps, make_some_observations_missing=False,
                  random_seed=None):
    # generate samples from a hidden Markov model given an initial
    # distribution, transition model, observation model, and number of time
    # steps, generate samples from the corresponding hidden Markov model
    hidden_states = []
    observations  = []

    # if the random seed is not None, then this makes the randomness
    # deterministic, which may be helpful for debug purposes
    np.random.seed(random_seed)

    # draw initial state and emit an observation
    initial_state       = initial_distribution().sample()
    initial_observation = observation_model(initial_state).sample()

    hidden_states.append(initial_state)
    observations.append(initial_observation)

    for time_step in range(1, num_time_steps):
        # move the robot
        prev_state   = hidden_states[-1]
        new_state    = transition_model(prev_state).sample()

        # maybe emit an observation
        if not make_some_observations_missing:
            new_observation = observation_model(new_state).sample()
        else:
            if np.random.rand() < .1: # 0.1 prob. of observation being missing
                new_observation = None
            else:
                new_observation = observation_model(new_state).sample()

        hidden_states.append(new_state)
        observations.append(new_observation)

    return hidden_states, observations


#-----------------------------------------------------------------------------
# Main
#

if __name__ == '__main__':
    # flags
    make_some_observations_missing = False
    use_graphics                   = enable_graphics
    need_to_generate_data          = True

    # parse command line arguments
    for arg in sys.argv[1:]:
        if arg == '--missing':
            make_some_observations_missing = True
        elif arg == '--nographics':
            use_graphics = False
        elif arg.startswith('--load='):
            filename = arg[7:]
            hidden_states, observations = robot.load_data(filename)
            need_to_generate_data = False
            num_time_steps = len(hidden_states)

    # if no data is loaded, then generate new data
    if need_to_generate_data:
        num_time_steps = 100
        hidden_states, observations = \
            generate_data(robot.initial_distribution,
                          robot.transition_model,
                          robot.observation_model,
                          num_time_steps,
                          make_some_observations_missing)

    all_possible_hidden_states   = robot.get_all_hidden_states()
    all_possible_observed_states = robot.get_all_observed_states()
    prior_distribution           = robot.initial_distribution()

    print('Running forward-backward...')
    marginals = forward_backward(all_possible_hidden_states,
                                 all_possible_observed_states,
                                 prior_distribution,
                                 robot.transition_model,
                                 robot.observation_model,
                                 observations)
    print('\n')

    timestep = num_time_steps - 1
    print("Most likely parts of marginal at time %d:" % (timestep))
    if marginals[timestep] is not None:
        top_10_states = sorted(marginals[timestep].items(), key=lambda x: x[-1], reverse=True)[:10]
        print([s for s in top_10_states if s[-1]>0])
        
    else:
        print('*No marginal computed*')
    print('\n')

    timestep = 0
    print("Most likely parts of marginal at time %d:" % (timestep))
    if marginals[timestep] is not None:
        top_10_states = sorted(marginals[timestep].items(), key=lambda x: x[-1], reverse=True)[:10]
        print([s for s in top_10_states if s[-1]>0])
    else:
        print('*No marginal computed*')
    print('\n')
    

    print('Running Viterbi...')
    estimated_states = Viterbi(all_possible_hidden_states,
                               all_possible_observed_states,
                               prior_distribution,
                               robot.transition_model,
                               robot.observation_model,
                               observations)
    print('\n')

    if num_time_steps > 10:
        print("Last 10 hidden states in the MAP estimate:")
        for time_step in range(num_time_steps - 10, num_time_steps):
            if estimated_states[time_step] is None:
                print('Missing')
            else:
                print(estimated_states[time_step])
        print('\n')

        print('Finding second-best MAP estimate...')
        estimated_states2 = second_best(all_possible_hidden_states,
                                        all_possible_observed_states,
                                        prior_distribution,
                                        robot.transition_model,
                                        robot.observation_model,
                                        observations)
        print('\n')

        print("Last 10 hidden states in the second-best MAP estimate:")
        for time_step in range(num_time_steps - 10 - 1, num_time_steps):
            if estimated_states2[time_step] is None:
                print('Missing')
            else:
                print(estimated_states2[time_step])
        print('\n')

        difference = 0
        for time_step in range(num_time_steps):
            if estimated_states[time_step] != hidden_states[time_step]:
                difference += 1
        print("Number of differences between MAP estimate and true hidden " + \
              "states:", difference)
        true_prob = robot.sequence_prob(hidden_states,
                                       robot.transition_model, robot.observation_model,
                                       prior_distribution, observations)
        print("True Sequence Prob:", true_prob)
        map_prob = robot.sequence_prob(estimated_states,
                                       robot.transition_model, robot.observation_model,
                                       prior_distribution, observations)
        print("MAP Estimate Prob:", map_prob)


        difference = 0
        for time_step in range(num_time_steps):
            if estimated_states2[time_step] != hidden_states[time_step]:
                difference += 1
        print("Number of differences between second-best MAP estimate and " + \
              "true hidden states:", difference)
        map_prob2 = robot.sequence_prob(estimated_states2,
                                       robot.transition_model, robot.observation_model,
                                       prior_distribution, observations)
        print("Second-best MAP Estimate Prob:", map_prob2)

        difference = 0
        for time_step in range(num_time_steps):
            if estimated_states[time_step] != estimated_states2[time_step]:
                difference += 1
        print("Number of differences between MAP and second-best MAP " + \
              "estimates:", difference)

    # display
    if use_graphics:
        app = graphics.playback_positions(hidden_states,
                                          observations,
                                          estimated_states,
                                          marginals)
        app.mainloop()
