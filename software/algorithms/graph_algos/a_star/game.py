import pygame
import random
import sys
from copy import deepcopy


def select_random_bias(bias):
    '''
    Return a bit given a bias. If random number
    is smaller than bias, returns 1. Otherwise, returns 0.
    '''
    
    r = random.random()
    
    if r >= bias:
        return 0
    
    else:
        return 1
    
            
def h(tup):
    x,y = tup
    return ((goal_x-x)**2 + (goal_y-y)**2)**0.5


# setting colors
BLACK = (0,0,0) # blocked cell
WHITE = (255,255,255) # free cell
GREEN = (0, 255, 0)
BLUE = (0,0,255)
RED = (255, 0, 0)

# setting screen
WIDTH = 1200
HEIGHT = 800
RESOLUTION = 20

# other variables
SEEN = set()
max_y = HEIGHT//RESOLUTION - 1
max_x = WIDTH//RESOLUTION - 1
goal_x = random.randint(0,max_x)
goal_y = random.randint(0, max_y)

openSet = set([(0,0)])
closedSet = set()

cameFrom = {}

trueScore = {}
trueScore[(0,0)] = 0

guessScore = {}
guessScore[(0,0)] = h((0,0))

def return_guess_score(tup):
    return guessScore.get(tup, float('inf'))

def return_true_score(tup):
    return trueScore.get(tup, float('inf'))

grid = [[select_random_bias(0.70) for _ in range(max_y+1)] for _ in range(max_x+1)]

next_grid = deepcopy(grid)

grid[goal_x][goal_y] = 3
grid[0][0] = 2

pygame.init()
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
CLOCK = pygame.time.Clock()
    
def drawGrid(path):
    global WIDTH, HEIGHT, BLACK, \
    WHITE, RESOLUTION, grid, \
    RED, GREEN
    
    next_grid = deepcopy(grid)
    
    for x,y in closedSet:
        next_grid[x][y] = 4
        
    for x,y in openSet:
        next_grid[x][y] = 5
    
    # compute new grid
    for x,y in path:
        next_grid[x][y] = 2
    
    
    for x in range(max_x+1):
        for y in range(max_y+1):

            if next_grid[x][y] == 0:
                color = BLACK
                
            elif next_grid[x][y] == 3:
                color = GREEN
                
            elif next_grid[x][y] == 2:
                color = RED
                
            elif next_grid[x][y] == 4:
                color = BLUE
                
            elif next_grid[x][y] == 5:
                color = (127, 255, 255)
                
            else:
                color = WHITE
                
            rect = pygame.Rect(x*RESOLUTION,
                               y*RESOLUTION,
                               RESOLUTION-1,
                               RESOLUTION-1)
            
            pygame.draw.rect(SCREEN, color, rect)

def get_neighbors(tup, nondiag=False):
    '''
    Return neighbors of a given position
    '''
    x,y = tup
    neighbors = []
    
    if nondiag:
        
        if x+1 <= max_x and next_grid[x+1][y] != 0: neighbors.append((x+1, y))
        if x-1 >= 0 and next_grid[x-1][y] !=0 : neighbors.append((x-1,y))
        if y+1 <= max_y and next_grid[x][y+1] !=0 : neighbors.append((x, y+1))
        if y-1 >= 0 and next_grid[x][y-1] != 0: neighbors.append((x, y-1))
        
    else:
        
        for i in range(-1,2):
            for j in range(-1,2):
                
                # out of border
                if x+i<0 or x+i>max_x: continue
                if y+j<0 or y+j>max_y: continue
                
                
                if next_grid[x+i][y+j] != 0: neighbors.append((x+i, y+j))
        try:
            neighbors.remove((x,y))
        except:
            pass
    
    
    return neighbors

def get_path(cameFrom, current_cell):
    total_path = [current_cell]
    
    while current_cell in cameFrom.keys():
        current_cell = cameFrom[current_cell]
        total_path.append(current_cell)
        
    return total_path

def get_dist(c1, c2):
    '''
    '''
    
    x1,y1 = c1
    x2,y2 = c2
    
    # if not diag
    if (x1 == x2) or (y1 == y2): return 1
    
    # if diag
    return ((x1-x2)**2 + (y1-y2)**2)**0.5
     

while True:
       
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
    
    while openSet:  
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()   
        
        current = min(openSet, key=return_guess_score)
        
        if current[0] == goal_x and current[1] == goal_y:
            path = get_path(cameFrom, current)
            break
        
        openSet.remove(current)
        closedSet.add(current)
        
        for neighbor in get_neighbors(current):
            
            if neighbor in closedSet:
                continue
            
            tent_score = get_dist(current, neighbor) + return_true_score(current)
            
            if neighbor not in openSet:
                openSet.add(neighbor)
            
            elif tent_score >= return_true_score(neighbor): 
                continue

            trueScore[neighbor] = tent_score
            guessScore[neighbor] = tent_score + h(neighbor)
            cameFrom[neighbor] = current
                
        path = get_path(cameFrom,current)
        
        drawGrid(path)
        pygame.display.update()
        CLOCK.tick(15)
        

    drawGrid(path)
    pygame.display.update()
    CLOCK.tick(15)


    
    