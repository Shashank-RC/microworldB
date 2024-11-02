# Kaleb Hannan, Shashank Reddy
#
# We were working in the same github repo 
#
# APPROACH: Look In aiA File for discriction on approch for both of the AI's what we did 
# how the AI's are similar and how they are differnt.
#
#aiB Approch: 
# This AI first uses a depth first search to explore the map. 
# The ai will prioritize going West first then North, then East and lastly South.
# This will make it so that the ai will primaraly search the left and top of the map.
# aiB will always send 2 things to aiB the updated map after its move and also ether None or the exit coordinates if it fould the exit.
# aiB will also not be able to use the teleporters to explore the map. 
# aiB will only use the teleopters if the exit is thought one of them.
# It also has a goal based approch were it will move tords the objectivs and the exit if it sees it.
# If aiB is on the exit it will then exit the map.
# If aiA finds the exit then it will use the A* method to find its way to the goal if in the 'main' map
# If the goal if thought a teleporter then it will A* to the teleporter then A* to the exit.



import random
import heapq
from aiA import Node  # Assuming aiA contains the Node class

class AI:
    def __init__(self, max_turns):
        self.xCoord = 0
        self.yCoord = 0
        self.currentNode = Node(0, 0, 'main')
        self.map = {(0, 0, 'main'): self.currentNode}
        self.path_stack = []
        self.turn = -1
        self.goalCoords = None
        self.goalMap = None
        self.atExit = False
        self.last_teleporter = None
        self.teleporter_cooldown = 0
        self.hasAStarRunYet = False
        self.AStarPath = None
        self.AStarCount = 0
        self.max_turn = max_turns if max_turns else 800

    def update(self, percepts, msg):
        self.turn += 1

        # Process incoming data from Agent A, including teleporter use
        if msg:
            # Update goal location, map, and A* path if received from Agent A
            self.goalCoords = msg[0] if msg[0] else self.goalCoords
            self.map = msg[1] if msg[1] else self.map
            if len(msg) > 2 and msg[2] is not None:
                self.AStarPath = msg[2]
                self.AStarCount = len(self.AStarPath) - 1
                self.hasAStarRunYet = True

            # If Agent A used a teleporter to reach the exit, Agent B should adapt
            if msg[0] and msg[1] and msg[2]:  # Check if we received goal coordinates, map, and path
                self.goalCoords = msg[0]  # Update with Agent A's teleport destination
                self.goalMap = self.currentNode.whatMap if msg[0] else self.goalMap
                self.clear_internal_paths()  # Clear paths as they may no longer be valid

        self.update_graph(percepts)

        # If A* path is available, prioritize following it
        if self.AStarPath and self.hasAStarRunYet:
            if 0 <= self.AStarCount < len(self.AStarPath):
                move_cmd = self.AStarPath[self.AStarCount]
                self.AStarCount -= 1
                return move_cmd, [self.goalCoords, self.map, self.AStarPath]
            else:
                # Reset A* path if exhausted
                self.AStarPath = None
                self.hasAStarRunYet = False

        # Detect exit or goal in the current cell if no A* path is set
        if percepts['X'][0] == 'r':  # Exit cell
            self.goalCoords = (self.xCoord, self.yCoord)
            self.goalMap = self.currentNode.whatMap
            self.atExit = True
            if not self.hasAStarRunYet:
                self.AStarPath = self.AStar_search(self.currentNode)
                self.hasAStarRunYet = True
                self.AStarCount = len(self.AStarPath) - 1
            return 'U', [self.goalCoords, self.map, self.AStarPath]
        
        elif percepts['X'][0].isdigit():  # Goal cell
            return 'U', [self.goalCoords, self.map]

        # Detect goals or exits in surrounding cells
        for direction in ['N', 'S', 'E', 'W']:
            if 'r' in percepts[direction] and not self.goalCoords:
                self.path_stack.append(self.currentNode)
                return self.move_in_direction(direction), [self.goalCoords, self.map]
            if any(x in percepts[direction] for x in '0123456789'):
                self.path_stack.append(self.currentNode)
                return self.move_in_direction(direction), [self.goalCoords, self.map]

        # Teleporter handling with cooldown
        if percepts['X'][0] in 'obyp' and self.teleporter_cooldown == 0:
            if msg and len(msg) > 2 and msg[2] is not None:
                self.last_teleporter = percepts['X'][0]
                self.teleporter_cooldown = 3
                if self.currentNode.whatMap == 'main':
                    self.xCoord, self.yCoord, self.currentNode.whatMap = 0, 0, percepts['X'][0]
                else:
                    self.currentNode.whatMap = 'main'
                self.path_stack = []  # Clear path_stack after teleporting
                return 'U', [self.goalCoords, self.map, self.AStarPath]

        elif self.teleporter_cooldown > 0:
            self.teleporter_cooldown -= 1

        # Use A* if the exit or goal is known and proceed directly
        if self.goalCoords:
            if self.currentNode.whatMap != 'main':
                if self.path_stack:
                    backtrack_node = self.path_stack.pop()
                    return self.backtrack_to_node(backtrack_node), [self.goalCoords, self.map, self.AStarPath]
                else:
                    return self.explore_or_backtrack(), [self.goalCoords, self.map]
            else:
                if not self.hasAStarRunYet:
                    self.AStarPath = self.AStar_search(self.currentNode)
                    self.hasAStarRunYet = True
                    self.AStarCount = len(self.AStarPath) - 1
                if percepts['X'][0] == 'r':
                    return 'U', [self.goalCoords, self.map, self.AStarPath]
                
                if self.AStarPath and 0 <= self.AStarCount < len(self.AStarPath):
                    move_cmd = self.AStarPath[self.AStarCount]
                    self.AStarCount -= 1
                    return move_cmd, [self.goalCoords, self.map, self.AStarPath]
                else:
                    return self.explore_or_backtrack(), [self.goalCoords, self.map]

        # Fallback to exploration or backtracking
        return self.explore_or_backtrack(), [self.goalCoords, self.map]

    def explore_or_backtrack(self):
        for direction in ['W', 'N', 'E', 'S']:
            next_node = self.get_neighbor_node(direction)
            if next_node and not next_node.Bvisited:
                self.path_stack.append(self.currentNode)
                return self.move_in_direction(direction)

        if self.path_stack:
            backtrack_node = self.path_stack.pop()
            return self.backtrack_to_node(backtrack_node)

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
        self.currentNode.setBVisitedToYes()
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
                if neighbor and not neighbor.aiBAStarVisited:
                    g_score = current.g_score + 1
                    if g_score < neighbor.g_score:
                        cameFrom[neighbor] = current
                        neighbor.g_score = g_score
                        neighbor.f_score = g_score + abs(goal_node.xCoord - neighbor.xCoord) + abs(goal_node.yCoord - neighbor.yCoord)
                        neighbor.aiBAStarVisited = True
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
    
    def clear_internal_paths(self):
        """ Clear any internal paths that may be invalid after teleportation or exit update. """
        self.path_stack = []
        self.AStarPath = None
        self.hasAStarRunYet = False