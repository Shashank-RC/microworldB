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
        self.xCoord = 0
        self.yCoord = 0
        self.currentNode = Node(0, 0, 'main')
        self.map = {(0, 0, 'main'): self.currentNode}
        self.path_stack = []
        self.turn = -1
        self.goalCoords = None
        self.savedgoalCoords = None
        self.goalMap = None
        self.atExit = False  # Flag to wait at exit if found first
        self.last_teleporter = None
        self.teleporter_cooldown = 0
        self.hasAStarRunYet = False
        self.AStarPath = None
        self.AStarCount = 0
        self.max_turn = max_turns if max_turns else 800

    def update(self, percepts, msg):
        self.turn += 1

        # Receive data from Agent B
        #if msg:
        #    self.goalCoords = msg.get("goalCoords", self.goalCoords)
        #    self.map.update(msg.get("sharedMap", {}))
        #    if msg.get("teleporter"):
        #        self.last_teleporter = msg["teleporter"]
        #        self.teleporter_cooldown = 3

        # Outgoing message to Agent B
        #outgoing_msg = {
        #    "goalCoords": self.goalCoords,
        #    "sharedMap": self.map,
        #    "teleporter": self.last_teleporter if self.teleporter_cooldown == 0 else None,
        #}

        self.map = msg[1] if msg != None else self.map
        self.goalCoords = msg[0] if msg != None else self.goalCoords
        

        self.update_graph(percepts)

        # Detect exit or goal in the current cell
        if percepts['X'][0] == 'r':  # Exit cell
            self.goalCoords = (self.xCoord, self.yCoord)
            self.goalMap = self.currentNode.whatMap
            self.atExit = True  # Set waiting at exit if B finds it first
            return 'U', [self.goalCoords, self.map]  # Stay here to help guide Agent A
        elif percepts['X'][0].isdigit():  # Goal cell
            return 'U', [self.goalCoords, self.map]
        
        for direction in ['N', 'S', 'E', 'W']:
            if 'r' in percepts[direction] and self.goalCoords == None:
                self.path_stack.append(self.currentNode)
                return self.move_in_direction(direction), [self.goalCoords, self.map]
            
            if any(x in percepts[direction] for x in '0123456789'):
                self.path_stack.append(self.currentNode)
                return self.move_in_direction(direction), [self.goalCoords, self.map]

        # If at exit, wait here for Agent B if exit has been found
        if self.atExit:
            return None, [self.goalCoords, self.map]  # Remain stationary

        # Teleporter handling with cooldown
        '''
        if percepts['X'][0] in 'obyp' and self.teleporter_cooldown == 0:
            self.last_teleporter = percepts['X'][0]
            self.teleporter_cooldown = 3
            if self.currentNode.whatMap == 'main':
                self.xCoord, self.yCoord, self.currentNode.whatMap = 0, 0, percepts['X'][0]
            else:
                self.currentNode.whatMap = 'main'
            return 'U', [self.goalCoords, self.map]
        elif self.teleporter_cooldown > 0:
            self.teleporter_cooldown -= 1
        '''
        # Use A* if the exit or goal is known and proceed directly
        if self.goalCoords:
            if self.currentNode.whatMap!= 'main':
                backtrack_node = self.path_stack.pop()
                return self.backtrack_to_node(backtrack_node), [self.goalCoords, self.map]
            else:
                if self.hasAStarRunYet == False:
                    self.AStarPath = self.AStar_search(self.currentNode)
                    self.hasAStarRunYet = True
                if percepts['X'][0] == 'r':
                    return 'U', [self.goalCoords, self.map]
                self.AStarCount -= 1
                return self.AStarPath[self.AStarCount],[self.goalCoords, self.map]

        # Explore or backtrack if the goal or exit is unknown
        return self.explore_or_backtrack(), [self.goalCoords, self.map]

    def explore_or_backtrack(self):
        for direction in ['E', 'S', 'W', 'N']:
            next_node = self.get_neighbor_node(direction)
            if next_node and not next_node.Avisited:
                self.path_stack.append(self.currentNode)
                return self.move_in_direction(direction)

        # Backtrack only if no new areas to explore
        if self.path_stack:
            backtrack_node = self.path_stack.pop()
            return self.backtrack_to_node(backtrack_node)

        # Fallback: Random movement if path stack is empty
        return random.choice(['N', 'S', 'E', 'W'])

    def move_in_direction(self, direction):
        target_node = self.get_neighbor_node(direction)
        if not target_node:
            self.create_neighbor_node(direction)

        move_dict = {'N': (1, 0), 'S': (-1, 0), 'E': (0, 1), 'W': (0, -1)}
        dx, dy = move_dict[direction]
        self.xCoord += dx
        self.yCoord += dy
        self.currentNode = self.get_neighbor_node(direction)
        self.currentNode.setAVisitedToYes()
        return direction

    def get_neighbor_node(self, direction):
        return {
            'N': self.currentNode.northNode,
            'S': self.currentNode.southNode,
            'E': self.currentNode.eastNode,
            'W': self.currentNode.westNode
        }.get(direction)

    def backtrack_to_node(self, backtrack_node):
        for direction in ['N', 'S', 'E', 'W']:
            if self.get_neighbor_node(direction) == backtrack_node:
                return self.move_in_direction(direction)
        return random.choice(['N', 'S', 'E', 'W'])

    def update_graph(self, percepts):
        for direction in ['N', 'S', 'E', 'W']:
            if percepts[direction][0] != 'w':
                dx, dy = (1 if direction == 'N' else -1 if direction == 'S' else 0,
                          1 if direction == 'E' else -1 if direction == 'W' else 0)
                neighbor_node = self.find_or_create_node(self.xCoord + dx, self.yCoord + dy)
                self.link_nodes(direction, neighbor_node)

    def find_or_create_node(self, x, y, map=None):
        key = (x, y, map or self.currentNode.whatMap)
        if key in self.map:
            return self.map[key]
        new_node = Node(x, y, map or self.currentNode.whatMap)
        self.map[key] = new_node
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
                if neighbor and not neighbor.aiAAStarVisited:
                    g_score = current.g_score + 1
                    if g_score < neighbor.g_score:
                        cameFrom[neighbor] = current
                        neighbor.g_score = g_score
                        neighbor.f_score = g_score + abs(goal_node.xCoord - neighbor.xCoord) + abs(goal_node.yCoord - neighbor.yCoord)
                        neighbor.aiAAStarVisited = True
                        f_score = neighbor.f_score
                        heapq.heappush(openset, (f_score, neighbor))
        return random.choice(['N', 'S', 'E', 'W'])

    def reconstruct_path(self, cameFrom, node):
        path = []
        while node in cameFrom:
            direction = self.get_direction(cameFrom[node], node)
            path.append(direction)
            node = cameFrom[node]
        return path

    def get_direction(self, from_node, to_node):
        if from_node.northNode == to_node:
            return 'N'
        elif from_node.southNode == to_node:
            return 'S'
        elif from_node.eastNode == to_node:
            return 'E'
        elif from_node.westNode == to_node:
            return 'W'

class Node:
    def __init__(self, X, Y, map_name):
        self.xCoord = X
        self.yCoord = Y
        self.whatMap = map_name
        self.Avisited = False
        self.Bvisited = False
        self.northNode = self.southNode = self.eastNode = self.westNode  = self.teleportNode = None
        self.f_score = float('inf')
        self.g_score = float('inf')
        self.aiAAStarVisited = self.aiBAStarVisited= False
    
    def setAVisitedToYes(self):
        self.Avisited = True

    def setBVisitedToYes(self):
        self.Bvisited = True

    def setNorthNode(self, node): self.northNode = node
    def setSouthNode(self, node): self.southNode = node
    def setEastNode(self, node): self.eastNode = node
    def setWestNode(self, node): self.westNode = node

    def get_neighbor_node(self, direction):
        return {
            'N': self.northNode,
            'S': self.southNode,
            'E': self.eastNode,
            'W': self.westNode
        }.get(direction)
    
    def __lt__(self, other):
        return self.f_score < other.f_score 
