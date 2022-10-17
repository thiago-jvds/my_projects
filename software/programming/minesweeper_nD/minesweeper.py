#!/usr/bin/env python3
"""6.009 Lab -- Six Double-Oh Mines"""

import doctest

# NO ADDITIONAL IMPORTS ALLOWED!


def dump(game):
    """
    Prints a human-readable version of a game (provided as a dictionary)
    """
    for key, val in sorted(game.items()):
        if isinstance(val, list) and val and isinstance(val[0], list):
            print(f'{key}:')
            for inner in val:
                print(f'    {inner}')
        else:
            print(f'{key}:', val)


# 2-D IMPLEMENTATION

def new_game_2d(num_rows, num_cols, bombs):
    """
    Start a new game.

    Return a game state dictionary, with the 'dimensions', 'state', 'board' and
    'visible' fields adequately initialized.

    Parameters:
       num_rows (int): Number of rows
       num_cols (int): Number of columns
       bombs (list): List of bombs, given in (row, column) pairs, which are
                     tuples

    Returns:
       A game state dictionary

    >>> dump(new_game_2d(2, 4, [(0, 0), (1, 0), (1, 1)]))
    board:
        ['.', 3, 1, 0]
        ['.', '.', 1, 0]
    dimensions: (2, 4)
    state: ongoing
    visible:
        [False, False, False, False]
        [False, False, False, False]
    """

    return new_game_nd((num_rows, num_cols), bombs)


def dig_2d(game, row, col):
    """
    Reveal the cell at (row, col), and, in some cases, recursively reveal its
    neighboring squares.

    Update game['visible'] to reveal (row, col).  Then, if (row, col) has no
    adjacent bombs (including diagonally), then recursively reveal (dig up) its
    eight neighbors.  Return an integer indicating how many new squares were
    revealed in total, including neighbors, and neighbors of neighbors, and so
    on.

    The state of the game should be changed to 'defeat' when at least one bomb
    is visible on the board after digging (i.e. game['visible'][bomb_location]
    == True), 'victory' when all safe squares (squares that do not contain a
    bomb) and no bombs are visible, and 'ongoing' otherwise.

    Parameters:
       game (dict): Game state
       row (int): Where to start digging (row)
       col (int): Where to start digging (col)

    Returns:
       int: the number of new squares revealed

    >>> game = {'dimensions': (2, 4),
    ...         'board': [['.', 3, 1, 0],
    ...                   ['.', '.', 1, 0]],
    ...         'visible': [[False, True, False, False],
    ...                  [False, False, False, False]],
    ...         'state': 'ongoing'}
    >>> dig_2d(game, 0, 3)
    4
    >>> dump(game)
    board:
        ['.', 3, 1, 0]
        ['.', '.', 1, 0]
    dimensions: (2, 4)
    state: victory
    visible:
        [False, True, True, True]
        [False, False, True, True]

    >>> game = {'dimensions': [2, 4],
    ...         'board': [['.', 3, 1, 0],
    ...                   ['.', '.', 1, 0]],
    ...         'visible': [[False, True, False, False],
    ...                  [False, False, False, False]],
    ...         'state': 'ongoing'}
    >>> dig_2d(game, 0, 0)
    1
    >>> dump(game)
    board:
        ['.', 3, 1, 0]
        ['.', '.', 1, 0]
    dimensions: [2, 4]
    state: defeat
    visible:
        [True, True, False, False]
        [False, False, False, False]
    """
    
    # # if bomb
    # if get_coord_nd(game['board'], (row,col)) == '.':
    #     set_coord_nd(game['visible'], (row,col), True)
    #     game['state'] = 'defeat'
    #     return 1

    # if get_coord_nd(game['visible'], (row,col)) != True:
    #     set_coord_nd(game['visible'], (row, col), True)
    #     revealed = 1
    # else:
    #     return 0

    # if game['board'][row][col] == 0:
    #     for neighbor in get_neighbors(game['dimensions'], (row,col)):
    #         r,c = neighbor
    #         if game['board'][r][c] != '.' and not game['visible'][r][c]:
    #             revealed += dig_2d(game, r,c)

    # covered_squares = 0
    # for r in range(game['dimensions'][0]):
    #     # for each r,
    #     for c in range(game['dimensions'][1]):
    #         # for each c,

    #         # if not visible and not a bomb
    #         if not game['visible'][r][c] and game['board'][r][c] != '.':
    #             covered_squares +=1

    # if covered_squares > 0:
    #     game['state'] = 'ongoing'
    #     return revealed
    # else:
    #     game['state'] = 'victory'
    #     return revealed
    return dig_nd(game, (row, col))


def render_2d_locations(game, xray=False):
    """
    Prepare a game for display.

    Returns a two-dimensional array (list of lists) of '_' (hidden squares),
    '.' (bombs), ' ' (empty squares), or '1', '2', etc. (squares neighboring
    bombs).  game['visible'] indicates which squares should be visible.  If
    xray is True (the default is False), game['visible'] is ignored and all
    cells are shown.

    Parameters:
       game (dict): Game state
       xray (bool): Whether to reveal all tiles or just the ones allowed by
                    game['visible']

    Returns:
       A 2D array (list of lists)

    >>> render_2d_locations({'dimensions': (2, 4),
    ...         'state': 'ongoing',
    ...         'board': [['.', 3, 1, 0],
    ...                   ['.', '.', 1, 0]],
    ...         'visible':  [[False, True, True, False],
    ...                   [False, False, True, False]]}, False)
    [['_', '3', '1', '_'], ['_', '_', '1', '_']]

    >>> render_2d_locations({'dimensions': (2, 4),
    ...         'state': 'ongoing',
    ...         'board': [['.', 3, 1, 0],
    ...                   ['.', '.', 1, 0]],
    ...         'visible':  [[False, True, False, True],
    ...                   [False, False, False, True]]}, True)
    [['.', '3', '1', ' '], ['.', '.', '1', ' ']]
    """

    return render_nd(game, xray)


def render_2d_board(game, xray=False):
    """
    Render a game as ASCII art.

    Returns a string-based representation of argument 'game'.  Each tile of the
    game board should be rendered as in the function
        render_2d_locations(game)

    Parameters:
       game (dict): Game state
       xray (bool): Whether to reveal all tiles or just the ones allowed by
                    game['visible']

    Returns:
       A string-based representation of game

    >>> render_2d_board({'dimensions': (2, 4),
    ...                  'state': 'ongoing',
    ...                  'board': [['.', 3, 1, 0],
    ...                            ['.', '.', 1, 0]],
    ...                  'visible':  [[True, True, True, False],
    ...                            [False, False, True, False]]})
    '.31_\\n__1_'
    """
    s = ''

    game_ = render_2d_locations(game, xray)

    for i in range(len(game_)):
        for j in range(len(game_[i])):
            s += game_[i][j]

        if i != len(game_)-1:
            s+='\n'
    
    return s

# N-D IMPLEMENTATION

# helper

def get_coord_nd(nd_array, tup):
    '''
    A function that, given an N-d array and a tuple/list of coordinates, 
    returns the value at those coordinates in the array.

    >>> get_coord_nd([[[1,8],[2,7]], [[3,4],[5,6]]], (1,1,0))
    5

    '''
    d = tup[:]
    first,rest = d[0], d[1:]
    curr = nd_array

    while rest:
        curr = curr[first]
        first, rest = rest[0], rest[1:]

    return curr[first]

def set_coord_nd(nd_array, tup, val, add=False):
    '''
    A function that, given an N-d array, a tuple/list of coordinates, 
    and a value, replaces the value at those coordinates in 
    the array with the given value.

    >>> A = [[[1,8],[2,7]], [[3,4],[5,6]]]
    >>> set_coord_nd(A, (1,1,0), 7)
    >>> A
    [[[1, 8], [2, 7]], [[3, 4], [7, 6]]]

    '''
    first,rest = tup[0], tup[1:]
    curr = nd_array

    while rest:
        curr = curr[first]
        first, rest = rest[0], rest[1:]

    if curr[first] != '.':
        if add:
            curr[first] += val
        else:
            curr[first] = val
    

def create_uniform_val(dimensions, val):
    '''
    A function that, given a list of dimensions and a value, 
    creates a new N-d array with those dimensions, 
    where each value in the array is the given value.

    >>> create_uniform_val([2,3,2], 0)
    [[[0, 0], [0, 0], [0, 0]], [[0, 0], [0, 0], [0, 0]]]

    >>> create_uniform_val([2,3], 4)
    [[4, 4, 4], [4, 4, 4]]
    '''
    #base case
    if len(dimensions) == 0:
        return val

    first = dimensions[0]

    return [create_uniform_val(dimensions[1:], val) for _ in range(first)]

def get_coords(dimensions):
    '''
    A function that returns all possible coordinates in a given board.

    >>> get_coords((2,2,2))
    [(0, 0, 0), (0, 0, 1), (0, 1, 0), (0, 1, 1), (1, 0, 0), (1, 0, 1), (1, 1, 0), (1, 1, 1)]
    '''

    # base case
    if len(dimensions) == 1:
        return [(i,) for i in range(dimensions[0])]

    tmp = []
    returned_tuples = get_coords(dimensions[1:])

    for i in range(dimensions[0]):
        for tup in returned_tuples:
            tmp.append((i,) + tup)

    return tmp


def get_neighbors(dimensions, coord, is_original=True):
    '''
    Returns the neighbors for a coord

    >>> get_neighbors((10,20,3), (5,13,0))
    [(4, 12, 0), (5, 12, 0), (6, 12, 0), (4, 13, 0), (6, 13, 0), (4, 14, 0), (5, 14, 0), (6, 14, 0), (4, 12, 1), (5, 12, 1), (6, 12, 1), (4, 13, 1), (5, 13, 1), (6, 13, 1), (4, 14, 1), (5, 14, 1), (6, 14, 1)]

    >>> get_neighbors((10, 20), (5,13))
    [(4, 12), (5, 12), (6, 12), (4, 13), (6, 13), (4, 14), (5, 14), (6, 14)]

    >>> get_neighbors((2,4,2), (1,1,1))
    [(0, 0, 0), (1, 0, 0), (0, 1, 0), (1, 1, 0), (0, 2, 0), (1, 2, 0), (0, 0, 1), (1, 0, 1), (0, 1, 1), (0, 2, 1), (1, 2, 1)]
    '''
    # base case
    if len(coord) == 1:
        t = []
        if coord[0]-1>=0:
            t.append((coord[0]-1,))

        t.append((coord[0],))

        if coord[0]+1 < dimensions[0]:
            t.append((coord[0]+1,))
        return t

    f_dim = dimensions[0]
    first = coord[0]

    neighbors = []
    returned_neighbors = get_neighbors(dimensions[1:], coord[1:], is_original=False)

    for neighbor in returned_neighbors:
        for i in range(first-1, first+2):
            if 0 <= i < f_dim:
                neighbors.append((i,) + neighbor)

    if is_original:
        neighbors.remove(coord)

    return neighbors



def new_game_nd(dimensions, bombs):
    """
    Start a new game.

    Return a game state dictionary, with the 'dimensions', 'state', 'board' and
    'visible' fields adequately initialized.


    Args:
       dimensions (tuple): Dimensions of the board
       bombs (list): Bomb locations as a list of lists, each an
                     N-dimensional coordinate

    Returns:
       A game state dictionary

    >>> g = new_game_nd((2, 4, 2), [(0, 0, 1), (1, 0, 0), (1, 1, 1)])
    >>> dump(g)
    board:
        [[3, '.'], [3, 3], [1, 1], [0, 0]]
        [['.', 3], [3, '.'], [1, 1], [0, 0]]
    dimensions: (2, 4, 2)
    state: ongoing
    visible:
        [[False, False], [False, False], [False, False], [False, False]]
        [[False, False], [False, False], [False, False], [False, False]]
    """
    board = create_uniform_val(dimensions, 0)
    visible = create_uniform_val(dimensions, False)
    state = 'ongoing'
    dim = dimensions[:]

    for bomb in bombs:
        set_coord_nd(board, bomb, '.')
        for neighbor in get_neighbors(dimensions, bomb):
                set_coord_nd(board, neighbor, 1, add=True)


    return {
        'board':board,
        'visible':visible,
        'state' :state,
        'dimensions':dim
    }



def dig_nd(game, coordinates, is_original=True):
    """
    Recursively dig up square at coords and neighboring squares.

    Update the visible to reveal square at coords; then recursively reveal its
    neighbors, as long as coords does not contain and is not adjacent to a
    bomb.  Return a number indicating how many squares were revealed.  No
    action should be taken and 0 returned if the incoming state of the game
    is not 'ongoing'.

    The updated state is 'defeat' when at least one bomb is visible on the
    board after digging, 'victory' when all safe squares (squares that do
    not contain a bomb) and no bombs are visible, and 'ongoing' otherwise.

    Args:
       coordinates (tuple): Where to start digging

    Returns:
       int: number of squares revealed

    >>> g = {'dimensions': (2, 4, 2),
    ...      'board': [[[3, '.'], [3, 3], [1, 1], [0, 0]],
    ...                [['.', 3], [3, '.'], [1, 1], [0, 0]]],
    ...      'visible': [[[False, False], [False, True], [False, False],
    ...                [False, False]],
    ...               [[False, False], [False, False], [False, False],
    ...                [False, False]]],
    ...      'state': 'ongoing'}
    >>> dig_nd(g, (0, 3, 0))
    8
    >>> dump(g)
    board:
        [[3, '.'], [3, 3], [1, 1], [0, 0]]
        [['.', 3], [3, '.'], [1, 1], [0, 0]]
    dimensions: (2, 4, 2)
    state: ongoing
    visible:
        [[False, False], [False, True], [True, True], [True, True]]
        [[False, False], [False, False], [True, True], [True, True]]
    >>> g = {'dimensions': (2, 4, 2),
    ...      'board': [[[3, '.'], [3, 3], [1, 1], [0, 0]],
    ...                [['.', 3], [3, '.'], [1, 1], [0, 0]]],
    ...      'visible': [[[False, False], [False, True], [False, False],
    ...                [False, False]],
    ...               [[False, False], [False, False], [False, False],
    ...                [False, False]]],
    ...      'state': 'ongoing'}
    >>> dig_nd(g, (0, 0, 1))
    1
    >>> dump(g)
    board:
        [[3, '.'], [3, 3], [1, 1], [0, 0]]
        [['.', 3], [3, '.'], [1, 1], [0, 0]]
    dimensions: (2, 4, 2)
    state: defeat
    visible:
        [[False, True], [False, True], [False, False], [False, False]]
        [[False, False], [False, False], [False, False], [False, False]]
    """
    # base case
    if game['state'] == 'defeat' or game['state'] == 'victory' or get_coord_nd(game['visible'], coordinates):
        game['state'] = game['state']
        return 0


    pos = get_coord_nd(game['board'], coordinates)
    set_coord_nd(game['visible'], coordinates, True)
    revealed = 1

    if pos == '.':
        game['state'] = 'defeat'
        return revealed

    elif pos != 0:
        pass

    elif pos == 0:
        dum_var = get_neighbors(game['dimensions'], coordinates)
        for neighbor in dum_var:
            if not get_coord_nd(game['visible'], neighbor):
                revealed += dig_nd(game, neighbor, is_original=False)

    if is_original:
        covered_squares = 0
        for coord in get_coords(game['dimensions']):
            if get_coord_nd(game['board'], coord) != '.' and not get_coord_nd(game['visible'], coord):
                covered_squares +=1

        if covered_squares > 0:
            game['state'] = 'ongoing'
            return revealed
        else:
            game['state'] = 'victory'
            return revealed
    
    return revealed



def render_nd(game, xray=False):
    """
    Prepare the game for display.

    Returns an N-dimensional array (nested lists) of '_' (hidden squares), '.'
    (bombs), ' ' (empty squares), or '1', '2', etc. (squares neighboring
    bombs).  The game['visible'] array indicates which squares should be
    visible.  If xray is True (the default is False), the game['visible'] array
    is ignored and all cells are shown.

    Args:
       xray (bool): Whether to reveal all tiles or just the ones allowed by
                    game['visible']

    Returns:
       An n-dimensional array of strings (nested lists)

    >>> g = {'dimensions': (2, 4, 2),
    ...      'board': [[[3, '.'], [3, 3], [1, 1], [0, 0]],
    ...                [['.', 3], [3, '.'], [1, 1], [0, 0]]],
    ...      'visible': [[[False, False], [False, True], [True, True],
    ...                [True, True]],
    ...               [[False, False], [False, False], [True, True],
    ...                [True, True]]],
    ...      'state': 'ongoing'}
    >>> render_nd(g, False)
    [[['_', '_'], ['_', '3'], ['1', '1'], [' ', ' ']],
     [['_', '_'], ['_', '_'], ['1', '1'], [' ', ' ']]]

    >>> render_nd(g, True)
    [[['3', '.'], ['3', '3'], ['1', '1'], [' ', ' ']],
     [['.', '3'], ['3', '.'], ['1', '1'], [' ', ' ']]]
    """
    nd_array = create_uniform_val(game['dimensions'], None)

    for coord in get_coords(game['dimensions']):
        if get_coord_nd(game['visible'], coord) or xray:
            w = get_coord_nd(game['board'], coord)
            if w == 0:
                set_coord_nd(nd_array, coord, ' ')
            else:
                set_coord_nd(nd_array, coord, str(w))
        else:
            set_coord_nd(nd_array, coord, '_')

    return nd_array


if __name__ == "__main__":
    # Test with doctests. Helpful to debug individual lab.py functions.
    _doctest_flags = doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS
    doctest.testmod(optionflags=_doctest_flags)  # runs ALL doctests

    # Alternatively, can run the doctests JUST for specified function/methods,
    # e.g., for render_2d_locations or any other function you might want.  To
    # do so, comment out the above line, and uncomment the below line of code.
    # This may be useful as you write/debug individual doctests or functions.
    # Also, the verbose flag can be set to True to see all test results,
    # including those that pass.
    #
    # doctest.run_docstring_examples(
    #    dig_nd,
    #    globals(),
    #    optionflags=_doctest_flags,
    #    verbose=True
    # )
