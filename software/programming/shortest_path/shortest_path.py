#!/usr/bin/env python3

from util import read_osm_data, great_circle_distance, to_local_kml_url

# NO ADDITIONAL IMPORTS!


ALLOWED_HIGHWAY_TYPES = {
    'motorway', 'trunk', 'primary', 'secondary', 'tertiary', 'unclassified',
    'residential', 'living_street', 'motorway_link', 'trunk_link',
    'primary_link', 'secondary_link', 'tertiary_link',
}


DEFAULT_SPEED_LIMIT_MPH = {
    'motorway': 60,
    'trunk': 45,
    'primary': 35,
    'secondary': 30,
    'residential': 25,
    'tertiary': 25,
    'unclassified': 25,
    'living_street': 10,
    'motorway_link': 30,
    'trunk_link': 30,
    'primary_link': 30,
    'secondary_link': 30,
    'tertiary_link': 25,
}


def build_internal_representation(nodes_filename, ways_filename):
    """
    Create any internal representation you want for the specified map, by
    reading the data from the given filenames (using read_osm_data)

    Returns
    -------
        map : dict

            map in the form
            {
                node_id : {'loc' : (lat, lon), 'nodes':{reachable_nodes}}
            }
    """

    # get edges
    seen = set()
    edges = {}
    for data in read_osm_data(ways_filename):
        # check if its in valid highways
        try:
            if data['tags']['highway'] in ALLOWED_HIGHWAY_TYPES:
                #check if its oneway
                try:
                    if data['tags']['oneway'] == 'yes':
                        edges[data['id']] = {'oneway':True, 'nodes':data['nodes']}
                    else:
                        edges[data['id']] = {'nodes': data['nodes'], 'oneway' : False}

                except:
                    edges[data['id']] = {'nodes': data['nodes'], 'oneway' : False}

                # check if there is a maxspeed_mph assigned 
                try:
                    edges[data['id']]['maxspeed_mph'] = data['tags']['maxspeed_mph']
                except:
                    edges[data['id']]['maxspeed_mph'] = DEFAULT_SPEED_LIMIT_MPH[data['tags']['highway']]

                for node in data['nodes']:
                    seen.add(node)

        except:
            continue

     # get nodes
    nodes = {}
    for data in read_osm_data(nodes_filename):
        if data['id'] in seen:
            nodes[data['id']] = (data['lat'], data['lon'])

    del seen

    map = {}

    for edge in edges.keys():

        # iterate over nodes in way
        for i in range(1,len(edges[edge]['nodes'])):

            # get subsequent nodes
            node_1 = edges[edge]['nodes'][i-1]
            node_2 = edges[edge]['nodes'][i]

            # nodes that were mentioned -> important
            if map.get(node_1) is None:
                map[node_1] = {'loc' : nodes[node_1], 'nodes': {}}

            if map.get(node_2) is None:
                map[node_2] = {'loc': nodes[node_2], 'nodes': {}}

            # if it is oneway
            if edges[edge]['oneway']:
                
                # if there is something already assigned, check if its greater, else create 
                if map[node_1]['nodes'].get(node_2, 0) < edges[edge]['maxspeed_mph']:
                    map[node_1]['nodes'][node_2] = edges[edge]['maxspeed_mph']

            else:

                if map[node_1]['nodes'].get(node_2, 0) < edges[edge]['maxspeed_mph']:
                    map[node_1]['nodes'][node_2] = edges[edge]['maxspeed_mph']
                
                if map[node_2]['nodes'].get(node_1, 0) < edges[edge]['maxspeed_mph']:
                    map[node_2]['nodes'][node_1] = edges[edge]['maxspeed_mph']
        


                
    # delete variables
    # question: redundant?

    return map

def find_short_path_nodes(map_rep, node1, node2, check_number=False):
    """
    Return the shortest path between the two nodes

    Parameters:
        map_rep: the result of calling build_internal_representation
        node1: node representing the start location
        node2: node representing the end location

    Returns:
        a list of node IDs representing the shortest path (in terms of
        distance) from node1 to node2
    """

    # init variables
    number_paths = 0
    agenda = [(0, [node1])] # each path is a tuple (cost, [list_of_nodes])
    expanded = set()

    # while agenda is not empty
    while agenda:

        # get lowest path by cost (first index)
        lowest_path = min(agenda, key=lambda path: path[0])
        number_paths+=1
        
        # remove path from agenda
        agenda.remove(lowest_path)

        # get terminal vertex and cost
        terminal_vertex = lowest_path[1][-1]
        cost = lowest_path[0]

        # if already checked
        if terminal_vertex in expanded:
            continue
        
        # terminal condition
        if terminal_vertex == node2:

            # if checking number
            if check_number:
                print('Number of paths for UC Search: ', number_paths)
            
            # return that path
            return lowest_path[1]

        else:

            # added to checked nodes
            expanded.add(terminal_vertex)
            
            # get info about node
            # if node is not in map_rep, ['nodes'] = empty list
            info = map_rep.get(terminal_vertex, {'nodes':[]})

            for child in info['nodes']:
                
                # if child already checked
                if child in expanded:
                    continue

                else:

                    # get new path and new cost
                    new_path = lowest_path[1] + [child]
                    new_cost = great_circle_distance(map_rep[terminal_vertex]['loc'], map_rep[child]['loc']) + cost

                    # append new path to agenda
                    agenda.append((new_cost, new_path))
    
    if check_number:
        print('Number of paths for UC Search: ', number_paths)

    # if all agenda checked
    # and not assigned
    # return None
    return None

def find_short_path(map_rep, loc1, loc2, a_star=False, check=False):
    """
    Return the shortest path between the two locations

    Parameters:
        map_rep: the result of calling build_internal_representation
        loc1: tuple of 2 floats: (latitude, longitude), representing the start
              location
        loc2: tuple of 2 floats: (latitude, longitude), representing the end
              location

    Returns:
        a list of (latitude, longitude) tuples representing the shortest path
        (in terms of distance) from loc1 to loc2.
    """

    # get best node for loc1, loc2
    best_dist_1 = float('inf')
    best_dist_2 = float('inf')
    
    for node, prop in map_rep.items():
        
        if great_circle_distance(loc1, prop['loc']) < best_dist_1:
            best_dist_1 = great_circle_distance(loc1, prop['loc'])
            n1 = node

        if great_circle_distance(loc2, prop['loc']) < best_dist_2:
            best_dist_2 = great_circle_distance(loc2, prop['loc'])
            n2 = node

    del best_dist_1
    del best_dist_2
    
    if a_star:
        shortest_path = A_star(map_rep, n1, n2, check)
    else:
        shortest_path = find_short_path_nodes(map_rep, n1, n2,check)


    # check if there exists path
    try:

        for i in range(len(shortest_path)):

            # convert path to ('lat', 'lon')
            shortest_path[i] = map_rep[shortest_path[i]]['loc']

        return shortest_path
    except:
        return None

def A_star(map_rep, node1, node2, check_number=False):
    number_paths = 0

    def f(curr_dist, node, goal):
        '''
        Return heuristic for a node

        Parameters
        ----------
            curr_dist : float
                Current distance of the path

            node : int
                Current node

            goal : int
                Goal node

        Returns
        -------
            Heuristic associated to given node
        '''
        loc1 = map_rep[node]['loc']
        loc2 = map_rep[goal]['loc']

        return curr_dist+ great_circle_distance(loc1, loc2)

    # init variables
    agenda = [(0, f(0, node1, node2), [node1])] # each path is a tuple (cost, heuristic, [list_of_nodes])
    expanded = set()

    while agenda:
        
        # get min arg by heuristic
        lowest_path = min(agenda, key=lambda path: path[1])
        number_paths +=1
        agenda.remove(lowest_path)

        terminal_vertex = lowest_path[2][-1]
        cost = lowest_path[0]

        if terminal_vertex in expanded:
            continue

        if terminal_vertex == node2:
            if check_number:
                print('Number of paths for A* Search: ', number_paths)
            return lowest_path

        else:
            expanded.add(terminal_vertex)

            info = map_rep.get(terminal_vertex, {'nodes':[]})

            for child in info['nodes']:

                if child in expanded:
                    continue

                else:
                    new_path = lowest_path[2] + [child]
                    new_cost = great_circle_distance(map_rep[terminal_vertex]['loc'], map_rep[child]['loc']) + cost
                    new_heuristic = f(new_cost, child, node2)
                    agenda.append((new_cost, new_heuristic, new_path))

                    del new_path, new_cost, new_heuristic

            del lowest_path

    if check_number:
                print('Number of paths for A* Search: ', number_paths)
    return None

def find_fast_path(map_rep, loc1, loc2, check_number=False):
    """
    Return the shortest path between the two locations, in terms of expected
    time (taking into account speed limits).

    Parameters:
        map_rep: the result of calling build_internal_representation
        loc1: tuple of 2 floats: (latitude, longitude), representing the start
              location
        loc2: tuple of 2 floats: (latitude, longitude), representing the end
              location

    Returns:
        a list of (latitude, longitude) tuples representing the shortest path
        (in terms of time) from loc1 to loc2.
    """
    def helper():
        best_dist_1 = float('inf')
        best_dist_2 = float('inf')
        
        for node, prop in map_rep.items():
            
            if great_circle_distance(loc1, prop['loc']) < best_dist_1:
                best_dist_1 = great_circle_distance(loc1, prop['loc'])
                node1 = node

            if great_circle_distance(loc2, prop['loc']) < best_dist_2:
                best_dist_2 = great_circle_distance(loc2, prop['loc'])
                node2 = node

        number_paths = 0
        agenda = [(0, [node1])]
        expanded = set()

        while agenda:

            lowest_path = min(agenda, key=lambda path: path[0])
            number_paths+=1
            agenda.remove(lowest_path)

            terminal_vertex = lowest_path[1][-1]
            time = lowest_path[0]

            if terminal_vertex in expanded:
                continue

            if terminal_vertex == node2:
                if check_number:
                    print('Number of paths for UC Time Search: ', number_paths)
                return lowest_path[1]

            else:
                expanded.add(terminal_vertex)
                
                info = map_rep.get(terminal_vertex, {'nodes':[]})

                for child in info['nodes']:

                    if child in expanded:
                        continue

                    else:
                        new_path = lowest_path[1] + [child]

                        # time is distance / max_speed
                        time_ = great_circle_distance(map_rep[terminal_vertex]['loc'], map_rep[child]['loc'])/map_rep[terminal_vertex]['nodes'][child]

                        new_time = time_ + time
                        agenda.append((new_time, new_path))
        
        if check_number:
            print('Number of paths for UC Search: ', number_paths)
        return None

    shortest_path = helper()

    try:
        for i in range(len(shortest_path)):
            shortest_path[i] = map_rep[shortest_path[i]]['loc']

        return shortest_path
        
    except:
        return None

if __name__ == '__main__':
    # additional code here will be run only when lab.py is invoked directly
    # (not when imported from test.py), so this is a good place to put code
    # used, for example, to generate the results for the online questions.
    # midwest_nodes = '6009/lab03/resources/midwest.nodes'
    # midwest_ways = '6009/lab03/resources/midwest.ways'
    # map = build_internal_representation(midwest_nodes, midwest_ways)

    # loc = (41.4452463, -89.3161394)
    # best_dist = float('inf')
    
    # for node, prop in map.items():
        
    #     if great_circle_distance(loc, prop['loc']) < best_dist:
    #         best_dist = great_circle_distance(loc, prop['loc'])
    #         n = node

    # print(n)

    # cambridge_nodes = '6009/lab03/resources/cambridge.nodes'
    # cambridge_ways = '6009/lab03/resources/cambridge.ways'

    # map_rep = build_internal_representation(cambridge_nodes, cambridge_ways)    

    # loc1 = (42.3858, -71.0783)
    # loc2 = (42.5465, -71.1787)

    # find_short_path(map_rep, loc1, loc2, a_star=True, check=True) # print 50704
    # find_short_path(map_rep, loc1, loc2, check=True)              # print 420555
    pass




    