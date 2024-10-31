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
        self.last_teleporter = None    # Track the last teleporter used
        self.teleporter_cooldown = 0   # Counter to avoid immediate teleporter reuse

    def update(self, percepts, msg):
        # Set default values for the message
        if msg is None:
            msg = [self.map, self.goalCoords]

        # Process message contents
        self.goalCoords = msg[1]
        self.map = msg[0]
        self.turn += 1
        self.update_graph(percepts)

        # Check if on the goal (exit cell 'r') and exit immediately
        if percepts['X'][0] == 'r':
            self.goalCoords = (self.xCoord, self.yCoord)
            self.goalMap = self.currentNode.whatMap
            self.hasAFoundGoal = True
            # Immediate exit if on the exit cell
            return 'U', [self.map, self.goalCoords]
        
        for direction in ['N', 'S', 'E', 'W']:
            if 'r' in percepts[direction]:
                return self.move_in_direction(direction), [self.map, self.goalCoords]

        # Exit strategy near turn limit
        if self.goalCoords is not None and self.hasAFoundGoal:
            self.distanceFromGoal += 1
        if (self.turn + self.distanceFromGoal - 1) >= self.numOfTurns:
            if percepts['X'][0] == 'r':  # Exit if on goal cell
                return 'U', [self.map, self.goalCoords]
            # Backtrack towards exit if close to turn limit
            backtrack_node = self.path_stack.pop() if self.path_stack else None
            return self.backtrack_to_node(backtrack_node), [self.map, self.goalCoords]

        # Immediate goal activation if detected
        if percepts['X'][0].isdigit():
            return 'U', [self.map, self.goalCoords]

        # Teleporter handling with cooldown
        if percepts['X'][0] in 'obyp':
            if self.teleporter_cooldown > 0:
                self.teleporter_cooldown -= 1
                return self.explore_or_backtrack(), [self.map, self.goalCoords]

            self.last_teleporter = percepts['X'][0]
            self.teleporter_cooldown = 3
            if self.currentMap == 'main':
                self.xCoord, self.yCoord, self.currentMap = 0, 0, percepts['X'][0]
            else:
                self.currentMap = 'main'
            return 'U', [self.map, self.goalCoords] 

        # Reset teleporter data when moving without teleportation
        self.last_teleporter = None
        self.teleporter_cooldown = max(0, self.teleporter_cooldown - 1)

        # Use A* pathfinding if the goal is known
        #if self.goalCoords is not None:
            #return self.AStar_search(self.currentNode), [self.map, self.goalCoords]

        # Explore using DFS, prioritize unvisited neighbors
        return self.explore_or_backtrack(), [self.map, self.goalCoords]

    def explore_or_backtrack(self):
        for direction in ['W', 'N', 'E', 'S']:
            next_node = self.get_neighbor_node(direction)
            if next_node and not next_node.visited:
                self.path_stack.append(self.currentNode)
                return self.move_in_direction(direction)

        if self.path_stack:
            backtrack_node = self.path_stack.pop()
            return self.backtrack_to_node(backtrack_node)

        return random.choice(['N', 'S', 'E', 'W'])

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

    def backtrack_to_node(self, backtrack_node):
        return next((self.move_in_direction(d) for d in ['N', 'S', 'E', 'W'] if self.get_neighbor_node(d) == backtrack_node), None)

    def update_graph(self, percepts):
        for direction in ['N', 'S', 'E', 'W']:
            if percepts[direction][0] != 'w':
                neighbor_node = self.find_or_create_node(
                    self.xCoord + (1 if direction == 'N' else -1 if direction == 'S' else 0),
                    self.yCoord + (1 if direction == 'E' else -1 if direction == 'W' else 0),
                    self.currentMap
                )
                self.link_nodes(direction, neighbor_node)

    def find_or_create_node(self, x, y, map=None):
        for node in self.map:
            if node.xCoord == x and node.yCoord == y and node.whatMap == (map or self.currentMap):
                return node
        new_node = Node(x, y, map or self.currentMap)
        self.map.append(new_node)
        print(f"Created new node at x={x}, y={y} on map={map or self.currentMap}")
        return new_node

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
        return random.choice(['N', 'S', 'E', 'W'])

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
        self.f_score = self.g_score = 999999
        self.AStarVisited = False
    def setVisitedToYes(self):
        self.visited = True
    
    def __lt__(self, other):
        return self.f_score < other.f_score

    def setNorthNode(self, node): self.northNode = node
    def setSouthNode(self, node): self.southNode = node
    def setEastNode(self, node): self.eastNode = node
    def setWestNode(self, node): self.westNode = node

    def get_neighbor_node(self, direction):
        if direction == 'N':
            return self.northNode
        elif direction == 'S':
            return self.southNode
        elif direction == 'E':
            return self.eastNode
        elif direction == 'W':
            return self.westNode
        return None