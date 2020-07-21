import sys

# Setup pygame
import pygame
import pygame.locals
pygame.init()
pygame.font.init()

# Setup logging
import logging
logger = logging.getLogger(__file__)
import LoggerSettings

# Local Imports
from Board import Board
from DisplayInfo import DisplayInfo


class ScoreKeeper:
    def __init__(self):
        self.scores = {1: 0, -1:0}


    def recordP1Win(self):
        self.scores[1] += 1


    def recordP2Win(self):
        self.scores[-1] += 1


    def getP1Score(self):
        return self.scores[1]


    def getP2Score(self):
        return self.scores[-1]


class Game:
    '''
    Handles Game Logic
    '''
    def __init__(self, display, board):
        self.startingBeads = 17
        self.scores = ScoreKeeper()

        self.board = board
        self.display = display

        self.p1Turn = False # Will be set to true by processNewState call
        self.isFinished = False

        self.inRemoval = False
        self.stagedForRemoval = None

        # Used to remove beads when board is full
        self.inClearance = False
        self.clearanceCount = 0

        self.processNewState()


    def reset(self):
        logging.info("Resetting game state")
        self.board.reset()
        self.isFinished = False

        # Reset removal variables
        self.inRemoval = False
        self.stagedForRemoval = None

        # Reset clearance variables
        self.inClearance = False
        self.clearanceCount = 0
        self.processNewState()


    ### State management functions

    def isP1Turn(self):
        return self.p1Turn


    def isP2Turn(self):
        return not self.p1Turn


    def getP1NBeads(self):
        return self.startingBeads - self.board.countP1Beads()


    def getP2NBeads(self):
        return self.startingBeads - self.board.countP2Beads()


    def setStateClearance(self):
        logging.info("Entering clearance state")
        assert(not self.inRemoval)
        self.clearanceCount = 6
        self.inClearance = True


    def unsetStateClearance(self):
        logging.info("Leaving clearance state")
        assert(self.inClearance)
        assert(self.clearanceCount == 0)
        self.inClearance = False


    def setStateRemoval(self, coor):
        '''
        Stage a bead for removal and update state
        '''
        logging.info("Entering removal state")
        assert(not self.inClearance)
        self.board.setHighlight(coor)
        self.stagedForRemoval = coor
        self.inRemoval = True


    def unsetStateRemoval(self):
        logging.info("Leaving removal state")
        assert(self.inRemoval)
        self.board.unsetHighlight()
        self.stagedForRemoval = None
        self.inRemoval = False


    def isStateRegular(self):
        return not (self.inClearance or self.inRemoval)


    def isStateClearance(self):
        return self.inClearance


    def isStateRemoval(self):
        return self.inRemoval


    ### State update functions

    def updateTurn(self):
        '''
        Alternates the players' turns each call
        '''
        self.p1Turn = not self.p1Turn


    def updateDisplay(self):
        '''
        Updates the display to match the current game state
        '''
        # Update display
        self.display.setTopText("Active Player: {}".format("Red" if self.isP1Turn() else "Blue"))
        self.display.setP1BeadsRemaining(self.getP1NBeads())
        self.display.setP2BeadsRemaining(self.getP2NBeads())
        self.display.setP1Score(self.scores.getP1Score())
        self.display.setP2Score(self.scores.getP2Score())
        # Set bottom text
        if (self.isFinished):
            self.display.setTopText("{} Wins!".format("Red" if self.isP1Turn() else "Blue"))
            self.display.setBottomText("Press Space to replay!")
        elif (self.inClearance):
            self.display.setBottomText(f"Clearance! Removals remaining: {self.clearanceCount}")
        else:
            self.display.eraseBottomText()


    def processNewState(self):
        '''
        Updates the game state based on the state of the board
        '''
        logging.info("Processing game state")
        if (self.board.isVictory()):
            self.isFinished = True
            if self.isP1Turn():
                logging.info("Player 1 wins!")
                self.scores.recordP1Win()
            else:
                logging.info("Player 2 wins!")
                self.scores.recordP2Win()
        else:
            if (self.board.isFull()):
                self.setStateClearance()
            elif (self.isStateClearance() and self.clearanceCount == 0):
                self.unsetStateClearance()
            self.updateTurn()

        # Update display to represent new state
        self.updateDisplay()


    def processClick(self, pos, surface):
        '''
        Processes user input from the mouse
        '''
        if (not self.isFinished):
            if (self.board.isOnGrid(pos)):
                coor = self.board.getCoor(pos)
                logging.info("Click signal received on grid: coordinate ({} {})".format(*coor))
                self.processClickOnBoard(coor)
            else:
                logging.info("Click signal received: position ({} {})".format(*pos))
                self.processClickOutsideBoard(pos, surface)


    def processClickOnBoard(self, coor):
        '''
        Process a mouse click on the board based on the postion and game state.
        '''
        if (self.isStateClearance()):
            self.runClearance(coor)
        else:
            if (self.isStateRemoval()):
                if (coor  == self.stagedForRemoval):
                    # If clicked space is already staged, needs to be unstaged
                    self.unsetStateRemoval()
                elif (self.board.areP1AndP2(coor, self.stagedForRemoval)):
                    # If clicked space is controlled by a different player, remove both
                    self.board.setEmpty(coor)
                    self.board.setEmpty(self.stagedForRemoval)
                    self.unsetStateRemoval()
                    self.processNewState()
            elif (self.board.isSpaceEmpty(coor)):
                # If space is empty, check if move is legal and add a bead if so
                if (self.isP1Turn() and not self.board.isSpaceSurroundedByP2(coor) and self.getP1NBeads() > 0):
                    self.board.setP1(coor)
                    self.processNewState()
                elif (self.isP2Turn() and not self.board.isSpaceSurroundedByP1(coor) and self.getP2NBeads() > 0):
                    self.board.setP2(coor)
                    self.processNewState()
            else:
                # If space isn't empty and state isn't removal,
                #   stage clicked bead for removal
                self.setStateRemoval(coor)


    def runClearance(self, coor):
        '''
        Process clearance. Can only remove own beads.
        '''
        if ((self.isP1Turn() and self.board.isP1(coor)) or (self.isP2Turn() and self.board.isP2(coor))):
            self.board.setEmpty(coor)
            self.clearanceCount -= 1
            assert(self.clearanceCount > -1)
            self.processNewState()


    def processClickOutsideBoard(self, pos, surface):
        xMax, yMax = surface.get_size()
        # Convert coordinates to be relative to centre. Top right is (+, +)
        xRel, yRel = pos[0] - xMax/float(2), yMax/float(2) - pos[1]
        # Detect clicks in four zones around the board
        if (xRel > 0 and abs(xRel) > abs(yRel)):
            logging.info("Attempting move Right")
            if (self.board.canShiftRight()):
                logging.info("Shift right possible")
                self.board.shiftRight()
        if (xRel < 0 and abs(xRel) > abs(yRel)):
            logging.info("Attempting move Left")
            if (self.board.canShiftLeft()):
                logging.info("Shift left possible")
                self.board.shiftLeft()
        if (yRel > 0 and abs(yRel) > abs(xRel)):
            logging.info("Attempting move Up")
            if (self.board.canShiftUp()):
                logging.info("Shift up possible")
                self.board.shiftUp()
        if (yRel < 0 and abs(yRel) > abs(xRel)):
            logging.info("Attempting move Down")
            if (self.board.canShiftDown()):
                logging.info("Shift down possible")
                self.board.shiftDown()


    def processKey(self, key):
        if (key == pygame.K_SPACE and self.isFinished):
            self.reset()
