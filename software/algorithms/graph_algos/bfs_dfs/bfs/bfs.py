def bfs(Adj, s):
    """

    Breadth-first search algorithm

    input:
        
        Adj   -> list of adjacent vertices to s

        s     -> source vertex

    output:

        parent -> list of shortest path from s to any other vertex
    """

    parent = [None for v in Adj]                # O(V)
    parent[s]= s                                # O(1) root
    level = [[s]]                               # O(1) initiliaze levels 
    while 0 < len(level[-1]):                   # O(?) last level contains vertices 
        level.append([])                        # O(1) amortized, make new level
        for u in level[-2]:                     # O(?) loop over last full level
            for v in Adj[u]:                    # O(Adj[u]) loop over neighbors
                if parent[v] is None:           # O(1) parent not yet assigned
                    parent[v] = u               # O(1) assign parent from level[-2]
                    level[-1].append(v)         # O(1) amortized, add to border

    return parent

def unweighted_shortest_path(Adj, s, t):
    """
    input:

        Adj        -> list of adjacent vertices to s

        s          -> source vertex

        t          -> final vertex

    output:

        path[::-1] -> shortest path from s to t

    """
    parent = bfs(Adj, s)                        # O(V+E) BFS tree from s
    if parent[t] is None:                       # O(1) t reachable from s?
        return None                             # O(1) no path
    i = t                                       # O(1) label of current vertex
    path = [t]                                  # O(1) initiliaze path
    while i != s:                               # O(V) walk back to s
        i = parent[i]                           # O(1) move parent
        path.append(i)                          # O(1) amortized add to path
    return path[::-1]                           # O(V) return reversed path