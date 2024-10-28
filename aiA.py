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


class AI:
    def __init__(self, max_turns):
        self.xCoord = 0
        self.yCoord = 0
        self.currentNode = Node(0, 0)
        self.map = [self.currentNode]  
        self.path_stack = []  
        self.last_direction = None  
        self.numOfTurns = max_turns
        self.turn = -1
        self.goalCoords = None
        self.distanceFromGoal = 0
        self.hasAFoundGoal = False
        
    def update(self, percepts, msg):

        self.turn += 1
        self.goalCoords = msg[1]
        self.map = msg[0]
        # Agent A will use depth first search to find the goal
        if percepts['X'][0] == 'r' and self.goalCoord == None:
            self.goalCoord = (self.xCoord,self.yCoord)
            self.hasAFoundGoal = True
        
        #if aiA has found the goal keep distance from goal so that we know when to go back.
        if self.goalCoord != None and self.hasAFoundGoal == True:
            self.distanceFromGoal += 1

        if (self.turn + self.distanceFromGoal - 1) == self.numOfTurns:
            #need to backtrack to goal.
            x=None

        if ['X'][0] == '0' or ['X'][0] == '1' or ['X'][0] == '2' or ['X'][0] == '3' or ['X'][0] == '4' or ['X'][0] == '5' or ['X'][0] == '6' or ['X'][0] == '7' or ['X'][0] == '8' or ['X'][0] == '9':
            msg = [self.map, self.goalCoords ]
            return 'U', msg

        if  

        print(f"A received the message: {msg}")

        match percepts['X'][0]:
            case '0' | '1' | 'r' | 'b':
                return 'U', None
            case _:
                return random.choice(['N', 'S', 'E', 'W']), "A moving"

    #This functions is used to return the direction of the node when it moves     
    def move_in_direction(self, direction):
        target_node = self.get_neighbor_node(direction)
        if target_node is None:
            print(f"Creating new node in direction {direction} before moving.")
            self.create_neighbor_node(direction)  # Ensure node exists before moving

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
        self.currentNode.setVisitedToYes()  # Mark the node as visited
        return direction
    
    #This function is used to backtrack nodes
    def backtrack_to_node(self, backtrack_node):
        if self.currentNode.northNode == backtrack_node:
            return self.move_in_direction('N')
        elif self.currentNode.southNode == backtrack_node:
            return self.move_in_direction('S')
        elif self.currentNode.eastNode == backtrack_node:
            return self.move_in_direction('E')
        elif self.currentNode.westNode == backtrack_node:
            return self.move_in_direction('W')

    #This function is used to update the map the AI's are using
    def update_graph(self, percepts):
        directions = {
            'N': (1, 0),
            'S': (-1, 0),
            'E': (0, 1),
            'W': (0, -1)
        }
        for direction, (dx, dy) in directions.items():
            if percepts[direction][0] == 'g':  # Ground is walkable
                neighbor_node = self.find_or_create_node(self.xCoord + dx, self.yCoord + dy)
                self.link_nodes(direction, neighbor_node)

    #This function is used to find a node a create a new node if one is not already there
    def find_or_create_node(self, x, y):
        for node in self.map:
            if node.xCoord == x and node.yCoord == y:
                return node
        new_node = Node(x, y)
        self.map.append(new_node)
        print(f"Created new node at x={x}, y={y}")
        return new_node

    # This function is used to create a new node before the agent moves to if if one is not present.
    def create_neighbor_node(self, direction):
        directions = {
            'N': (1, 0),
            'S': (-1, 0),
            'E': (0, 1),
            'W': (0, -1)
        }
        dx, dy = directions[direction]
        new_node = self.find_or_create_node(self.xCoord + dx, self.yCoord + dy)
        self.link_nodes(direction, new_node)

    # This function creates the link between two nodes.
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

    #This function returns the Node in a direction 
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
    
class Node:
    def __init__(self, X, Y):
        self.xCoord = X
        self.yCoord = Y
        self.northNode = None
        self.southNode = None
        self.eastNode = None
        self.westNode = None
        self.visited = False
    
    def setNorthNode(self, node):
        self.northNode = node
    
    def setSouthNode(self, node):
        self.southNode = node
    
    def setEastNode(self, node):
        self.eastNode = node
    
    def setWestNode(self, node):
        self.westNode = node
    
    def setVisitedToYes(self):
        self.visited = True