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
from aiA import Node

class AI:
    def __init__(self, max_turns):
        self.xCoord = 0
        self.yCoord = 0
        self.currentNode = Node(0, 0)
        self.map = [self.currentNode]
        self.path_queue = deque()  # BFS queue for exploration
        self.path_stack = []       # Stack for backtracking
        self.numOfTurns = max_turns
        self.turn = -1
        self.goalCoords = None
        self.goalMap = None
        self.hasBFoundGoal = False

    def update(self, percepts, msg):

        print(f"B received the message: {msg}")
        
        # Update turn count and check message for goal information
        self.turn += 1
        self.goalCoords = msg[1] if msg else None
        self.map = msg[0] if msg else self.map
        self.update_graph(percepts)

        # Use A* to find the shortest path if the goal location is known
        if self.goalCoords is not None:
            return self.AStar_search(self.currentNode), msg

        # Check for goal or teleport on the current cell
        if percepts['X'][0] in '0123456789rb':
            return 'U', [self.map, self.goalCoords]

        # BFS exploration and backtracking integration
        for direction in ['N', 'E', 'S', 'W']:
            neighbor_node = self.get_neighbor_node(direction)
            if neighbor_node and not neighbor_node.visited:
                self.path_queue.append(direction)  # Add to BFS queue
                self.path_stack.append(self.currentNode)  # Save for backtracking

        # Prioritize BFS direction if available
        if self.path_queue:
            next_direction = self.path_queue.popleft()
            return self.move_in_direction(next_direction), [self.map, self.goalCoords]

        # If BFS queue is empty, initiate backtracking
        if self.path_stack:
            backtrack_node = self.path_stack.pop()
            return self.backtrack_to_node(backtrack_node), [self.map, self.goalCoords]

        # If all else fails, fallback to random movement
        return random.choice(['N', 'S', 'E', 'W']), "B moving randomly due to empty queue and stack"

    # Move in the specified direction
    def move_in_direction(self, direction):
        target_node = self.get_neighbor_node(direction)
        if target_node is None:
            print(f"Creating new node in direction {direction} before moving.")
            self.create_neighbor_node(direction)

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

    # Backtrack to a specified node
    def backtrack_to_node(self, backtrack_node):
        if self.currentNode.northNode == backtrack_node:
            return self.move_in_direction('N')
        elif self.currentNode.southNode == backtrack_node:
            return self.move_in_direction('S')
        elif self.currentNode.eastNode == backtrack_node:
            return self.move_in_direction('E')
        elif self.currentNode.westNode == backtrack_node:
            return self.move_in_direction('W')

    # Update graph with newly perceived cells
    def update_graph(self, percepts):
        directions = {
            'N': (1, 0),
            'S': (-1, 0),
            'E': (0, 1),
            'W': (0, -1)
        }
        for direction, (dx, dy) in directions.items():
            if percepts[direction][0] != 'w':
                neighbor_node = self.find_or_create_node(self.xCoord + dx, self.yCoord + dy)
                self.link_nodes(direction, neighbor_node)

    # Find or create a new node at the specified coordinates
    def find_or_create_node(self, x, y):
        for node in self.map:
            if node.xCoord == x and node.yCoord == y:
                return node
        new_node = Node(x, y)
        self.map.append(new_node)
        print(f"Created new node at x={x}, y={y}")
        return new_node

    # Link the current node to the neighbor in the specified direction
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

    # Get the neighboring node in the specified direction
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

    # A* Search to find shortest path to a known goal or exit
    def AStar_search(self, start_node):
        goal_node = self.find_or_create_node(self.goalCoords[0], self.goalCoords[1])

        openset = []
        start_node.f_score = 0
        start_node.g_score = 0
        heapq.heappush(openset, (start_node.f_score, start_node))

        came_from = {}

        while openset:
            current_node = heapq.heappop(openset)[1]
            current_node.AStarVisited = True

            if current_node == goal_node:
                return self.reconstruct_path(came_from, current_node)

            for direction in ['N', 'S', 'E', 'W']:
                neighbor = current_node.get_neighbor_node(direction)
                if neighbor and not neighbor.AStarVisited:
                    tentative_g_score = current_node.g_score + 1

                    if tentative_g_score < neighbor.g_score:
                        came_from[neighbor] = current_node
                        neighbor.g_score = tentative_g_score
                        neighbor.f_score = tentative_g_score + self.heuristic(goal_node, neighbor)
                        if (neighbor.f_score, neighbor) not in openset:
                            heapq.heappush(openset, (neighbor.f_score, neighbor))

        return random.choice(['N', 'S', 'E', 'W'])  # Default if no path found

    # Heuristic function for A* (Manhattan distance)
    def heuristic(self, goalNode, otherNode):
        return abs(goalNode.xCoord - otherNode.xCoord) + abs(goalNode.yCoord - otherNode.yCoord)

    # Reconstruct path to follow back to the goal node after A* completion
    def reconstruct_path(self, came_from, current_node):
        path = []
        while current_node in came_from:
            previous_node = came_from[current_node]
            direction = self.get_direction(previous_node, current_node)
            path.append(direction)
            current_node = previous_node
        return path[-1] if path else random.choice(['N', 'S', 'E', 'W'])  # Take the next step

    # Get direction between two nodes
    def get_direction(self, from_node, to_node):
        if from_node.northNode == to_node:
            return 'N'
        elif from_node.southNode == to_node:
            return 'S'
        elif from_node.eastNode == to_node:
            return 'E'
        elif from_node.westNode == to_node:
            return 'W'
