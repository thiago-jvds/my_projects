def MergeSort(A, p, r):
    '''
    Sorts in-place list with MergeSort algorithm

    Parameters
    ----------
        A : list
            List to be sorted

        p : int
            Inital sorting index of list A

        r : int
            Final sorting index of list A
    
    Returns
    -------
        None
    '''

    def Merge(A, p, q, r):
        '''
        Merges in-place list A[p:q+1] and A[q+1:r+1]

        Parameters
        ----------
            A : list
                List to be sliced and merged

            p : int
                Initial sorting index of list A

            q : int 
                Middle sorting index of list A

            r : int
                Final sorting index of list A
        
        Returns
        -------
            None
        '''
        n_1 = q-p+1     # Length of array A[p:q+1]
        n_2 = r-q       # Length of array A[q+1:r+1]

        # Init variables
        L = [0 for _ in range(n_1+1)]   # Left side
        R = [0 for _ in range(n_2+1)]   # Right side

        # Assigning left side values
        for i in range(n_1):
            L[i] = A[p+i]  

        # Assigning right side values
        for j in range(n_2):
            R[j] = A[q+j]

        # Final value to be +inf
        # greater than anything else
        L[n_1] = float('inf')
        R[n_2] = float('inf')

        # Init counters for loop
        i=0
        j=0

        for k in range(p,r+1):
            
            # If left side is smaller
            # Append to A and i++
            if L[i] <= R[j]:
                A[k] = L[i]
                i += 1

            # If right side is smaller
            # Append to A and j++
            else:
                A[k] = R[j]
                j += 1

    # Check if is possible to merge
    if p < r:

        q = (p+r)//2 # find mid value
        
        MergeSort(A, p, q) # Sort left side

        MergeSort(A,q+1, r) # Sort right side

        Merge(A, p, q, r) # Merge sorted list

def MedianFinding(A, k):
    '''
    Returns the lower (or upper) median of the list

    Does not modify given parameters.

    Assumptions:
        * there are no repetitions.
        * |A| is odd

    Parameters
    ----------
        A : list
            List to be analyzed
        
        k : int
            Rank of element
            Generally half of len(A)

    Returns
    -------
        median : int
            Median of A
    '''

    # Base case
    if len(A) == 1:
        return A[0]

    # Init variables
    n = len(A)
    A_ = A[:]
    groups = []
    medians = []
    
    # Divinding in groups of 5
    for i in range(0, n, 5):
        try:
            groups.append(A_[i:i+5])
        except:
            groups.append(A_[i:])
            break

    # Sort each group and get the median
    for group in groups:
        
        # as the size is fixed, sorting from indices 0 to end
        MergeSort(group, 0, len(group)-1) 

        # get median
        middle = len(group)//2
        medians.append(group[middle])

    # Find median of medians
    lenmid = (len(medians)+1)//2    # median position
    median = MedianFinding(medians, lenmid)

    # Computing rank
    L = [y for y in A if y < median]     # numbers Less than x
    G = [z for z in A if z > median]     # numbers Greaters than x

    rank_median = len(L)+1

    # Check where is the median

    # if rank is mid, median found
    if rank_median == k:
        return median
    
    # if rank is greater than mid, 
    # recurse to smaller numbers
    elif rank_median > k:
        return MedianFinding(L, k)

    # if rank is smaller than mid,
    # recurse to greater numbers
    elif rank_median < k:
        return MedianFinding(G, k - rank_median)
        
if __name__ == "__main__":

    import numpy as np

    rng = np.random.default_rng()

    test = list(rng.choice(2000, 501, replace=False))
    median = np.median(test)

    n = (len(test)+1)//2

    print(MedianFinding(test, n))
    print(median) 



        

