#!/usr/bin/env python
"""
stocks.py
Template by: Gary Lee (6.008 TA, Fall 2021)

Please read the project instructions beforehand! Your code should go in the
blocks denoted by "YOUR CODE GOES HERE" -- you should not need to modify any
other code!

NAME: Thiago Veloso de Souza
"""

# import packages here
import numpy as np
import matplotlib.pyplot as plt
import time

# Information for Stocks A and B
priceA = np.loadtxt('data/priceA.csv')
priceB = np.loadtxt('data/priceB.csv')

def get_growth(prH, day):
    
    if day == 0: return 1 
    return prH[day]/prH[day-1]

def get_D_growth(seq_D, day, alpha, beta):
    
    if seq_D[day] == '0': return alpha
    return beta

def investing(strategy, I_0=1.0, prA=None, prB=None, n=20, seq_D=None, 
                 gamma=None, alpha=None, beta=None):
    
    A_inv, B_inv = I_0/2, I_0/2
    
    total = [I_0]        

    for day in range(n):
        
        if prA is not None and prB is not None:
            growthA = get_growth(prA, day)
            growthB = get_growth(prB, day)
        else:
            growthA = get_D_growth(seq_D, day, alpha, beta) # growth for D
            growthB = gamma                                 # growth for C
            
        A_inv *= growthA
        B_inv *= growthB
        
        if strategy == 'buyandhold':
            total.append(A_inv+B_inv)
            
        elif strategy == 'rebalancing':
            new_total = A_inv + B_inv
        
            A_inv = new_total/2
            B_inv = new_total/2
            
            total.append(A_inv+B_inv) 

    return np.array(total)

# DO NOT RENAME OR REDEFINE THIS FUNCTION.
# THE compute_average_value_investments FUNCTION EXPECTS NO ARGUMENTS, AND
# SHOULD OUTPUT 2 FLOAT VALUES
def compute_average_value_investments():
    # -------------------------------------------------------------------------
    # YOUR CODE GOES HERE FOR PART (b)
    #
    # ASSIGN YOUR FINAL VALUES TO THE RESPECTIVE VARIABLES, I.E.,
    # average_buyandhold = (YOUR ANSWER FOR BUY & HOLD)
    # average_rebalancing = (YOUR ANSWER FOR REBALANCING)
    #
    
    n = 20
    gamma = 1.0500
    beta = 1.4000
    alpha = 0.7875
    
    average_buyandhold = 0
    average_rebalancing = 0
    
    for epoch in range(2**n):
        
        num = epoch + 1
        
        seq_D = np.binary_repr(epoch, width=n)
            
        buyandhold = investing(strategy='buyandhold',
                                n=n,
                                I_0=1.0,
                                seq_D=seq_D,
                                gamma=gamma,
                                alpha=alpha,
                                beta=beta)[-1]
        
        rebalancing = investing(strategy='rebalancing',
                                n=n,
                                I_0=1.0,
                                seq_D=seq_D,
                                gamma=gamma,
                                alpha=alpha,
                                beta=beta)[-1]  

        # update averages
        
        average_buyandhold = (average_buyandhold*(num-1) + buyandhold)/(num)
        average_rebalancing = (average_rebalancing*(num-1) + rebalancing)/(num)

    # END OF YOUR CODE FOR PART (b)
    # -------------------------------------------------------------------------
    
    
    return average_buyandhold, average_rebalancing


# DO NOT RENAME OR REDEFINE THIS FUNCTION.
# THE compute_doubling_rate_investments FUNCTION EXPECTS NO ARGUMENTS, AND
# SHOULD OUTPUT 2 FLOAT VALUES
def compute_doubling_rate_investments():
    # -------------------------------------------------------------------------
    # YOUR CODE GOES HERE FOR PART (e)
    #
    # ASSIGN YOUR FINAL VALUES TO THE RESPECTIVE VARIABLES, I.E.,
    # doubling_rate_buyandhold = (YOUR ANSWER FOR BUY & HOLD)
    # doubling_rate_rebalancing = (YOUR ANSWER FOR REBALANCING)
    
       
    n = 20
    gamma = 1.0500
    beta = 1.4000
    alpha = 0.7875
    
    doubling_rate_buyandhold = 0
    doubling_rate_rebalancing = 0
    i=0
    
    for epoch in range(2**n):
        
        seq_D = np.binary_repr(epoch, width=n)
        
        if seq_D.count('1') != (n/2): continue
        else: i+= 1
            
        buyandhold = investing(strategy='buyandhold',
                                n=n,
                                I_0=1.0,
                                seq_D=seq_D,
                                gamma=gamma,
                                alpha=alpha,
                                beta=beta)[-1]
        
        rebalancing = investing(strategy='rebalancing',
                                n=n,
                                I_0=1.0,
                                seq_D=seq_D,
                                gamma=gamma,
                                alpha=alpha,
                                beta=beta)[-1]  

        # update rates
        
        rn_buyandhold = (1/n)*np.log2(buyandhold)
        rn_rebalancing = (1/n)*np.log2(rebalancing)
    
        doubling_rate_buyandhold = (doubling_rate_buyandhold*(i-1) + rn_buyandhold)/(i)
        doubling_rate_rebalancing = (doubling_rate_rebalancing*(i-1) + rn_rebalancing)/(i)
    #
    # END OF YOUR CODE FOR PART (e)
    # -------------------------------------------------------------------------

    return doubling_rate_buyandhold, doubling_rate_rebalancing

def main():

    print("PART (b)")
    average_buyandhold, average_rebalancing = compute_average_value_investments()
    print(f'Computed Averaged Value for Buy & Hold: {average_buyandhold}')
    print(f'Computed Averaged Value for Rebalancing: {average_rebalancing}')
    print()
    
    # # '''
    # # Rebalancing performs better.
    # # '''

    print("PART (e)")
    doubling_rate_buyandhold, doubling_rate_rebalancing = compute_doubling_rate_investments()
    print(f'Computed Doubling Rate for Buy & Hold: {doubling_rate_buyandhold}')
    print(f'Computed Doubling Rate for Rebalancing: {doubling_rate_rebalancing}')
    print()

    # -------------------------------------------------------------------------
    # YOUR CODE GOES HERE FOR ALL OTHER PARTS
    
    print("PART (a)")
    
    fig, ax = plt.subplots(1)
    
    ax.plot(investing(strategy='buyandhold',
                      I_0=1.0, 
                      prA=priceA, 
                      prB=priceB, 
                      n=priceA.shape[0]), 
            label="Buy and Hold")
    
    ax.plot(investing(strategy='rebalancing',
                      I_0=1.0, 
                      prA=priceA, 
                      prB=priceB, 
                      n=priceA.shape[0]), 
            label='Rebalancing')
    
    ax.set_xlabel("Days"), ax.set_ylabel("Total Return")
    ax.legend()
    plt.show()
    
    '''
    The results are quite interesting. Despite being a counterintuitive strategy,
    one notices that constant rebalancing performs better in the long term than 
    pure buy and hold. This might be due to better risk management. If a stock is 
    constantly returning better investment, it is likely that will crash or similar.
    By constantly adjust the proportion, one avoids big losses. 
    '''
    
    print("PART (c)")
    
    n = 20
    gamma = 1.0500
    beta = 1.4000
    alpha = 0.7875
    
    frac = 0
    
    for epoch in range(2**n):
        
        seq_D = np.binary_repr(epoch, width=n)
            
        buyandhold = investing(strategy='buyandhold',
                                n=n,
                                I_0=1.0,
                                seq_D=seq_D,
                                gamma=gamma,
                                alpha=alpha,
                                beta=beta)[-1]
        
        rebalancing = investing(strategy='rebalancing',
                                n=n,
                                I_0=1.0,
                                seq_D=seq_D,
                                gamma=gamma,
                                alpha=alpha,
                                beta=beta)[-1] 
        
        if buyandhold > rebalancing: frac+=1
            
    print(f"Fraction of patterns BuyAndHold performed better: {frac}/{(2**n)}")
    
    '''
    26.32%
    '''
    
    print("PART (d)")
    
    times = []
    
    for it in range(1,21):
        
        time0 = time.time()
        n = it
        gamma = 1.0500
        beta = 1.4000
        alpha = 0.7875
        
        frac = 0
        
        for epoch in range(2**n):
            
            seq_D = np.binary_repr(epoch, width=n)
                
            buyandhold = investing(strategy='buyandhold',
                                    n=n,
                                    I_0=1.0,
                                    seq_D=seq_D,
                                    gamma=gamma,
                                    alpha=alpha,
                                    beta=beta)[-1]
            
            rebalancing = investing(strategy='rebalancing',
                                    n=n,
                                    I_0=1.0,
                                    seq_D=seq_D,
                                    gamma=gamma,
                                    alpha=alpha,
                                    beta=beta)[-1] 
            
            if buyandhold > rebalancing: frac+=1
        
        timeF = time.time()
        
        times.append(np.log(timeF-time0))
        
    fig, ax = plt.subplots(1)
    ones = np.ones(20)
    A = np.vstack([np.array([i for i in range(1,21)]),ones]).T

    b = np.array(times).reshape((20,1))
    m,c = np.linalg.lstsq(A, b, rcond=None)[0]
    
    print(f"Equation: {m.round(2)}n + {c.round(2)} = log(time)")
    print(f"Predicted time for n=30: {np.exp(m*30 + c)}")
    ax.plot(times, label='original')
    ax.plot(m*[i for i in range(1,21)]+c, label='fit')
    ax.set_xlabel("n")
    ax.set_ylabel("Log of time taken in seconds")
    plt.legend()
    plt.show()
        
    
    
    # END OF YOUR CODE FOR ALL OTHER PARTS
    # -------------------------------------------------------------------------



if __name__ == '__main__':  
    main()
