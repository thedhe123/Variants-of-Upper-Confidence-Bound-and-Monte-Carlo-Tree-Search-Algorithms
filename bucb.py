import random
import math
from array import *
from copy import deepcopy
import numpy as np

graphs = []

class bucb:
    
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
        
        self.actions = []
        self.optimalActions = []
                        
    def opponentAction(pawns, kings, epawns, ekings):
        
        flipState = checkers.flip(pawns, kings, epawns, ekings)
        flipState.updateAll()
        return(random.choice(flipState.optimalActions))
    
    # todo: Move tuplefy out of ucb
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

        if self.checkers.win == 1:
            return(1)
                
        position = deepcopy(self.checkers)
        position.updateBoard(move)

        opponentMove = bucb.opponentAction(position.pawns, position.kings, position.epawns, position.ekings)

        opponentBoard = checkers.flip(position.pawns, position.kings, position.epawns, position.ekings)
        opponentBoard.updateBoard(opponentMove)
        subposition = checkers.flip(opponentBoard.pawns, opponentBoard.kings, opponentBoard.epawns, opponentBoard.ekings)
        subposition.updateAll()

        if depth > 1:
                    
            if bucb.tuplefy(move) in self.children:
                
                childState = self.children[bucb.tuplefy(move)]
                childState.position = subposition.position
                childState.checkers = checkers(position = childState.position)
                childState.checkers.updateAll()
            
            else:
            
                childState = bucb(position = subposition.position, explore_param = self.explore_param, depth = self.depth-1)
                self.children[bucb.tuplefy(move)] = childState
            
            self.total_visits += 1
            
            childMove = childState.starvingAction()
            
            qval = childState.update(childMove, depth - 1)
            
            if bucb.tuplefy(move)in self.UCBVals:
                self.qBar[bucb.tuplefy(move)] = (self.qBar[bucb.tuplefy(move)] * self.num_visits[bucb.tuplefy(move)] + qval)/(self.num_visits[bucb.tuplefy(move)]+1)
                self.num_visits[bucb.tuplefy(move)] += 1
                for move in self.UCBVals:
                    self.UCBVals[move] = self.qBar[bucb.tuplefy(move)] + self.explore_param * math.sqrt(math.log(self.total_visits)/self.num_visits[move])
                
            else:
                self.qBar[bucb.tuplefy(move)] = qval
                self.num_visits[bucb.tuplefy(move)] = 1
                self.UCBVals[bucb.tuplefy(move)] = self.qBar[bucb.tuplefy(move)] + self.explore_param * math.sqrt(math.log(self.total_visits))

            for i in self.qBar:
                if self.qBar[i] > self.qHat:
                    self.qHat = self.qBar[i]

            return(self.qHat)
        
        else:
            
            return(bucb.rollout(subposition))
            
    def rollout(position):
        
        board = checkers(position)
        
        for iter in range(30):
                
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
        return((len(board.pawns) + 1.5 * len(board.kings))/(len(board.pawns) + len(board.epawns) + 1.5 * len(board.kings) + 1.5 * len(board.ekings)))
    
    def starvingAction(self):
        
        maxUCB = 0
        maxAction = []
        
        for action in self.actions:
            
            if not (bucb.tuplefy(action) in self.children):
                
                return(action)

            if self.UCBVals[bucb.tuplefy(action)] > maxUCB:
                
                maxUCB = self.UCBVals[bucb.tuplefy(action)] 
                maxAction = action
        
        return(maxAction)
    
    def simulate(self, iter, p):
        
        self.actions = self.checkers.optimalActions
        
        if self.checkers.win == 1:
            
            return(self.checkers.optimalActions[0])
        
        for val in range(math.floor(iter/2)):

            self.update(self.starvingAction(), self.depth)
        
        actions = []

        if self.checkers.win == 1:
            
            return(self.checkers.optimalActions[0])

        for move in sorted(self.UCBVals)[len(self.actions) - math.floor(len(self.actions) * p):]:
            actions.append(bucb.untuplefy(move))
        
        self.actions = actions
        
        for val in range(iter - math.floor(iter/2)):
            
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
                
                temp.append(bucb.traverse(self.children[child]))

        return(temp)