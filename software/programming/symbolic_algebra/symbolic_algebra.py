import doctest
from re import L

# NO ADDITIONAL IMPORTS ALLOWED!
# You are welcome to modify the classes below, as well as to implement new
# classes and helper functions as necessary.

class Symbol:
    def __add__(self, other):
        return Add(self, other)
    def __radd__(self, other):
        return Add(other,self)
    
    def __sub__(self, other):
        return Sub(self, other)  
    def __rsub__(self, other):
        return Sub(other, self)
    
    def __mul__(self, other):
        return Mul(self, other) 
    def __rmul__(self, other):
        return Mul(other,self)
    
    def __truediv__(self, other):
        return Div(self, other)
    def __rtruediv__(self, other):
        return Div(other,self)
    
    def __pow__(self, other):
        return Pow(self, other) 
    def __rpow__(self, other):
        return Pow(other,self)
    
    

class Var(Symbol):
    def __init__(self, n):
        """
        Initializer.  Store an instance variable called `name`, containing the
        value passed in to the initializer.
        """
        self.name = n
        self.precedence = float('inf')

    def __str__(self):
        return self.name

    def __repr__(self):
        return "Var(" + repr(self.name) + ")"
    
    def deriv(self, var):
        if self.name == var:
            return Num(1)
        return Num(0)
    
    def simplify(self):
        return Var(self.name)
    
    
    def eval(self, mapping):
        if mapping.get(self.name):
            return mapping[self.name]
        else:
            return self


class Num(Symbol):
    def __init__(self, n):
        """
        Initializer.  Store an instance variable called `n`, containing the
        value passed in to the initializer.
        """
        self.n = n
        self.precedence = float('inf')

    def __str__(self):
        return str(self.n)

    def __repr__(self):
        return "Num(" + repr(self.n) + ")"
    
    def deriv(self, var):
        return Num(0)
    
    def simplify(self):
        return Num(self.n)
    
    def eval(self, mapping):
        return self.n

class BinOp(Symbol):
    def __init__(self, left, right):
        
        if isinstance(left, int) or isinstance(left, float): self.left = Num(left)
        elif isinstance(left, str): self.left = Var(left)
        else: self.left = left
        
        if isinstance(right, int) or isinstance(right, float): self.right = Num(right)
        elif isinstance(right, str): self.right = Var(right)
        else: self.right = right
        
    def __repr__(self):
        return self.ope + "(" + repr(self.left) + ', ' + repr(self.right) + ')'
    
    def __str__(self):
        L = self.left.__str__()
        if self.left.precedence < self.precedence:
            L = "(" + L + ")"
            
        R = self.right.__str__()
        if self.right.precedence < self.precedence or (self.right.precedence == self.precedence and (self.char == ' - '  or self.char == ' / ')):
            R = "(" + R + ")"
            
        return L + self.char + R
    
    def eval(self, mapping):
        if self.ope == 'Add':
            return self.left.eval(mapping) + self.right.eval(mapping)
        
        if self.ope == 'Sub':
            return self.left.eval(mapping) - self.right.eval(mapping)
        
        if self.ope == 'Mul':
            return self.left.eval(mapping) * self.right.eval(mapping)
        
        if self.ope == 'Div':
            return self.left.eval(mapping) / self.right.eval(mapping)
        
        if self.ope == 'Pow':
            return self.left.eval(mapping) ** self.right.eval(mapping)
        
        
        
class Add(BinOp):
    def __init__(self, left, right):
        super().__init__(left,right)
        self.ope = "Add"
        self.char = " + "
        self.precedence = 1
        
    def deriv(self, var):
        return self.left.deriv(var) + self.right.deriv(var)
    
    def simplify(self):
        
        w = Add(self.left.simplify(), self.right.simplify())
        
        if isinstance(w.left, Num) and isinstance(w.right, Num):
            return Num(w.left.n + w.right.n)
        
        elif isinstance(w.left, Num) and w.left.n == 0:
            return w.right.simplify()
        
        elif isinstance(w.right, Num) and w.right.n == 0:
            return w.left.simplify()
          
        return w
    
class Sub(BinOp):
    def __init__(self, left, right):
        super().__init__(left,right)
        self.ope = "Sub"
        self.char = " - "
        self.precedence = 1
        
    def deriv(self, var):
        return self.left.deriv(var) - self.right.deriv(var)
    
    def simplify(self):
        
        w = Sub(self.left.simplify(), self.right.simplify())
        
        if isinstance(w.left, Num) and isinstance(w.right, Num):
            return Num(w.left.n - w.right.n)
        
        elif isinstance(w.right, Num) and w.right.n == 0:
            return w.left.simplify()
        
        return w
        
    
class Mul(BinOp):
    def __init__(self, left, right):
        super().__init__(left,right)
        self.ope = "Mul"
        self.char = " * "
        self.precedence = 2
        
    def deriv(self, var):
        exp1 = Mul(self.left, self.right.deriv(var))
        exp2 = Mul(self.left.deriv(var), self.right)
        return exp2 + exp1
    
    def simplify(self):
        
        w = Mul(self.left.simplify(), self.right.simplify())
        
        if isinstance(w.left, Num) and isinstance(w.right, Num):
            return Num(w.left.n * w.right.n)
        
        elif isinstance(w.left, Num) and w.left.n == 0:
            return Num(0)
        
        elif isinstance(w.right, Num) and w.right.n == 0:
            return Num(0)
        
        elif isinstance(w.left, Num) and w.left.n == 1:
            return w.right.simplify()
        
        elif isinstance(w.right, Num) and w.right.n == 1:
            return w.left.simplify()
        
        return w
        

class Div(BinOp):
    def __init__(self, left, right):
        super().__init__(left,right)
        self.ope = "Div"
        self.char = " / "
        self.precedence = 2
    
    def simplify(self):
        
        w = Div(self.left.simplify(), self.right.simplify())
         
        if isinstance(w.left, Num) and isinstance(w.right, Num):
            return Num(w.left.n / w.right.n)
        
        elif isinstance(w.left, Num) and w.left.n == 0:
            return Num(0)
        
        elif isinstance(w.right, Num) and w.right.n == 1:
            return w.left.simplify()
        
        return w
        
    def deriv(self, var):
        exp1 = Mul(self.left.deriv(var), self.right)
        exp2 = Mul(self.left, self.right.deriv(var))
        sqr = Mul(self.right, self.right)
        S = exp1 - exp2
        return Div(S, sqr)
    
class Pow(BinOp):
    def __init__(self, left, right):
        super().__init__(left, right)
        self.ope = 'Pow'
        self.char = ' ** '
        self.precedence = 3
        
    def deriv(self, var):
        if not isinstance(self.right, Num):
            raise TypeError('Cant take a derivative of non-number exponent')
        
        exp = Mul(self.right, Pow(self.left, Sub(self.right,Num(1))))
        return Mul(exp, self.left.deriv(var))
    
    def simplify(self):
        
        w = Pow(self.left.simplify(), self.right.simplify())
        
        if isinstance(w.left, Num) and isinstance(w.right, Num):
            return Num(w.left.n ** w.right.n) 
        
        elif isinstance(w.right, Num) and w.right.n == 0:
            return Num(1)
        
        elif isinstance(w.right, Num) and w.right.n == 1:
            return w.left
        
        elif isinstance(w.left, Num) and w.left.n == 0:
            return Num(0)
        
        return w
    
    def __str__(self):
        L = self.left.__str__()
        if self.left.precedence <= self.precedence:
            L = "(" + L + ")"
            
        R = self.right.__str__()
        if self.right.precedence < self.precedence or (self.right.precedence == self.precedence and (self.char == ' - '  or self.char == ' / ')):
            R = "(" + R + ")"
            
        
            
        return L + self.char + R
        
        
        
    
    
def expression(string):
    '''
    '''
       
    tokens = tokenize(string)
    return parse(tokens)     
        
        
        
def parse(tokens):   
    
    ops = {
        '+': Add,
        '-': Sub,
        '*': Mul,
        '/': Div,
        '**': Pow
    }
   
    def parse_expression(index):
        
        #------base case------# 
        
        # if index == len(tokens): return
        
        try:
            n = int(tokens[index])
            return Num(n), index+1
        
        except ValueError:
            
            # var
            if tokens[index].isalpha():
                return Var(tokens[index]), index+1
            
            # operation
            elif tokens[index] in ops.keys():
                return ops[tokens[index]], index+1
            
        #-------recursive call------#         
            else:
                # index is (
                # print('index ', index)
                E1, i1 = parse_expression(index+1)
                # print('E1 ', repr(E1))
                # print('i1 ', i1)
 
                # i1 is )
                op, i2 = parse_expression(i1)
                # print('OP ', op)
                # print('i2 ', i2)
                
                # i2 is (
                E2, i3 = parse_expression(i2)
                # print('E2 ', repr(E2))
                # print('i3 ', i3)
                
                # i3 is )
                return op(E1, E2), i3+1
                
        
    
    parsed_expression, next_index = parse_expression(0)
    return parsed_expression
        
def tokenize(string):
    '''
    Args
        a string 
            
    Returns
        a list of meaningful tokens (parentheses, variable names, numbers, or operands)
        
    >>> tokenize("(x * (200 + 3.0))")
    ['(', 'x', '*', '(', '200', '+', '3.0', ')', ')']
    
    >>> tokenize("(3 ** x)")
    ['(', '3', '**', 'x', ')']
    
    >>> tokenize('((x * y) * z)')
    ['(', '(', 'x', '*', 'y', ')', '*', 'z', ')']
    '''
    
    # get rid of blank spaces
    no_spaces = string.split(' ')
    
    tmp = []
    while no_spaces:
        e = no_spaces.pop(0)
        
        number = ''
        flag = False
        while e:
            
            if len(e) == 1 and number == '':
                tmp.append(e)
                break
            
            char = e[0]
            
            # if open paranthesis
            if char == '(':
                tmp.append(char)
                e = e[1:]
                continue
            
            # if close parenthesis
            if char == ')':
                
                if number and not flag:
                    tmp.append(number)
                    flag = True
                    
                tmp.append(char)
                e = e[1:]
                continue
                
                
            # number has smth
            elif number:
                number += char
                e = e[1:]
                continue
            
            # sign and/or numbers    
            else:
                number = char
                e = e[1:]
                
        if number and not flag:
            tmp.append(number)
            
    return tmp
        
    

        

if __name__ == "__main__":
    
    exp = expression('(((x + A) * (y + z)) ** 2)')
    # print(repr(exp))
    # doctest.testmod()
    print(repr(exp))
    


    