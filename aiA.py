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
        self.goalMap = None
        self.atExit = False  # Flag to wait at exit if found first
        self.last_teleporter = None
        self.teleporter_cooldown = 0

    def update(self, percepts, msg):
        print(f"A received the message: {msg}")
        self.turn += 1

        # Receive data from Agent B
        if msg:
            self.goalCoords = msg.get("goalCoords", self.goalCoords)
            self.map.update(msg.get("sharedMap", {}))
            if msg.get("teleporter"):
                self.last_teleporter = msg["teleporter"]
                self.teleporter_cooldown = 3

        # Outgoing message to Agent B
        outgoing_msg = {
            "goalCoords": self.goalCoords,
            "sharedMap": self.map,
            "teleporter": self.last_teleporter if self.teleporter_cooldown == 0 else None,
        }

        self.update_graph(percepts)

        # Detect goal or exit
        if percepts['X'][0] == 'r':  # Exit cell
            self.goalCoords = (self.xCoord, self.yCoord)
            self.goalMap = self.currentNode.whatMap
            self.atExit = True  # Indicate that A will wait here if exit is found
            return 'U', outgoing_msg
        elif percepts['X'][0].isdigit():  # Goal cell
            self.goalCoords = (self.xCoord, self.yCoord)
            return 'U', outgoing_msg

        # If at exit, wait here for Agent B if exit has been found
        if self.atExit:
            return None, outgoing_msg  # Remain stationary

        # Teleporter handling with cooldown
        if percepts['X'][0] in 'obyp' and self.teleporter_cooldown == 0:
            self.last_teleporter = percepts['X'][0]
            self.teleporter_cooldown = 3
            if self.currentNode.whatMap == 'main':
                self.xCoord, self.yCoord, self.currentNode.whatMap = 0, 0, percepts['X'][0]
            else:
                self.currentNode.whatMap = 'main'
            return 'U', outgoing_msg
        elif self.teleporter_cooldown > 0:
            self.teleporter_cooldown -= 1

        # Use A* if the exit or goal is known and proceed directly
        if self.goalCoords:
            return self.AStar_search(self.currentNode), outgoing_msg

        # Explore or backtrack if the goal or exit is unknown
        return self.explore_or_backtrack(), outgoing_msg

    def explore_or_backtrack(self):
        possibleDirections = []
        for direction in ['N', 'S', 'E', 'W']:
            next_node = self.get_neighbor_node(direction)
            if next_node and not next_node.visited:
                possibleDirections.append(direction)

        # Prioritize exploration of new areas
        if possibleDirections:
            direction = random.choice(possibleDirections)
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
        self.currentNode.setVisitedToYes()
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
                if neighbor and not neighbor.AStarVisited:
                    g_score = current.g_score + 1
                    if g_score < neighbor.g_score:
                        cameFrom[neighbor] = current
                        neighbor.g_score = g_score
                        neighbor.f_score = g_score + abs(goal_node.xCoord - neighbor.xCoord) + abs(goal_node.yCoord - neighbor.yCoord)
                        neighbor.AStarVisited = True
                        heapq.heappush(openset, (neighbor.f_score, neighbor))
        return random.choice(['N', 'S', 'E', 'W'])

    def reconstruct_path(self, cameFrom, node):
        path = []
        while node in cameFrom:
            direction = self.get_direction(cameFrom[node], node)
            path.append(direction)
            node = cameFrom[node]
        return path[-1] if path else random.choice(['N', 'S', 'E', 'W'])

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
        self.visited = False
        self.northNode = self.southNode = self.eastNode = self.westNode = None
        self.f_score = float('inf')
        self.g_score = float('inf')
        self.AStarVisited = False
    
    def setVisitedToYes(self):
        self.visited = True

    def setNorthNode(self, node): self.northNode = node
    def setSouthNode(self, node): self.southNode = node
    def setEastNode(self, node): self.eastNode = node
    def setWestNode(self, node): self.westNode = node
