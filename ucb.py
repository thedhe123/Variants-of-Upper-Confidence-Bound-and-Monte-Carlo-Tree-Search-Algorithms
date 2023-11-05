import random
import math
from array import *
from copy import deepcopy
import numpy as np

graphs = []

class ucb:
    
    def __init__(self, position = [1] * 12 + [0] * 8 + [-1] * 12, explore_param = math.sqrt(2), depth = 5):
        
        self.checkers = checkers(position = position)
        self.checkers.updateAll()
        
        self.children = {}
        
        self.position = []
        self.explore_param = explore_param
        
        self.total_visits = 0
        self.num_visits = {}
        self.depth = depth
        
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

        opponentMove = ucb.opponentAction(position.pawns, position.kings, position.epawns, position.ekings)
        opponentBoard = checkers.flip(position.pawns, position.kings, position.epawns, position.ekings)
        opponentBoard.updateBoard(opponentMove)
        subposition = checkers.flip(opponentBoard.pawns, opponentBoard.kings, opponentBoard.epawns, opponentBoard.ekings)
        subposition.updateAll()

        if depth > 1:
            
            #print("blah")
                
            if ucb.tuplefy(move) in self.children:
                
                childState = self.children[ucb.tuplefy(move)]
                childState.position = subposition.position
                childState.checkers = checkers(position = childState.position)
                childState.checkers.updateAll()
            
            else:
            
                childState = ucb(position = subposition.position, explore_param = self.explore_param, depth = self.depth-1)
                self.children[ucb.tuplefy(move)] = childState
            
            self.total_visits += 1
            
            childMove = childState.starvingAction()
            """
            if isinstance(childMove[0], int):
                childMove = [childMove]
            """
             
            qval = childState.update(childMove, depth - 1)
            
            if ucb.tuplefy(move) in self.UCBVals:
                self.qBar[ucb.tuplefy(move)] = (self.qBar[ucb.tuplefy(move)] * self.num_visits[ucb.tuplefy(move)] + qval)/(self.num_visits[ucb.tuplefy(move)]+1)
                self.num_visits[ucb.tuplefy(move)] += 1
                # self.UCBVals[ucb.tuplefy(move)] = self.qBar[ucb.tuplefy(move)] + self.explore_param * math.sqrt(math.log(self.total_visits))
                for move in self.UCBVals:
                    self.UCBVals[move] = self.qBar[ucb.tuplefy(move)] + self.explore_param * math.sqrt(math.log(self.total_visits)/self.num_visits[move])
                    # print(move)
                
            else:
                self.qBar[ucb.tuplefy(move)] = qval
                self.num_visits[ucb.tuplefy(move)] = 1
                # self.UCBVals[ucb.tuplefy(move)] = self.qBar[ucb.tuplefy(move)] + self.explore_param * math.sqrt(math.log(self.total_visits))
                self.UCBVals[ucb.tuplefy(move)] = self.qBar[ucb.tuplefy(move)] + self.explore_param * math.sqrt(math.log(self.total_visits)/self.num_visits[ucb.tuplefy(move)])
                
            for i in self.qBar:
                if self.qBar[i] > self.qHat:
                    self.qHat = self.qBar[i]
                    
            return(self.qHat)
        
        else:
            
            return(ucb.rollout(subposition))
            
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
                        
            if not (ucb.tuplefy(action) in self.children):
                
                return(action)

            if self.UCBVals[ucb.tuplefy(action)] > maxUCB:
                
                maxUCB = self.UCBVals[ucb.tuplefy(action)] 
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
                
                temp.append(ucb.traverse(self.children[child]))
        print(temp)
        return(temp)