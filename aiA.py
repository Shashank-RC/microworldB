# NAME(S): [PLACE YOUR NAME(S) HERE]
#
# APPROACH: [WRITE AN OVERVIEW OF YOUR APPROACH HERE.]
#     Please use multiple lines (< ~80-100 char) for you approach write-up.
#     Keep it readable. In other words, don't write
#     the whole damned thing on one super long line.
#
#     In-code comments DO NOT count as a description of
#     of your approach.

import random
import heapq

class AI:
    def __init__(self, max_turns):
        # Set a default number of turns if max_turns is None
        self.numOfTurns = max_turns if max_turns is not None else 1000  # Default to 1000 if None

        # Initialize agent position, map, path, and tracking variables
        self.xCoord = 0
        self.yCoord = 0
        self.currentNode = Node(0, 0, 'main')
        self.map = [self.currentNode]  # Track explored nodes in the map
        self.path_stack = []           # Stack for DFS and backtracking
        self.turn = -1
        self.goalCoords = None
        self.goalMap = None
        self.distanceFromGoal = 0
        self.hasAFoundGoal = False
        self.currentMap = 'main'       # Initialize current map layer

    def update(self, percepts, msg):
        """
        Updates each turn to manage DFS and A* pathfinding.
        """
        # Check if msg is None and set default values if needed
        if msg is None:
            msg = [self.map, self.goalCoords]  # Provide fallback values if no message is received

        # Process message contents
        self.goalCoords = msg[1]
        self.map = msg[0]
        self.turn += 1
        self.update_graph(percepts)

        # Requirement: Check if current cell is an exit (goal) and store if unknown
        if percepts['X'][0] == 'r' and self.goalCoords is None:
            self.goalCoords = (self.xCoord, self.yCoord)
            self.goalMap = self.currentNode.whatMap
            self.hasAFoundGoal = True

        # Exit strategy: if approaching turn limit, go to exit if possible
        if self.goalCoords is not None and self.hasAFoundGoal:
            self.distanceFromGoal += 1
        if (self.turn + self.distanceFromGoal - 1) >= self.numOfTurns:
            msg = [self.map, self.goalCoords]
            if percepts['X'][0] == 'r':  # Use 'U' if on exit cell
                return 'U', msg
            # Backtrack towards exit if near turn limit
            backtrack_node = self.path_stack.pop() if self.path_stack else None
            return self.backtrack_to_node(backtrack_node), msg

        # Requirement: Goal detection and activation
        if percepts['X'][0].isdigit():
            msg = [self.map, self.goalCoords]
            return 'U', msg

        # Requirement: Handle teleports with 'U' command and update map if teleported
        if percepts['X'][0] in 'obyp':
            msg = [self.map, self.goalCoords]
            if self.currentMap == 'main':
                # Reset coordinates for teleport
                self.xCoord, self.yCoord, self.currentMap = 0, 0, percepts['X'][0]
            else:
                self.currentMap = 'main'  # Return to main map if back from teleport
            return 'U', msg 

        # Goal-directed A* pathfinding when goal is known
        if self.goalCoords is not None:
            return self.AStar_search(self.currentNode), msg

        # DFS Exploration: prioritize unvisited neighbors
        possibleDirections = []
        for direction in ['N', 'S', 'E', 'W']:
            next_node = self.get_neighbor_node(direction)
            if next_node and not next_node.visited:
                possibleDirections.append(direction)

        # If unvisited directions are available, push current node to stack for DFS
        if possibleDirections:
            direction = random.choice(possibleDirections)
            self.path_stack.append(self.currentNode)
            return self.move_in_direction(direction), msg

        # Backtrack if DFS exploration has exhausted all paths
        if self.path_stack:
            backtrack_node = self.path_stack.pop()
            return self.backtrack_to_node(backtrack_node), msg

        # Fallback movement if no other options (for redundancy)
        return random.choice(['N', 'S', 'E', 'W']), "A moving randomly"

    # Handles DFS movement by updating coordinates and direction
    def move_in_direction(self, direction):
        target_node = self.get_neighbor_node(direction)
        if target_node is None:
            self.create_neighbor_node(direction, self.currentMap)
        move_dict = {'N': (1, 0), 'S': (-1, 0), 'E': (0, 1), 'W': (0, -1)}
        dx, dy = move_dict[direction]
        self.xCoord += dx
        self.yCoord += dy
        self.currentNode = self.get_neighbor_node(direction)
        self.currentNode.setVisitedToYes()
        return direction

    # This function retrieves the neighboring node in the specified direction, if it exists
    def get_neighbor_node(self, direction):
        if direction == 'N':
            return self.currentNode.northNode
        elif direction == 'S':
            return self.currentNode.southNode
        elif direction == 'E':
            return self.currentNode.eastNode
        elif direction == 'W':
            return self.currentNode.westNode
        return None

    # Backtracking to revisit previous nodes when DFS runs out of paths
    def backtrack_to_node(self, backtrack_node):
        return next((self.move_in_direction(d) for d in ['N', 'S', 'E', 'W'] if self.get_neighbor_node(d) == backtrack_node), None)

    # Update the graph with perceived environment, linking nodes
    def update_graph(self, percepts):
        for direction in ['N', 'S', 'E', 'W']:
            if percepts[direction][0] != 'w':
                neighbor_node = self.find_or_create_node(self.xCoord + (1 if direction == 'N' else -1 if direction == 'S' else 0),
                                                         self.yCoord + (1 if direction == 'E' else -1 if direction == 'W' else 0),
                                                         self.currentMap)
                self.link_nodes(direction, neighbor_node)

    # Find or create a new node at specified coordinates within the map
    def find_or_create_node(self, x, y, map=None):
        # Search for an existing node with the specified coordinates and map
        for node in self.map:
            if node.xCoord == x and node.yCoord == y and node.whatMap == (map or self.currentMap):
                return node
        # If not found, create a new node
        new_node = Node(x, y, map or self.currentMap)
        self.map.append(new_node)
        print(f"Created new node at x={x}, y={y} on map={map or self.currentMap}")
        return new_node

    # Link nodes in the specified direction to maintain graph structure
    def link_nodes(self, direction, neighbor_node):
        if direction == 'N':
            self.currentNode.setNorthNode(neighbor_node)
            neighbor_node.setSouthNode(self.currentNode)
        elif direction == 'S':
            self.currentNode.setSouthNode(neighbor_node)
            neighbor_node.setNorthNode(self.currentNode)
        elif direction == 'E':
            self.currentNode.setEastNode(neighbor_node)
            neighbor_node.setWestNode(self.currentNode)
        elif direction == 'W':
            self.currentNode.setWestNode(neighbor_node)
            neighbor_node.setEastNode(self.currentNode)

    # Helper function to handle A* pathfinding to a known goal
    def AStar_search(self, start_node):
        goal_node = self.find_or_create_node(self.goalCoords[0], self.goalCoords[1], self.goalMap)
        openset = [(start_node.f_score, start_node)]
        start_node.g_score = start_node.f_score = 0
        cameFrom = {}
        while openset:
            current = heapq.heappop(openset)[1]
            if current == goal_node:
                return self.reconstruct_path(cameFrom, current)
            for direction in ['N', 'S', 'E', 'W']:
                neighbor = current.get_neighbor_node(direction)
                if neighbor and not neighbor.AStarVisited:
                    g_score = current.g_score + 1
                    if g_score < neighbor.g_score:
                        cameFrom[neighbor] = current
                        neighbor.g_score = g_score
                        neighbor.f_score = g_score + abs(goal_node.xCoord - neighbor.xCoord) + abs(goal_node.yCoord - neighbor.yCoord)
                        heapq.heappush(openset, (neighbor.f_score, neighbor))
        return random.choice(['N', 'S', 'E', 'W'])  # Fallback if no path found

    def reconstruct_path(self, cameFrom, node):
        path = []
        while node in cameFrom:
            path.append(self.get_direction(cameFrom[node], node))
            node = cameFrom[node]
        return path[-1] if path else random.choice(['N', 'S', 'E', 'W'])

class Node:
    def __init__(self, X, Y, map):
        self.xCoord = X
        self.yCoord = Y
        self.visited = False
        self.whatMap = map
        self.northNode = self.southNode = self.eastNode = self.westNode = None
        self.f_score = self.g_score = 999999  # for A*

    def setVisitedToYes(self):
        self.visited = True

    # Directional linking methods
    def setNorthNode(self, node): self.northNode = node
    def setSouthNode(self, node): self.southNode = node
    def setEastNode(self, node): self.eastNode = node
    def setWestNode(self, node): self.westNode = node
