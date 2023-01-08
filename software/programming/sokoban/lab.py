# 6.009 Lab 2: Snekoban

#import json
#import typing

# NO ADDITIONAL IMPORTS!


direction_vector = {
    "up": (-1, 0),
    "down": (+1, 0),
    "left": (0, -1),
    "right": (0, +1),
}

def new_position(x,y, direction):
    '''
    return new position
    '''
    dx, dy = direction_vector[direction]

    return (x+dx, y+dy)

class Board:

    def __init__(self, level_description):
        self.board = []
        self.targets = []
        self.computers = []
        self.walls = []
        self.id = 0

        for i in range(len(level_description)):
            tmp = []
            for j in range(len(level_description[i])):
                tmp2=[]
                for e in level_description[i][j]:
                    
                    if e == "player":
                        self.player = Player(i,j)
                    elif e == "target":
                        self.targets.append(Target(i,j))

                    elif e == "computer":
                        self.computers.append(Computer(i,j))

                    elif e == "wall":
                        self.walls.append(Wall(i,j))

                    self.id ^= hash((e,i,j))
                    tmp2.append(e)
                tmp.append(tmp2)
            self.board.append(tmp)

    def __hash__(self):
        return hash(str(self.board))

    def __eq__(self, other):
        return (self.id == other.id)
    
    def copy(self):
        b = Board(self.board)
        return b

    def get_level_description(self):
        return self.board

    def move_player(self, direction, flag=False):

        dx, dy = direction_vector[direction]
        x, y = self.player.get_position()
        x_,y_ = x+dx, y+dy

        # check collision
        if "wall" in self.board[x_][y_]:
            if flag:
                return -1,-1

            return 0

        # check if computer
        elif "computer" in self.board[x_][y_]:
            if flag:
                return self.push(x, y, direction, flag=True)
            self.push(x, y, direction)

        # regular movement
        else:

            if flag:
                b = self.copy()
                b.move_player(direction)
                c = b.copy()
                return (c, direction)

            self.player_pos = (x_, y_)
            self.update(x,y,direction,"player")

    def push(self, x, y, direction, flag=False):
        x_comp, y_comp = new_position(x,y, direction)
        nx_comp, ny_comp = new_position(x_comp, y_comp, direction)

        # check if it is possible:
        if "wall" in self.board[nx_comp][ny_comp] or "computer" in self.board[nx_comp][ny_comp]:
            if flag:
                return (-1,-1)
            
            return 0

        # possible move
        else:
            if flag:
                b = self.copy()
                b.push(x,y, direction)
                c = b.copy()
                return (c, direction)

            self.update(x_comp, y_comp, direction, "computer")
            self.update(x, y, direction, "player")

    def update(self, x, y, direction, object):
        x_, y_ = new_position(x,y, direction)

        self.board[x][y].remove(object)
        self.board[x_][y_].append(object)

    def get_possible_moves(self):
        res = []

        for direction in direction_vector.keys():

            board,move = self.move_player(direction, flag=True)

            if move == -1:
                continue
            else:
                res.append((board,move))


        return res

    def make_fake_move(self, list_of_direction):
        
        pass

    def is_win(self):
        '''
        '''

        if len(self.computers) != len(self.targets):
            return False

        elif len(self.computers) == 0  or len(self.targets) == 0:
            return False

        else:

            for t in self.targets:

                if not t.isFilled(self):
                    return False
                
            return True

class Obj:

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __hash__(self):
        return hash((self.x, self.y))

    def __eq__(self, other):
        if isinstance(other, self):
            return (self.x, self.y) == (other.x, other.y)

class Target:

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def get_position(self):
        return (self.x, self.y)

    
    def isFilled(self, board): 
        return "computer" in board.board[self.x][self.y]     


class Computer(Obj):

    def __init__(self,x,y):
        Obj.__init__(self, x,y)

    def get_position(self):
        return (self.x, self.y)

    def set_position(self, direction):
        x_, y_ = new_position(self.x,self.y, direction)
        self.x = x_
        self.y = y_

class Player(Obj):
    
    def __init__(self, x, y):
        Obj.__init__(self, x,y)

    def get_position(self):
        return (self.x, self.y)

    def set_position(self, direction):
        x_, y_ = new_position(self.x,self.y, direction)
        self.x = x_
        self.y = y_

class Wall(Obj):

    def __init__(self,x,y):
        Obj.__init__(self,x,y)

def new_game(level_description):
    """
    Given a description of a game state, create and return a game
    representation of your choice.

    The given description is a list of lists of lists of strs, representing the
    locations of the objects on the board (as described in the lab writeup).

    For example, a valid level_description is:

    [
        [[], ['wall'], ['computer']],
        [['target', 'player'], ['computer'], ['target']],
    ]

    The exact choice of representation is up to you; but note that what you
    return will be used as input to the other functions.
    """

    return Board(level_description)

def victory_check(game):
    """
    Given a game representation (of the form returned from new_game), return
    a Boolean: True if the given game satisfies the victory condition, and
    False otherwise.
    """
    return game.is_win()

def step_game(game, direction):
    """
    Given a game representation (of the form returned from new_game), return a
    new game representation (of that same form), representing the updated game
    after running one step of the game.  The user's input is given by
    direction, which is one of the following: {'up', 'down', 'left', 'right'}.

    This function should not mutate its input.
    """
    new_board = game.copy()

    new_board.move_player(direction)

    return new_board

def dump_game(game):
    """
    Given a game representation (of the form returned from new_game), convert
    it back into a level description that would be a suitable input to new_game
    (a list of lists of lists of strings).

    This function is used by the GUI and the tests to see what your game
    implementation has done, and it can also serve as a rudimentary way to
    print out the current state of your game for testing and debugging on your
    own.
    """
    return game.get_level_description()

def solve_puzzle(game):
    """
    Given a game representation (of the form returned from new game), find a
    solution.

    Return a list of strings representing the shortest sequence of moves ("up",
    "down", "left", and "right") needed to reach the victory condition.

    If the given level cannot be solved, return None.
    """
    t = BFS(game)

    if t:
        b_hash, parent, moves = t

        return get_path(b_hash, parent, moves)

    return None

def BFS(s):

    seen = set()

    parent = {}

    moves = {}

    parent[s] = None

    Q = [s]

    while Q:

        node = Q.pop(0)
        seen.add(node)

        for board, move in node.get_possible_moves():

            if board not in seen:
                parent[board] = node
                moves[board] = move
                Q.append(board)

            if board.is_win():
                return board, parent, moves


    return None

def get_path(goal, parent, moves):
    '''
    
    '''
    path = []
    h = goal
    
    while parent[h]:
        path.append(moves[h])
        h = parent[h]

    
    return path[::-1]

    
def hash_homomorphic(board, h, direction):
    '''
    Implements Zobrist Hashing
    '''
    prev_xor = h
    dx, dy = direction_vector[direction]




    

if __name__ == "__main__":
    level_description = [
        [["wall"], ["wall"], ["wall"], ["wall"], [], []],
        [["wall"], [], ["target"], ["wall"], [], []],
        [["wall"], [], [], ["wall"], ["wall"], ["wall"]],
        [["wall"], ["target", "computer"], ["player"], [], [], ["wall"]],
        [["wall"], [], [], ["computer"], [], ["wall"]],
        [["wall"], [], [], ["wall"], ["wall"], ["wall"]],
        [["wall"], ["wall"], ["wall"], ["wall"], [], []]
    ]

    board = Board(level_description)

    print(solve_puzzle(board))
    
    
    