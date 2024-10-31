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
from collections import deque
from aiA import Node  # Assuming aiA contains the Node class

class AI:
    def __init__(self, max_turns):
        # Initialize agent's position, map, and exploration settings
        self.xCoord = 0
        self.yCoord = 0
        self.currentNode = Node(0, 0, 'main')
        self.map = [self.currentNode]
        self.path_queue = deque()      # BFS queue for exploration
        self.path_stack = []           # Stack for backtracking when BFS queue is empty
        self.numOfTurns = max_turns if max_turns is not None else 1000
        self.turn = -1
        self.goalCoords = None
        self.goalMap = None
        self.distanceFromGoal = 0
        self.hasBFoundGoal = False
        self.last_teleporter = None
        self.teleporter_cooldown = 0   # Cooldown to prevent immediate teleporter reuse

    def update(self, percepts, msg):
        """
        Updates agent's actions each turn based on BFS exploration, A* goal pathfinding, and backtracking.
        Receives percepts of nearby cells and a message from Agent A containing map and goal info.
        """
        print(f"B received the message: {msg}")

        # Check if msg is None and set default values if needed
        if msg is None:
            msg = [self.map, self.goalCoords]

        # Process message contents
        self.goalCoords = msg[1]
        self.map = msg[0]
        self.turn += 1
        self.update_graph(percepts)

        # Requirement: Use A* search if goal location is known
        if self.goalCoords:
            return self.AStar_search(self.currentNode), [self.map, self.goalCoords]

        # Requirement: Check if current cell contains a goal or teleport cell
        if percepts['X'][0] in '0123456789rb':
            return 'U', [self.map, self.goalCoords]

        # Teleporter Handling: If on a teleporter, use it unless cooldown is active
        if percepts['X'][0] in 'obyp':
            if self.teleporter_cooldown == 0:
                self.last_teleporter = percepts['X'][0]
                self.teleporter_cooldown = 3  # Cooldown period to prevent immediate reuse

                # Switch maps on teleporter use
                if self.currentNode.whatMap == 'main':
                    self.xCoord, self.yCoord, self.currentNode.whatMap = 0, 0, percepts['X'][0]
                else:
                    self.currentNode.whatMap = 'main'
                return 'U', [self.map, self.goalCoords]
            else:
                self.teleporter_cooldown -= 1  # Decrement cooldown each turn

        # BFS Exploration: Add unvisited neighboring directions to queue
        for direction in ['N', 'E', 'S', 'W']:
            neighbor_node = self.get_neighbor_node(direction)
            if neighbor_node and not neighbor_node.visited:
                self.path_queue.append(direction)
                self.path_stack.append(self.currentNode)  # Save for backtracking

        # Requirement: Prioritize BFS queue direction if available
        if self.path_queue:
            next_direction = self.path_queue.popleft()
            return self.move_in_direction(next_direction), [self.map, self.goalCoords]

        # Requirement: Use backtracking when BFS queue is empty
        if self.path_stack:
            backtrack_node = self.path_stack.pop()
            return self.backtrack_to_node(backtrack_node), [self.map, self.goalCoords]

        # Fallback: Random movement when all options exhausted
        return random.choice(['N', 'S', 'E', 'W']), "B moving randomly due to empty queue and stack"

    # This method moves the agent in a specified direction and updates coordinates
    def move_in_direction(self, direction):
        target_node = self.get_neighbor_node(direction)
        if target_node is None:
            print(f"Creating new node in direction {direction} before moving.")
            self.create_neighbor_node(direction)

        # Update position based on direction and move agent to that node
        if direction == 'N':
            self.xCoord += 1
            self.currentNode = self.currentNode.northNode
        elif direction == 'S':
            self.xCoord -= 1
            self.currentNode = self.currentNode.southNode
        elif direction == 'E':
            self.yCoord += 1
            self.currentNode = self.currentNode.eastNode
        elif direction == 'W':
            self.yCoord -= 1
            self.currentNode = self.currentNode.westNode
        
        if self.currentNode is None:
            raise ValueError(f"Error: Moved in direction {direction}, but currentNode is None.")

        print(f"Moved {direction}, new position: x={self.xCoord}, y={self.yCoord}")
        self.currentNode.setVisitedToYes()
        return direction

    # Adds a neighboring node in the specified direction if it doesn’t already exist
    def create_neighbor_node(self, direction):
        # Map directions to coordinate adjustments
        move_dict = {'N': (1, 0), 'S': (-1, 0), 'E': (0, 1), 'W': (0, -1)}
        dx, dy = move_dict[direction]
        
        # Calculate the new coordinates for the neighboring node
        new_x, new_y = self.xCoord + dx, self.yCoord + dy
        
        # Create or find a node at the new coordinates
        new_node = self.find_or_create_node(new_x, new_y, self.currentNode.whatMap)
        
        # Link the newly created node with the current node in the specified direction
        self.link_nodes(direction, new_node)

    # Backtracking function to revisit previous nodes when BFS runs out of paths
    def backtrack_to_node(self, backtrack_node):
        return next((self.move_in_direction(d) for d in ['N', 'S', 'E', 'W'] if self.get_neighbor_node(d) == backtrack_node), None)

    # Graph update method that links new nodes in the map based on percepts
    def update_graph(self, percepts):
        directions = {
            'N': (1, 0),
            'S': (-1, 0),
            'E': (0, 1),
            'W': (0, -1)
        }
        for direction, (dx, dy) in directions.items():
            if percepts[direction][0] != 'w':  # Only proceed if cell is walkable
                neighbor_node = self.find_or_create_node(self.xCoord + dx, self.yCoord + dy)
                self.link_nodes(direction, neighbor_node)

    # This function finds or creates a new node if one does not already exist at the specified coordinates
    def find_or_create_node(self, x, y, map=None):
        # Search for an existing node with the specified coordinates and map
        for node in self.map:
            if node.xCoord == x and node.yCoord == y and node.whatMap == (map or self.currentNode.whatMap):
                return node
        # If not found, create a new node
        new_node = Node(x, y, map or self.currentNode.whatMap)
        self.map.append(new_node)
        print(f"Created new node at x={x}, y={y} on map={map or self.currentNode.whatMap}")
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

    # A* search function for finding shortest path to goal or exit when known
    def AStar_search(self, start_node):
        goal_node = self.find_or_create_node(self.goalCoords[0], self.goalCoords[1])

        # Open set for A* pathfinding with (f_score, node) tuples
        openset = []
        start_node.f_score = 0
        start_node.g_score = 0
        heapq.heappush(openset, (start_node.f_score, start_node))

        came_from = {}

        while openset:
            current_node = heapq.heappop(openset)[1]
            current_node.AStarVisited = True

            # Requirement: Check if goal has been reached
            if current_node == goal_node:
                return self.reconstruct_path(came_from, current_node)

            # Explore neighbors in four directions
            for direction in ['N', 'S', 'E', 'W']:
                neighbor = current_node.get_neighbor_node(direction)
                if neighbor and not neighbor.AStarVisited:
                    tentative_g_score = current_node.g_score + 1

                    # Update if a shorter path to neighbor is found
                    if tentative_g_score < neighbor.g_score:
                        came_from[neighbor] = current_node
                        neighbor.g_score = tentative_g_score
                        neighbor.f_score = tentative_g_score + self.heuristic(goal_node, neighbor)
                        if (neighbor.f_score, neighbor) not in openset:
                            heapq.heappush(openset, (neighbor.f_score, neighbor))

        # Requirement: Return fallback random direction if no path found
        return random.choice(['N', 'S', 'E', 'W'])

    # Manhattan distance heuristic for A* search
    def heuristic(self, goalNode, otherNode):
        return abs(goalNode.xCoord - otherNode.xCoord) + abs(goalNode.yCoord - otherNode.yCoord)

    # Reconstructs path to goal node after A* search is complete
    def reconstruct_path(self, came_from, current_node):
        path = []
        while current_node in came_from:
            previous_node = came_from[current_node]
            direction = self.get_direction(previous_node, current_node)
            path.append(direction)
            current_node = previous_node
        return path[-1] if path else random.choice(['N', 'S', 'E', 'W'])

    # Helper function to get direction between two nodes
    def get_direction(self, from_node, to_node):
        if from_node.northNode == to_node:
            return 'N'
        elif from_node.southNode == to_node:
            return 'S'
        elif from_node.eastNode == to_node:
            return 'E'
        elif from_node.westNode == to_node:
            return 'W'
