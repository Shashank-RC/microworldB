# Kaleb Hannan, Shashank Reddy
#
# We were working in the same github repo 
#
# APPROACH: [WRITE AN OVERVIEW OF YOUR APPROACH HERE.]

# DISCLAMERS: We have spent over 30 hours in the last week working on this project and the teleportation is still not working proporly
# When we are not using the teleper our A* search seemed to be working. as soon as we added the teleperter back in A* was could 
# not find a path to the exit node.  I do not know why I have tryed to fix thie issse for the las 5 hours and have still not sloved it
# We are leving the assinment here becsue we are completly stumped and do not know were to go from were we are.  We have been looking 
# at the code for so long our heads have starte to hurt.  Also are A* sometime will just not be able to find a path even if the AI has gone
# over the exit.  We also spent a lot of time trying to figure this out with no luck it was odd sometime it would work other times it would 
# not depending on where the node was. (I think that this was our hiuristic but I do not know how to improve or fix it.)


#   Our initial approach to this project was this: aiA would use the depth-first search approach we 
# made when creating our AI for project one.  aiB would then use a depth-first search to move 
# around the map, and its initial goal would be to find the objectives, whereas aiA’s initial goal 
# would be to find the exit of the map.  We thought that doing this it would make it so that they
# were each trying to do different things and also so that they would cover the most amount of 
# ground. In the case where an AI found a goal, it would keep a count of how far away it moved
# from the goal, and then when it got close to the max turn, it would backtrack to the exit.  The AI 
# that did not find the exit would then use an A* shortest path algorithm to try and find its way to
# the exit before the maximum number of turns.  When doing this, it was a complete failure. The 
# AIB breath first search was not working properly, and since we were sharing the same map and
# making the node when the ether AI went over it so the other would not, the AIs were getting 
# stuck and unable to move.  After this, we decided that each AI was going to use the same
# depth-first search algorithm, but the aiA move set was to go East and South as the first two 
# move options, and aiB would go West and North as its first two move options. We also made it
# so that they would only be restricted by nodes that each AI had already visited. This made it so
# that the ai’s were not getting stuck and not able to move, making them so that they could
# explore the map.  At this point in the implementation, we made it so that if an AI found the goal,
# it would exit and then, in the message, send the x,y Coordinates of the exit to the other AI so 
# that it could use the A* to find it’s way back.  But it was only working if the the AI using the 
# A* search had not goten throught a teleporter before using the A* becuse we did not have the nodes
# linked correctly.  So I wanted to try and keep the AI in he enviorment for a longer time before they
# exited so I disabled the teleportation on the ais and started to make it so the if the AI found the exit
# that it would mark it and save the exit coordinats and then it would keep searching, then I would keep track
# of the turns and the max turn, I then compared them and subtracted 100 from turn. 
# So when self.turn - 100 >= self.max_turn then I would use the A* on both agents and and they would both use that to get
# out the the enviorment.  They was working and we were going to start imlimenting teleportation but I waned to
# increase the number of moves in this comparison (self.turn - 100 >= self.max_turn) from 100 to 150 so that if 
# the map was differnt then it could get out.  But then I started to run into issues of the A* function were the
# ai that found the goal the A* founction could not find a path back.  So we tryed to fix the A* and were still 
# running into isses so we implemented a we tryed to implement dijkstra's algorithm to replace our A* but we were still
# having problems.  After this we took a few steps back becuse we were running out of ideas to make this work.
# So we went back the when an AI finds the exit to just exit and then for the other ai to call the A* to find it;s way back.
# We did this becuse the only time that the A* was haing isssues was with the AIs when they found the goal before exiting.
# After that we tried to go back and implemt the teleperters we first started with trying to link them to we kind of go this
# to work but were having a hard tiime maping the maps together if they saw the same Teleporter agein. So then we tryed to 
# make it so that it would only last up to 50 turn before the ai went back to the Teleporter that it came throught but we could 
# not figure out how to ge the back tracking to work proporly.  I tyried storing the mives to the tepelorter in an array and makeing 
# sure to swap the direction so if it when to the East is would Store West and then when it got to 50 moves then it would flip the array
# to make sure that we were poping the move to go back to the last position but we could just not get it to work proporly with our code.
# So after we did this we reverted our code back again to were it was working the last time but now it aiB dose not use tp unless
# the exit is in a TP and aiA and use the teleporters but is dose not have an escapse if it get stuck.
#
#
# So for our final implemtntation (If It was woking proporly):
#
# How are our AI similar:  They Are both using the same searching algorithem (Depth first search to move around the map).
# They are also using the same goal based moving system were if they see ether a objective or the exit they will move tordes it.
# They are also using the same Node structer. This Alows them to using the same map so that if one finds the goal the other can use
# that information that the other ai found to find it's way back.
#
# How are the AI's Differnt:  The way that the AI differ is that first both of the AI's use diffet movment patterns.
# aiA's defult movement pattern is to go East first then go South then West and lastly North.
# aiB'S defult movment pattern is the oposet it will go West first then it will go North then East and lastly South.
# The other differnce is that AI_ dose not use teleporters when exploring and will only use them if the goal is thought a Teleporter.
# By doing this it make is to the aiB will primarly start searching on the top and left side of the map and aiA will search on the
# Right and towrds the bottom of the map.  By doing this they will cover the most amount of ground in the least amount of moves.
#
#
# aiA Approch: 
# This AI first uses a depth first search to explore the map. 
# The ai will prioritize going  East first then South, then West and lastly North.
# This will make it so that the ai will primaraly search the right and bottom of the map.
# aiA will always send 2 things to aiB the updated map after its move and also ether None or the exit coordinates if it fould the exit.
# aiA will also be able to use the teleporters to explore the map. 
# It also has a goal based approch were it will move tords the objectivs and the exit if it sees it.
# If aiA is on the exit it will then exit the map.
# If aiB finds the exit then it will use the A* method to find its way to the goal if in the 'main' map
# if it is in a teleporter map it will backtrack back to the teleporter then use A* to find it's way to the goal.
#
#
#
#

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
        self.atExit = False
        self.last_teleporter = None
        self.teleporter_cooldown = 0
        self.hasAStarRunYet = False
        self.AStarPath = None
        self.AStarCount = 0
        self.max_turn = max_turns if max_turns else 800

    def update(self, percepts, msg):
        self.turn += 1

        # Receive data from Agent B
        if msg:
            self.goalCoords = msg[0] if msg[0] else self.goalCoords
            self.map = msg[1] if msg[1] else self.map

        self.update_graph(percepts)

        # Detect exit or goal in the current cell
        if percepts['X'][0] == 'r':  # Exit cell
            self.goalCoords = (self.xCoord, self.yCoord)
            self.goalMap = self.currentNode.whatMap
            self.atExit = True
            if not self.hasAStarRunYet:
                self.AStarPath = self.AStar_search(self.currentNode)
                self.hasAStarRunYet = True
                self.AStarCount = len(self.AStarPath) - 1  # Initialize AStarCount to the last index
            return 'U', [self.goalCoords, self.map, self.AStarPath]  # Share path with Agent B
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

        # If at exit, remain here and send data to Agent B
        if self.atExit:
            return None, [self.goalCoords, self.map, self.AStarPath]

        # Teleporter handling with cooldown
        if percepts['X'][0] in 'obyp' and self.teleporter_cooldown == 0:
            self.last_teleporter = percepts['X'][0]
            self.teleporter_cooldown = 3  # Activate cooldown
            # Teleport to corresponding paired location
            if self.currentNode.whatMap == 'main':
                self.xCoord, self.yCoord, self.currentNode.whatMap = 0, 0, percepts['X'][0]
            else:
                self.currentNode.whatMap = 'main'
            return 'U', [self.goalCoords, self.map, self.AStarPath]  # Teleport and update Agent B

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
                
                # Ensure AStarCount is within bounds before accessing AStarPath
                if self.AStarPath and 0 <= self.AStarCount < len(self.AStarPath):
                    move_cmd = self.AStarPath[self.AStarCount]
                    self.AStarCount -= 1
                    return move_cmd, [self.goalCoords, self.map, self.AStarPath]
                else:
                    return self.explore_or_backtrack(), [self.goalCoords, self.map]

        # Explore or backtrack if the goal or exit is unknown
        return self.explore_or_backtrack(), [self.goalCoords, self.map]

    def explore_or_backtrack(self):
        for direction in ['E', 'S', 'W', 'N']:
            next_node = self.get_neighbor_node(direction)
            if next_node and not next_node.Avisited:
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
        self.northNode = self.southNode = self.eastNode = self.westNode = self.teleportNode = None
        self.f_score = float('inf')
        self.g_score = float('inf')
        self.aiAAStarVisited = self.aiBAStarVisited = False
    
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