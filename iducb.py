import random
import math
from array import *
from copy import deepcopy
import numpy as np

graphs = []

class iducb:
    
    def __init__(self, position = [1] * 12 + [0] * 8 + [-1] * 12, explore_param = math.sqrt(2), maxdepth = 5, mindepth = 2, setdepth = False, depth = 0):
        
        self.checkers = checkers(position = position)
        self.checkers.updateAll()
        
        self.children = {}
        
        self.position = []
        self.explore_param = explore_param
        
        self.total_visits = 0
        self.num_visits = {}

        self.maxdepth = maxdepth
        self.mindepth = mindepth
        self.setdepth = setdepth
        self.depth = depth
        self.totaldepth = 0

        self.UCBVals = {}
        self.qBar = {}
        self.qHat = 0
        
        self.vHat = []
        self.optimalActions = []
                       
    def opponentAction(pawns, kings, epawns, ekings):
        
        flipState = checkers.flip(pawns, kings, epawns, ekings)
        flipState.updateAll()
        # print(flipState.optimalActions)
        return(random.choice(flipState.optimalActions))

    def tuplefy(move):
        
        newmove = []
        
        for step in move:
            
            newmove.append(tuple(step))
            
            if step == [""]:
                break
            
        return(tuple(newmove))
    
    def untuplefy(move):

        flag = True
        newmove = []
        
        for step in move:
            
            if list(step) == [""]:
                break
            
            newmove.append(list(step))
            
        newmove.append([""])
        
        return(newmove)
    
    def update(self, move, depth):
        
        """
        if isinstance(move[0], int):
            move = [move]    
           """
            
        if self.checkers.win == 1:
            return(1)
                
        position = deepcopy(self.checkers)
        position.updateBoard(move)

        opponentMove = iducb.opponentAction(position.pawns, position.kings, position.epawns, position.ekings)
        opponentBoard = checkers.flip(position.pawns, position.kings, position.epawns, position.ekings)
        opponentBoard.updateBoard(opponentMove)
        subposition = checkers.flip(opponentBoard.pawns, opponentBoard.kings, opponentBoard.epawns, opponentBoard.ekings)
        subposition.updateAll()

        if not self.setdepth:

            if not(iducb.tuplefy(move) in self.children):

                depth = self.maxdepth

            else:

                maxqBar = 0
                minqBar = 10

                for val in self.qBar:

                    if self.qBar[val] > maxqBar:
                        maxqBar = self.qBar[val]
                    if self.qBar[val] < minqBar:
                        minqBar = self.qBar[val]
                
                if self.qBar[iducb.tuplefy(move)] == maxqBar:

                    depth = self.maxdepth
                
                elif self.qBar[iducb.tuplefy(move)] == minqBar:

                    depth = self.mindepth
                
                else:

                    depth = round(np.random.beta((self.qBar[iducb.tuplefy(move)] - minqBar)/(maxqBar-self.qBar[iducb.tuplefy(move)]), 1) * (self.maxdepth - self.mindepth) + self.mindepth)
    
                self.totaldepth += depth

        if depth > 1:
            
            #print("blah")
                
            if iducb.tuplefy(move) in self.children:
                
                childState = self.children[iducb.tuplefy(move)]
                childState.position = subposition.position
                childState.checkers = checkers(position = childState.position)
                childState.checkers.updateAll()
            
            else:
            
                childState = iducb(position = subposition.position, explore_param = self.explore_param, setdepth = True, depth = depth-1)
                self.children[iducb.tuplefy(move)] = childState
            
            self.total_visits += 1
            
            childMove = childState.starvingAction()
            """
            if isinstance(childMove[0], int):
                childMove = [childMove]
            """
             
            qval = childState.update(childMove, depth - 1)
            
            if iducb.tuplefy(move) in self.UCBVals:
                self.qBar[iducb.tuplefy(move)] = (self.qBar[iducb.tuplefy(move)] * self.num_visits[iducb.tuplefy(move)] + qval)/(self.num_visits[iducb.tuplefy(move)]+1)
                self.num_visits[iducb.tuplefy(move)] += 1
                # self.UCBVals[ucb.tuplefy(move)] = self.qBar[ucb.tuplefy(move)] + self.explore_param * math.sqrt(math.log(self.total_visits))
                for move in self.UCBVals:
                    self.UCBVals[move] = self.qBar[iducb.tuplefy(move)] + self.explore_param * math.sqrt(math.log(self.total_visits)/self.num_visits[move])
                    # print(move)
                
            else:
                self.qBar[iducb.tuplefy(move)] = qval
                self.num_visits[iducb.tuplefy(move)] = 1
                # self.UCBVals[ucb.tuplefy(move)] = self.qBar[ucb.tuplefy(move)] + self.explore_param * math.sqrt(math.log(self.total_visits))
                self.UCBVals[iducb.tuplefy(move)] = self.qBar[iducb.tuplefy(move)] + self.explore_param * math.sqrt(math.log(self.total_visits)/self.num_visits[iducb.tuplefy(move)])
                
            for i in self.qBar:
                if self.qBar[i] > self.qHat:
                    self.qHat = self.qBar[i]
                    
            return(self.qHat)
        
        else:
            
            return(iducb.rollout(subposition))
            
    def rollout(position):
        
        board = checkers(position)
        
        for iter in range(40):
                
            board.updateAll()
            if board.win == 1:
                return(1)
    
            board.updateBoard(random.choice(board.optimalActions))
            board = checkers.flip(board.pawns, board.kings, board.epawns, board.ekings)
            board.updateAll()
            if board.win == 1:
                return(-1)    
            board.updateBoard(random.choice(board.optimalActions))
            board = checkers.flip(board.pawns, board.kings, board.epawns, board.ekings)
        
        board.updateLocation()
        # print(board.pawns, board.kings, board.epawns, board.ekings)
        return((len(board.pawns) + 1.5 * len(board.kings))/(len(board.pawns) + len(board.epawns) + 1.5 * len(board.kings) + 1.5 * len(board.ekings)))
    
    def starvingAction(self):
        
        maxUCB = 0
        maxAction = []
        
        for action in self.checkers.optimalActions:
                        
            if not (iducb.tuplefy(action) in self.children):
                
                return(action)

            if self.UCBVals[iducb.tuplefy(action)] > maxUCB:
                
                maxUCB = self.UCBVals[iducb.tuplefy(action)] 
                maxAction = action
        
        return(maxAction)
    
    def simulate(self):
        
        # print()
        # print(self.checkers.optimalActions)
        # print()
               
        if self.checkers.win == 1:
            
            return(self.checkers.optimalActions[0])
        
        for val in range(25):
            
            self.update(self.starvingAction(), self.depth)

        optscore = 0
        optmove = 0
        for i in self.qBar:
            if self.qBar[i] > optscore:
                optscore = self.qBar[i]
                optmove = i

        return(optmove)
            
    def traverse(self):

        temp = []
        temp.append(self.total_visits)
        
        if len(self.children) > 0:

            for child in self.children:
                
                temp.append(iducb.traverse(self.children[child]))
        print(temp)
        return(temp)