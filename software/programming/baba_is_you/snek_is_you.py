"""6.009 Lab 10: Snek Is You Video Game"""

import doctest

# NO ADDITIONAL IMPORTS!

# All words mentioned in lab. You can add words to these sets,
# but only these are guaranteed to have graphics.
NOUNS = {"SNEK", "FLAG", "ROCK", "WALL", "COMPUTER", "BUG"}
PROPERTIES = {"YOU", "WIN", "STOP", "PUSH", "DEFEAT", "PULL"}
WORDS = NOUNS | PROPERTIES | {"AND", "IS"}

# Maps a keyboard direction to a (delta_row, delta_column) vector.
direction_vector = {
    "up": (-1, 0),
    "down": (+1, 0),
    "left": (0, -1),
    "right": (0, +1),
}
   
class Board:
    
    def __init__(self, level_description):
        self.dump = level_description
        self.board = []
        self.objs = {}
        self.nouns = {}
        self.props = {}
        self.conjs = {}
        self.width = len(level_description)
        
        
        for ir in range(len(level_description)):
            tmp = []
            for ic in range(len(level_description[ir])):
                tmp2 = []
                for elt in level_description[ir][ic]: 
                    
                    # Object
                    if elt not in WORDS:
                        
                        if self.objs.get(elt) is None: self.objs[elt] = []
                        obj = Object(elt, (ir, ic))
                        
                        tmp2.append(obj)
                        self.objs[elt].append(obj)
                    
                    # Text 
                    elif elt in NOUNS:
                        if self.nouns.get(elt) is None: self.nouns[elt] = []
                        text = Text(elt, (ir,ic))
                        
                        tmp2.append(text)
                        self.nouns[elt].append(text)
                        
                    elif elt in PROPERTIES:
                        if self.props.get(elt) is None: self.props[elt] = []
                        text = Text(elt, (ir,ic))
                        
                        tmp2.append(text)
                        self.props[elt].append(text)
                        
                    else:
                        if self.conjs.get(elt) is None: self.conjs[elt] = []
                        text = Text(elt, (ir,ic))
                        
                        tmp2.append(text)
                        self.conjs[elt].append(text)
                        
                tmp.append(tmp2)
            self.board.append(tmp)
            
        self.getting_rules()
                        
    def new_rules(self):
        
        rules = {
                    "PUSH": WORDS.copy(),
                    "YOU": set(),
                    "STOP":set(),
                    "WIN":set(),
                    "DEFEAT":set(),
                    "PULL":set()
                }         
        
        return rules
        
    def assign_rule(self, pred, subj):

        try:
            self.rules[pred] |= {subj.lower()}
            return None
        
        # noun into noun
        except KeyError:
            
            return pred,subj
    
    def get_changes(self, pred, subj):  
        '''
        Get all objects that should be changed according to
        a given rule (pred, subj) and return them as a list
        of tuples of (obj, pred)
        '''   
        
        subj_objs = []
        try:
            for obj in self.objs[subj.lower()]:
                subj_objs.append(obj)
        except KeyError:
            return []
            
        del self.objs[subj.lower()]  
        
        res = []
        
        while subj_objs:
            
            obj = subj_objs.pop()
            res.append((obj, pred))
         
        return res
        
    def update_nouns(self):
        
        tmp = []
        for pred, subj in self.noun_into_noun:
             
            if subj.lower() in self.objs:
                tmp.append((pred,subj))
                
        changes = []
        
        for pred, subj in tmp:
            changes += self.get_changes(pred, subj)
            
        for obj, pred in changes:
            x,y = obj.pos
            self.dump[x][y].remove(obj.id)
            self.dump[x][y].append(pred.lower())
            obj.id = pred.lower()

            if self.objs.get(pred.lower(), None) is None: self.objs[pred.lower()] = []
            self.objs[pred.lower()].append(obj)
                      
                
    def getting_rules(self):
        
        def sort_by_pos(obj):
            
            x,y = obj.pos
            return self.width*y+x
        
        # sort
        self.conjs["IS"] = sorted(self.conjs["IS"], key=sort_by_pos)
        
        self.rules = self.new_rules()
        
        self.noun_into_noun = []
        
        for is_clause in self.conjs["IS"]:
            sents = self.get_subje_pred(is_clause)
            
            for subj, pred in sents:
                if subj == [] or pred == []:
                    continue
                
                else:
                    for subject in subj:    
                        for predicate in pred:
                            
                            pair = self.assign_rule(predicate, subject)
                            
                            if pair: self.noun_into_noun.append(pair)
        
        # default value for no YOU object
        if not self.rules["YOU"]:
            self.rules["YOU"] = -1
            return                
                
    def get_subje_pred(self, is_obj):
        ir,ic = is_obj.pos
        
        
        def search(search_set, col, incre):
            '''
            Checks the position according to col and incre, to get strings
            that are in search_set
            
            Parameters
            ----------
                search_set : set
                    Set which is going to be used to check 
                    
                col : bool
                    Whether it is checking columns in increasing order
                    
                incre : int
                    (+1, -1) Define how it checks in the list 
                    
            Returns
            -------
                List with all objects satisfying the constraints
            '''
            i = incre
            
            if col:
                try:
                    curr_list = self.dump[ir][ic+i]
                except IndexError:
                    return []
                
                tmp = []
                flag = True
                
                while True:
                    
                    if curr_list == []:
                        return tmp
                    
                    for curr in curr_list:
                        if curr == "AND":
                            flag = True
                            
                        else:
                            if flag:
                                flag = False
                                
                                if curr in search_set:
                                    tmp.append(curr)
                                
                                else:
                                    return tmp
                            else:
                                return tmp
                        
                    i += incre
                    
                    if self.out_of_bound(ir, ic+i): 
                        return tmp                    
                    
                    curr_list = self.dump[ir][ic+i]

            else:
                try:
                    curr_list = self.dump[ir+i][ic]
                except IndexError:
                    return []
                
                tmp = []
                flag = True
                while True:
                    
                    if curr_list == []:
                        return tmp
                    
                    for curr in curr_list:
                        
                        if curr == "AND":
                            flag = True
                            
                        else:
                            if flag:
                                flag = False
                                
                                if curr in search_set:
                                    tmp.append(curr)
                                else:
                                    return tmp                                
                            else:
                                return tmp
                        
                    i += incre
                    
                    if self.out_of_bound(ir+i, ic): 
                        return tmp
                    
                    try:
                        curr = self.dump[ir+i][ic]
                    except IndexError:
                        return tmp
                
        left_s = search(NOUNS | {"AND"}, True, -1)   
        up_s = search(NOUNS | {"AND"}, False, -1)
        
        right_p = search(WORDS - {"IS"}, True, 1)
        down_p = search(WORDS - {"IS"}, False, 1)   
        
        return (left_s, right_p), (up_s, down_p)
                                     
    def move_player(self, direction):
        
        dx, dy = direction_vector[direction]
        
        if self.rules["YOU"] == -1:
            return
        objs = []  
        for you in self.rules["YOU"]:
            
            # if obj does not exist
            if you not in self.objs: continue
            
            for you_obj in self.objs[you]:
                _, moves = self.move(you_obj, dx,dy)
                
                if moves != -1:
                    
                    for move in moves:
                        obj, pos, new_pos = move
                        objs.append(obj)
                        self.moving(obj, pos, new_pos)
        
        for obj in objs:
            obj.pushed = False
         
    
            
    def is_stop(self, x_, y_):
        
        for obj in self.board[x_][y_]:
            
            if obj.id in self.rules["STOP"] and obj.id not in self.rules["PUSH"]:
                
                return True

        return False
    
    def moving(self, obj, pos, new_pos):
        x,y = pos
        x_, y_ = new_pos
        self.board[x][y].remove(obj)
        self.board[x_][y_].append(obj)
        self.dump[x_][y_].append(obj.id) 
        self.dump[x][y].remove(obj.id)
        obj.pos = x_,y_       
    
    def move(self, obj, dx, dy, sofar=None):
        if sofar is None:
            sofar = []
        
        if sofar == -1:
            return False, -1
            
        x,y = obj.pos
        x_, y_ = x+dx, y+dy
        
        if not self.out_of_bound(x_, y_) and not self.is_stop(x_, y_):
                    
            # push
            for new_obj in self.board[x_][y_]:
            
                if new_obj.id in self.rules["PUSH"] and not new_obj.pushed:
                    new_obj.pushed = True
                    pushable, new = self.move(new_obj, dx,dy, sofar)
                    
                    if not pushable:
                        new_obj.pushed = False
                        return False, -1
                    else:
                        sofar = new
                        
            sofar.append((obj,(x,y), (x_, y_)))          
            
            # pull
            if not self.out_of_bound(x-dx, y-dy):
                
                for new_obj in self.board[x-dx][y-dy]:
      
                    if new_obj.id in self.rules["PULL"] and not new_obj.pushed:
                        new_obj.pushed = True
                        pushable, new = self.move(new_obj, dx,dy, sofar)
                        
                        if pushable:
                            sofar = new
                        else:
                            new_obj.pushed = False
                   
            return True, sofar        
        
        else:
            return False, -1   
                    
    def out_of_bound(self, x_, y_):
        
        if x_<0 or y_<0: return True
        
        try:
            self.dump[x_][y_]
            return False
        except IndexError:
            return True
        
    def defeat(self):
        
        if self.rules["YOU"] == -1:
            return 
        
        tmp = [] 
        for you in self.rules["YOU"]:
            
            if you not in self.objs: continue
            for you_obj in self.objs[you]:
                tmp.append(you_obj)
            
            while tmp:
                you_obj = tmp.pop()  
                x,y = you_obj.pos
                
                flag = False
                for obj in self.board[x][y]:
                
                    if obj.id in self.rules['DEFEAT']:
                        flag = True
                        
                    if flag:
                        self.board[x][y].remove(you_obj)
                        self.dump[x][y].remove(you_obj.id)
                        self.objs[you].remove(you_obj)
                        break
    
    def victory(self):
        
        if self.rules["YOU"] == -1:
            return False
        
        for you in self.rules['YOU']:
            
            if you not in self.objs: continue
            for you_obj in self.objs[you]:
                x,y = you_obj.pos
                
                for obj in self.board[x][y]:
                    
                    if obj.id in self.rules["WIN"]:
                        return True
                    
            return False
                
class Object():
    
    def __init__(self, idt, pos):
        self.id = idt
        self.pos = pos
        self.pushed = False
        
class Text():
    
    def __init__(self, idt, pos):
        self.pos = pos
        self.id = idt
        self.pushed = False
    
    


def new_game(level_description):
    """
    Given a description of a game state, create and return a game
    representation of your choice.

    The given description is a list of lists of lists of strs, where UPPERCASE
    strings represent word objects and lowercase strings represent regular
    objects (as described in the lab writeup).

    For example, a valid level_description is:

    [
        [[], ['snek'], []],
        [['SNEK'], ['IS'], ['YOU']],
    ]

    The exact choice of representation is up to you; but note that what you
    return will be used as input to the other functions.
    """
    return Board(level_description)


def step_game(game, direction):
    """
    Given a game representation (as returned from new_game), modify that game
    representation in-place according to one step of the game.  The user's
    input is given by direction, which is one of the following:
    {'up', 'down', 'left', 'right'}.

    step_game should return a Boolean: True if the game has been won after
    updating the state, and False otherwise.
    """
    
    game.move_player(direction)
    game.getting_rules()
    game.update_nouns()
    game.defeat()
    return game.victory()


def dump_game(game):
    """
    Given a game representation (as returned from new_game), convert it back
    into a level description that would be a suitable input to new_game.

    This function is used by the GUI and tests to see what your game
    implementation has done, and it can also serve as a rudimentary way to
    print out the current state of your game for testing and debugging on your
    own.
    """
    return game.dump

if __name__ == "__main__":
    
    test_case = [[['computer'], ['rock', 'snek'], []], 
                 [["SNEK"], ["IS"], ["YOU"]], 
                 [["ROCK"], ['IS'], ["PUSH"]],
                 [['COMPUTER'], ['IS'], ["PULL"]]
                 ]
    
    new_g = new_game(test_case)
    step_game(new_g, "right")
    print(dump_game(new_g))
    