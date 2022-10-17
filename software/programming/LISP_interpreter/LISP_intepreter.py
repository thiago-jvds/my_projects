"""6.009 Lab 9: Carlae Interpreter Part 2"""

import sys
sys.setrecursionlimit(10_000)
import doctest

###########################
# Carlae-related Exceptions #
###########################


class CarlaeError(Exception):
    """
    A type of exception to be raised if there is an error with a Carlae
    program.  Should never be raised directly; rather, subclasses should be
    raised.
    """

    pass


class CarlaeSyntaxError(CarlaeError):
    """
    Exception to be raised when trying to evaluate a malformed expression.
    """

    pass


class CarlaeNameError(CarlaeError):
    """
    Exception to be raised when looking up a name that has not been defined.
    """

    pass


class CarlaeEvaluationError(CarlaeError):
    """
    Exception to be raised if there is an error during evaluation other than a
    CarlaeNameError.
    """

    pass

############################
# Tokenization and Parsing #
############################

def number_or_symbol(x):
    """
    Helper function: given a string, convert it to an integer or a float if
    possible; otherwise, return the string itself

    >>> number_or_symbol('8')
    8
    >>> number_or_symbol('-5.32')
    -5.32
    >>> number_or_symbol('1.2.3.4')
    '1.2.3.4'
    >>> number_or_symbol('x')
    'x'
    """
    try:
        return int(x)
    except ValueError:
        try:
            return float(x)
        except ValueError:
            return x

def tokenize(source):
    """
    Splits an input string into meaningful tokens (left parens, right parens,
    other whitespace-separated values).  Returns a list of strings.

    Arguments:
        source (str): a string containing the source code of a Carlae
                      expression
                      
    >>> tokenize("(cat (dog (tomato)))")
    ['(', 'cat', '(', 'dog', '(', 'tomato', ')', ')', ')']
    """
    lines = source.splitlines()
    
    tmp = []
    while lines:
        line = lines.pop(0)
        
        no_space = line.split()
        
        comment = False
        while no_space:
            
            ele = no_space.pop(0)
            number = ''
            flag = False
            
            while ele:
                
                if comment:
                    break
                
                char = ele[0]
                
                # if open paranthesis
                if char == '(':
                    tmp.append(char)
                    ele = ele[1:]
                    continue
                
                # if comment
                if char == '#':
                    comment = True
                    break
                
                # if close parenthesis
                if char == ')':
                    
                    if number and not flag:
                        tmp.append(number)
                        flag = True
                        
                    tmp.append(char)
                    ele = ele[1:]
                    continue
                    
                    
                # number has smth
                elif number:
                    number += char
                    ele = ele[1:]
                    continue
                
                # sign and/or numbers    
                else:
                    number = char
                    ele = ele[1:]
                    
            if number and not flag and not comment:
                tmp.append(number)
            
    return tmp

def get_limits(tokens, initial_index):
    '''
    Returns the index of the final parenthesis for a given token. 
    
    >>> get_limits(['(', 'cat', '(', 'dog', '(', 'tomato', ')', ')', ')'], 2)
    7
    
    >>> get_limits(['(', 'call', '(', 'function', '(', ')', ')', ')'], 4)
    5
    '''
    
    open_par = 0
    i = initial_index
    
    while True:
        
        if tokens[i] == '(':
            open_par += 1
            
        elif tokens[i] == ')':
            open_par -= 1
            
            if open_par == 0:
                break
            
        i += 1
    
    return i   
    
def check_parenthesis(tokens):
    '''
    Check if parenthesis are correct
    
    >>> check_parenthesis(['(', 'cat', '(', 'dog', '(', 'tomato', ')', ')', ')'])
    False
    
    >>> check_parenthesis(['(', 'cat', '(', 'dog', '(', 'tomato', ')', ')', ')', ')'])
    True
    
    >>> check_parenthesis(['6.28'])
    False
    
    >>> check_parenthesis(['(', '(', 'missing-paren'])
    True
    
    >>> check_parenthesis(["(","adam","adam","chris","duane",")",")"])
    True
    
    '''
    stack = []  
    
    flag = False
    
    for char in tokens:
        if char == '(':
            stack.append(char)
            
        elif char == ')':
            try:
                tmp = stack.pop()
            except:
                flag = True
                break
            
            if tmp == '(':
                continue
            else:
                flag = True
                break
                
    if stack or flag:
        return True
    return False

def parse(tokens, repl=False):
    """
    Parses a list of tokens, constructing a representation where:
        * symbols are represented as Python strings
        * numbers are represented as Python ints or floats
        * S-expressions are represented as Python lists

    Arguments:
        tokens (list): a list of strings representing tokens
        
    >>> parse(['(', 'cat', '(', 'dog', '(', 'tomato', ')', ')', ')'])
    ['cat', ['dog', ['tomato']]]
    
    >>> parse(['2'])
    2
    
    >>> parse(['x'])
    'x'
    
    >>> parse(['bare-name'])
    'bare-name'
    
    >>> parse(['(', '+', '2', '(', '-', '5', '3', ')', '7', '8', ')'])
    ['+', 2, ['-', 5, 3], 7, 8]
    """
    
    x = number_or_symbol(tokens[0])
    
    if len(tokens) == 1: 
    # if int/float
        if isinstance(x, int) or isinstance(x, float):
            return x
        
        #if symbol
        elif x not in ['(', ')']:
            return x
    
    if check_parenthesis(tokens) or tokens[0] != '(':
        if repl:
            return "Malformed expression"
        raise CarlaeSyntaxError
   
    def parse_expression(index):
        
        #------base case------# 
        
        x = number_or_symbol(tokens[index])
        
        # if int/float
        if isinstance(x, int) or isinstance(x, float):
            return x, index+1
        
        # if symbol
        elif x not in ['(', ')']:
            return x, index+1
            
            
        #-------recursive call------#         
        else:
            
            final_index = get_limits(tokens, index)
            
            if final_index == index+1:
                return [], final_index+1

            op, i1 = parse_expression(index+1)

            tmp = [op]
            
            while i1 != final_index:
                E, i1 = parse_expression(i1)
                tmp.append(E)

            return tmp, i1+1
                
        
    
    tree, next_index = parse_expression(0)
    return tree

def is_symbol(expression):
    
    return expression in ['*', '/', '+', '-']
       
def REPL():
    inp = 'XXXXX'
    Global = Environment(builtins)
    args = sys.argv
    
    defs = args[1:]
    for expr in defs:
        evaluate_file(expr, env=Global)
    
    
    while True:
        inp = input('in> ')
        
        if inp == 'EXIT':
            break
        w = (parse(tokenize(inp), repl=True))
        
        if w == "Malformed expression": 
            print('   out> ', w)
            print('\n')
            continue
             
        print('   out> ', evaluate(w, env=Global, repl=True))
        print('\n')
        
######################
# Built-in Functions #
######################
def mul(L):
    r = 1
    for e in L:
        r *= e
        
    return r

def div(L, repl=False):
    
    if len(L) == 0:
        if repl:
            return 'No argument to divide'
        raise CarlaeEvaluationError
    
    else:
        
        r = L[0]
        for i in range(1,len(L)):
            r /= L[i]
            
        return r
    
def comparison(op):
    '''
    op = ['=?', '>', '>=', '<', '<=']
    '''
    
    def comp(L):
        
        if op == '=?':
            
            for i in range(1,len(L)):
                
                if L[i-1] != L[i]:
                    return False
                
            return True
        
        elif op == '>':
            
            for i in range(1,len(L)):
                
                if L[i-1] <= L[i]:
                    return False
                
            return True
                
        elif op == '>=':
            
            for i in range(1,len(L)):
                
                if L[i-1] < L[i]:
                    return False
                
            return True
        
        elif op == '<':
            
            for i in range(1,len(L)):
                
                if L[i-1] >= L[i]:
                    return False
                
            return True
        
        elif op == '<=':
            
            for i in range(1,len(L)):
                
                if L[i-1] > L[i]:
                    return False
                
            return True
        
    return comp

def not_op(L, repl=False):
    
    if len(L) != 1:
        
        if repl:
            return 'not operator cannot get more than one argument'
        
        else:
            
            raise CarlaeEvaluationError
        
    else:
        
        return not L[0]

def head(pair, repl=False):

    if len(pair) != 1 or not isinstance(pair[0], Pair):
        
        if repl:
            
            return "incorret number of arguments for head"
        
        else:
            raise CarlaeEvaluationError
        
    else:
        
        return pair[0].head
    
def tail(pair, repl=False):

    if len(pair) != 1 or not isinstance(pair[0], Pair):
        
        if repl:
            
            return "incorret number of arguments for tail"
        
        else:
            
            raise CarlaeEvaluationError
        
    else:
        
        return pair[0].tail
        
class Pair:
    
    def __init__(self, L, repl=False):
        
        if len(L) != 2:
            
            if repl:
                
                return "Incorret number of arguments for Pair"
            
            else:
                
                raise CarlaeEvaluationError
            
        else:
            
            self.head = L[0]
            self.tail = L[1]
            
            
    def set_final_element(self, val):
        
        if not isinstance(self.tail, Pair):
            
            self.tail = val
            
        else:
            
            self.tail.set_final_element(val)
        
    def set_item(self, item):
        self.head = item
            
    def copy(self):
        new_head = self.head
        if not isinstance(self.tail, Pair):

            new_tail = self.tail
            
            return Pair([new_head, new_tail])
        
        return Pair([new_head, self.tail.copy()])
    

def list_op(L):
    
    if len(L) == 0:
        
        return '@NONE'
    else:
        
        return Pair([L[0], list_op(L[1:])])   
    
def is_list(L, repl=False):
    
    if not isinstance(L, list): L_ = [L]
    else:   L_ = L
    
    if len(L_) != 1: 
        
        if repl:
            
            return 'Incorret number of arguments for list?'
        
        else:
            
            raise CarlaeEvaluationError
    
    else:

        if L_[0] == '@NONE': return True
        
        elif not isinstance(L_[0], Pair): 
            return False
        
        elif isinstance(L_[0], Pair) and L_[0].tail == '@NONE': return True
        
        else: 
            return is_list(L_[0].tail)

def length(L, repl=False):
    
    if not is_list(L): 
        
        if repl:
            
            return 'length function cannot be called in non-list objects'
        
        else:
            
            raise CarlaeEvaluationError
        
    else:
        
        if not isinstance(L, list): L_ = [L]
        else: L_ = L
        
        counter = 0
        
        curr = L_[0]
        
        # while not None
        while curr != '@NONE':
            
            counter += 1
            curr = curr.tail
            
        return counter
    
def nth(L, repl=False):
    
    ilist = L[0]
    index = L[1]
    
    if isinstance(ilist, Pair) and not isinstance(ilist.tail, Pair):
            
        if index != 0:
            
            if repl:
            
                return 'Index out of bounds'
        
            else:
            
                raise CarlaeEvaluationError
            
        else:
            
            return ilist.head
    
    elif not is_list(ilist):
        
        if repl:
            
            return 'first argument for nth must be a list'
        
        else:
            
            raise CarlaeEvaluationError
        
    else:
        
        if length(ilist) <= index:
            
            if repl:
            
                return 'Index out of bound'
        
            else:
            
                raise CarlaeEvaluationError
            
            
        counter = 0 
        e = ilist.head
        curr = ilist
        
        while counter != index:
            
            curr = curr.tail
            e = curr.head
            counter += 1
            
        return e
    
def concat(L, repl=False):
    
    if L == []: return '@NONE'
    
    if not is_list(L[0]): 
        
        if repl:
            
            return f'object {L[0]} is not a list'
        
        else:
            
            raise CarlaeEvaluationError
    
    if not isinstance(L, list): L_ = [L]
    else:   L_ = L
    
    if len(L_) == 1 and L_[0] != '@NONE': 
        return L_[0].copy()
    
    elif len(L_) == 0: return '@NONE'
    
    else:
        
        # get last element
        if L_[0] == '@NONE':
            return concat(L_[1:],  repl=repl)
        
        else:

            new_copy = L_[0].copy()
            
            new_copy.set_final_element(concat(L_[1:], repl=repl))
            
            return new_copy

def Map(L, repl=False):
    
    func = L[0]
    itemlist = L[1]
    
    if not is_list(itemlist): 
        if repl:
            return 'Not an item'
        else:
            print(itemlist)
            raise CarlaeEvaluationError
    
    if itemlist == '@NONE': return '@NONE'
    
    return Pair([func([itemlist.head]), Map([func, itemlist.tail])])

def Filter(L, repl=False):
    
    func = L[0]
    itemlist = L[1]
    
    if not is_list(itemlist): 
        if repl:
            return 'Not an item'
        else:
            raise CarlaeEvaluationError
        
    if itemlist == '@NONE': return '@NONE'
    
    if itemlist.head == '@NONE':
        tmp = 'nil'
    else:
        tmp = itemlist.head
    # print(f'tring filter at item {itemlist.head} with func {func}')
    if func([tmp]) is True:
        return Pair([tmp, Filter([func, itemlist.tail])])
    else:
        return Filter([func, itemlist.tail])
    
def Reduce(L, repl=False):
    
    func = L[0]
    itemlist = L[1]
    initial_value = L[2]
    
    if not is_list(itemlist): 
        if repl:
            return 'Not an item'
        else:
            raise CarlaeEvaluationError
        
    if itemlist == '@NONE': return initial_value
    
    new_value = func([initial_value, itemlist.head])
    
    return Reduce([func, itemlist.tail, new_value])

def begin(L, repl=False):
    
    return L[-1]
        
carlae_builtins = {
    "+": sum,
    "-": lambda args: -args[0] if len(args) == 1 else (args[0] - sum(args[1:])),
    "*": mul,
    "/": div,
    '=?': comparison('=?'),
    '>': comparison('>'),
    '>=': comparison('>='),
    '<': comparison('<'),
    '<=': comparison('<='),
    'not': not_op,
    '@t': True,
    '@f': False,
    'pair': Pair,
    'head':head,
    'tail':tail,
    'nil':'@NONE',
    'list':list_op,
    'list?':is_list,
    'length': length,
    'nth': nth,
    'concat': concat,
    'map':Map,
    'filter':Filter,
    'reduce':Reduce,
    'begin':begin
}

#################
#    CLASSES    #
#################
class Environment():
    def __init__(self, parent):
        self.vars = {}
        self.parent = parent
        
    def new_variable(self, name, expre):
        self.vars[name] = expre
        return self.vars[name]
    
    def get_value(self, var, repl):

        if self.vars.get(var, None) is not None:
            return self.vars[var]

        else:
            return self.parent.get_value(var, repl) 
        
    def is_value(self, var):
        if self.vars.get(var, None) is not None:
            return True

        else:
            return self.parent.is_value(var) 
        
        
    def bind_vars(self, args, params):
        
        for i in range(len(args)):
            
            self.vars[params[i]] = args[i]
            
    def first_level(self, var):
        
        return var in self.vars
    
    def delete_var(self, var):
        
        val = self.vars[var]
        del self.vars[var]
        return val
    
    def set_var(self, var, value):
        
        if self.vars.get(var, None) is None:
            return self.parent.set_var(var, value)
        
        self.vars[var] = value
        return value
        
class Builtins_Environment():
    def __init__(self):
        self.vars = carlae_builtins
        
    def get_value(self, var, repl):
        
        # print('var is', var)
        if self.vars.get(var, None) is not None:
            return self.vars[var]
        
        else:
            
            if repl:
                return f'Var {var} is not defined'
            else:
                raise CarlaeNameError
    
    def is_value(self, var):
        
        if self.vars.get(var, None) is not None:
            return True
        
        else:
            return False
        
    def set_var(self, var, value):
        
        raise CarlaeNameError
                
builtins = Builtins_Environment()

class UserDefinedFunctions():
    def __init__(self, parameters, body, env):
        self.parameters = parameters
        self.body = body
        self.env = env

    def __call__(self, args, repl=False):
            
        if len(args) != len(self.parameters):   
             
            if repl:
                return 'Incorret number of parameters' 
            else:
                raise CarlaeEvaluationError
    
        eval_args = []
        for arg in args:  
            eval_args.append(evaluate(arg, env=self.env, repl=repl))
        
        new_env = Environment(self.env)
        
        new_env.bind_vars(eval_args, self.parameters)
        
        return evaluate(self.body, env=new_env, repl=repl)
        
##############
# Evaluation #
##############
    
def evaluate(tree, env=None, repl=False):
    """
    Evaluate the given syntax tree according to the rules of the Carlae
    language.

    Arguments:
        tree (type varies): a fully parsed expression, as the output from the
                            parse function
    """
    
    if env is None:
        Global = Environment(builtins)
        env = Environment(Global)
        
    if isinstance(tree, str):
        
        if tree == '@NONE':
            tmp = 'nil'
        else: 
            tmp = tree
            
        return env.get_value(tmp, repl=repl)
    
    # number
    elif isinstance(tree, int) or isinstance(tree, float):
        return tree
    
    # defined function
    elif isinstance(tree, UserDefinedFunctions):
        return tree
    
    elif isinstance(tree, list) and len(tree) == 0:
        
        if repl:
            return 'Empty expression'
        else:
            raise CarlaeEvaluationError
    
    elif isinstance(tree, Pair): return tree
    # created new function
    elif tree[0] == 'function':
            
            parameters = tree[1]
            body = tree[2]
            
            return UserDefinedFunctions(parameters, body, env)
    
    # list   
    else:
        
        first = tree[0]
        
        if first == ':=':     
            
            # if short function definition
            if type(tree[1]) == list:
                
                name = tree[1][0]
                params = tree[1][1:]     
                body = tree[2]
                
                function = UserDefinedFunctions(params, body, env)
                
                return env.new_variable(name, function)    
                
            return env.new_variable(tree[1], evaluate(tree[2], env=env, repl=repl))
        
        elif first == 'del':
            
            var = tree[1]
            
            if env.first_level(var):
                
                return env.delete_var(var)
            
            else:
                
                if repl:
                    
                    return f'Var {var} is not defined locally'
                
                else:
                    
                    raise CarlaeNameError
                
        elif first == 'let':
            
            Vars = tree[1]
            body = tree[2]
            
            new_env = Environment(env)
            
            for pair in Vars:
                var = pair[0]
                val = evaluate(pair[1], env=env,repl=repl)
                new_env.vars[var] = val
                
            return evaluate(body, env=new_env, repl=repl)       
        
        elif first == 'set!':
            var = tree[1]
            expr = tree[2]
            
            val = evaluate(expr, env=env, repl=repl)
            
            return env.set_var(var, val)
            
        
        elif first == 'if':
            
            cond = tree[1]
            
            if evaluate(cond, env=env, repl=repl):
                
                return evaluate(tree[2], env=env, repl=repl)
            
            else:
                
                return evaluate(tree[3], env=env, repl=repl)
            
        elif first == 'and':
            
            rest = tree[1:]
            
            while rest:
                
                exp = rest.pop(0)
                
                if not evaluate(exp, env=env, repl=repl):
                    
                    return False
                
            return True
        
        elif first == 'or':
            
            rest = tree[1:]
            
            while rest:
                
                exp = rest.pop(0)
                
                if evaluate(exp, env=env, repl=repl):
                    
                    return True
                
            return False 
        
        
        elif type(first) == list:
            op = evaluate(first, env=env, repl=repl)
            
        elif env.is_value(first):
            op = env.get_value(first, repl) 
            
        elif isinstance(first, str):
            raise CarlaeNameError
        
        else:
            
            if repl:
                return 'Symbol not in builtins!'
            else:
                raise CarlaeEvaluationError
        
        tmp = []
        for item in tree[1:]:
            tmp.append(evaluate(item, env=env, repl=repl))
            
        return op(tmp)      
        
def result_and_env(tree, env=None):
    
    
    if env is None:
        Global = Environment(builtins)
        env = Global
    
    return (evaluate(tree, env=env, repl=False), env)
        
def evaluate_file(file, env=None):
    
    if env is None:
        Global = Environment(builtins)
        env = Global
        
    with open(file, 'r') as f:
        lines = f.read()
        tokens = tokenize(lines)
        parsed = parse(tokens)
        return evaluate(parsed, env=env, repl=False)



if __name__ == "__main__":
    # code in this block will only be executed if lab.py is the main file being
    # run (not when this module is imported)

    # uncommenting the following line will run doctests from above
    # doctest.testmod()
    REPL()  
    

    
