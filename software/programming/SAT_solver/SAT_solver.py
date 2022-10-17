#!/usr/bin/env python3
"""6.009 Lab 5 -- Boolean satisfiability solving"""

import sys
import typing
import doctest
sys.setrecursionlimit(10000)
# NO ADDITIONAL IMPORTS

def update_expression(expression, assignment):
    """
    Update expression based on an assignment
    
    Parameters
    ----------
        expression : list
            List of clauses
            
        assignment : tuple
            Tuple containing (str, bool)
            
    Returns
    -------
        New expression
    >>> A = [('a', True), ('b', True),('c', False)]
    >>> update_expression(A,('c', True))
    [('a', True), ('b', True)] 
    
    >>> A
    [('a', True), ('b', True), ('c', False)]
    
    >>> update_expression([('c', True), ('d', True)],('c', False))
    [('d', True)]
    """
    not_assignment = (assignment[0], not assignment[1])
    new_exp = [clause[:] for clause in expression]
    
    if assignment in new_exp:
        return True
        
    elif not_assignment in new_exp:
        new_exp = list(filter(lambda x: x != not_assignment, new_exp))
    
    return new_exp

def satisfying_assignment(formula):
    '''
    '''
    d = in_satisfying_assignment(formula)
    
    if d is not None:
        vars = set()
        
        for expression in formula:
            for clause in expression:
                vars.add(clause[0])
                
        for var in vars:
            if d.get(var) is None:
                d[var] = True 
                
    return d

def in_satisfying_assignment(formula):
    """
    Find a satisfying assignment for a given CNF formula.
    Returns that assignment if one exists, or None otherwise.

    >>> satisfying_assignment([])
    {}
    >>> x = satisfying_assignment([[('a', True), ('b', False), ('c', True)]])
    >>> x.get('a', None) is True or x.get('b', None) is False or x.get('c', None) is True
    True
    >>> satisfying_assignment([[('a', True)], [('a', False)]])
    """

    # base case
    # print('sol called on', formula)
    if formula == []:
        # print('trivial return')
        return {}
    
    # optimization 2
    for exp in formula:
        
        if len(exp) == 1:
            # print('found unit clause ', exp)
            var1, bool = exp[0]
            
            # print('trying ', var1, bool)
            F1 = []
            for expression in formula:
                clause = update_expression(expression, (var1, bool))
                if clause == []:
                    # print('found impossible clause within unit clause')
                    return None
                if clause != True:
                    F1.append(clause)
                
            d = in_satisfying_assignment(F1)
            
            # if F1 is solvable
            if d is not None:
                d[var1] = bool
                # print('sol found, returning ', d)
                return d

            return None
            
            
            
    # get variable
    var = formula[0][0][0]

    # optimization 1
    # check impossibility
    if [(var, True)] in formula and [(var, False)] in formula:
        return None
            

    # check if var set to True is possible
    # print('trying ', var, True)
    flag = True
    F1 = []
    for expression in formula:
        clause = update_expression(expression, (var,True))
        if clause == []:
            # print('found impossible clause')
            flag = False
            break
        if clause != True:
            F1.append(clause)
        
    if flag:
        d = in_satisfying_assignment(F1)
        
        # if F1 is solvable
        if d is not None:
            d[var] = True
            # print('sol found, returning ', d)
            return d
    
    # check if var set to False is possible
    # print('trying ', var, False)
    F1 = []
    for expression in formula:

        clause = update_expression(expression, (var,False))
        if clause == []:
            # print('found impossible clause, returning None')
            return None
        if clause != True:
            F1.append(clause)

    
    d = in_satisfying_assignment(F1)
    
    if d is not None:
        d[var] = False
        print('sol found, returning, ',d)
        return d
            
    # if there is not possible with either
    print('no sol found, return None')
    return None
            
def desired_sessions(student_preferences):
    """
    >>> desired_sessions({'Alice': ['basement', 'penthouse'],
    ...                    'Bob': ['kitchen'],
    ...                    'Charles': ['basement', 'kitchen'],
    ...                    'Dana': ['kitchen', 'penthouse', 'basement']})
    [[('Alice_basement', True), ('Alice_penthouse', True)], [('Bob_kitchen', True)], [('Charles_basement', True), ('Charles_kitchen', True)], [('Dana_kitchen', True), ('Dana_penthouse', True), ('Dana_basement', True)]]
    """
    CNF1 = []
    for student in student_preferences:
        CNF1.append([(student+'_'+room, True) for room in student_preferences[student]])

    return CNF1   

def exactly_once(student_preferences):
    """
    
    >>> exactly_once({'Alice': ['basement', 'penthouse'],
    ...                    'Bob': ['kitchen'],
    ...                    'Charles': ['basement', 'kitchen'],
    ...                    'Dana': ['kitchen', 'penthouse', 'basement']})
    [[('Alice_basement', False), ('Alice_penthouse', False)], [('Charles_basement', False), ('Charles_kitchen', False)], [('Dana_kitchen', False), ('Dana_penthouse', False)], [('Dana_kitchen', False), ('Dana_basement', False)], [('Dana_penthouse', False), ('Dana_basement', False)]]
    """
    CNF2 = []
    for student, preferences in student_preferences.items():
        
        for i in range(len(preferences)):
            for j in range(i+1,len(preferences)):
                CNF2.append([(student+'_'+preferences[i], False), (student+'_'+preferences[j], False)])
    
    return CNF2

def all_combinations(L, number):
    """_summary_

    Args:
        L (_type_): _description_
        number (_type_): _description_
    """
    # base case
    if number == 0:
        yield []
    
    for i in range(len(L)):
        for comb in all_combinations(L[i+1:], number-1):
            yield [L[i]]+comb
        

def no_overscribed(student_preferences, room_capacities):
    """
    >>> no_overscribed({'Alice': ['basement', 'penthouse'],
    ...                    'Bob': ['kitchen'],
    ...                    'Charles': ['basement', 'kitchen'],
    ...                    'Dana': ['kitchen', 'penthouse', 'basement']},                           
    ...                    {'basement': 1,
    ...                    'kitchen': 2,
    ...                    'penthouse': 4})
    [[('Alice_basement', False), ('Charles_basement', False)], [('Alice_basement', False), ('Dana_basement', False)], [('Charles_basement', False), ('Dana_basement', False)], [('Bob_kitchen', False), ('Charles_kitchen', False), ('Dana_kitchen', False)]] 
    """
    CNF3 = []

    for room, capacity in room_capacities.items():
        tmp = []
        
        qual_studs = [student for student in student_preferences.keys() if room in student_preferences[student]]
        
        for comb in all_combinations(qual_studs, capacity+1):
            tmp2 = []
            for stud in comb:
                tmp2.append((stud+'_'+room, False))
            tmp.append(tmp2) 
        
        CNF3 += tmp
        
    return CNF3
                        
                    
             
        

def boolify_scheduling_problem(student_preferences, room_capacities):
    """
    Convert a quiz room scheduling problem into a Boolean formula.

    student_preferences: a dictionary mapping a student name (string) to a list
                         of room names (strings) that work for that student

    room_capacities: a dictionary mapping each room name to a positive integer
                     for how many students can fit in that room

    Returns: a CNF formula encoding the scheduling problem, as per the
             lab write-up

    We assume no student or room names contain underscores.
    """
    return desired_sessions(student_preferences) + exactly_once(student_preferences) + no_overscribed(student_preferences, room_capacities)
            


if __name__ == '__main__':
    import doctest
    _doctest_flags = doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS
    doctest.testmod(optionflags=_doctest_flags)
    
    

    
    