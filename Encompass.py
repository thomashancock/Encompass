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
from Input import Input
from Actions import *
from Board import Board
from DisplayInfo import DisplayInfo
import Colours as colour


class Game:
    '''
    Handles Game Logic
    '''
    def __init__(self, display, board):
        self.startingBeads = 17

        # Store a pointer to the board
        self.board = board
        self.display = display
        self.p1Turn = False # Will be set to true by updateState call

        self.isFinished = False

        self.inRemoval = False
        self.stagedForRemoval = None

        # Used to remove beads when board is full
        self.inClearance = False
        self.clearance = 0

        self.updateState()


    def reset(self):
        logging.info("Resetting game state")


    def isP1Turn(self):
        return self.p1Turn


    def isP2Turn(self):
        return not self.p1Turn


    def getP1NBeads(self):
        return self.startingBeads - self.board.countP1Beads()


    def getP2NBeads(self):
        return self.startingBeads - self.board.countP2Beads()


    def updateTurn(self):
        self.p1Turn = not self.p1Turn


    def updateDisplay(self):
        # Update display
        self.display.setTopText("Active Player: {}".format("Red" if self.isP1Turn() else "Blue"))
        self.display.setP1BeadsRemaining(self.getP1NBeads())
        self.display.setP2BeadsRemaining(self.getP2NBeads())
        if (self.isFinished):
            self.display.setTopText("{} Wins!".format("Red" if self.isP1Turn() else "Blue"))
            self.display.setBottomText("Game ended.")
        elif (self.inClearance):
            self.display.setBottomText("In clearance. Beads can only be removed.")
        else:
            self.display.eraseBottomText()


    def updateState(self):
        logging.info("Updating game state")
        if (self.board.isVictory()):
            self.isFinished = True
        elif (self.board.isFull()):
            logging.info("Board full. Entering clearance mode")
            self.clearance = 6
            self.inClearance = True
            self.updateTurn()
        elif (self.inClearance and self.clearance == 0):
            logging.info("End of clearance mode")
            self.inClearance = False
            self.updateTurn()
        else:
            self.updateTurn()

        self.updateDisplay()


    def processClick(self, pos):
        if (self.board.isOnGrid(pos) and not self.isFinished):
            coor = self.board.getCoor(pos)
            logging.info("Click signal received on grid: coordinate ({} {})".format(*coor))

            if (self.clearance == 0):
                if (self.inRemoval):
                    if (coor  == self.stagedForRemoval):
                        self.board.unsetHighlight()
                        self.stagedForRemoval = None
                        self.inRemoval = False
                    elif (self.board.areP1AndP2(coor, self.stagedForRemoval)):
                        self.board.setEmpty(coor)
                        self.board.setEmpty(self.stagedForRemoval)

                        self.board.unsetHighlight()
                        self.stagedForRemoval = None
                        self.inRemoval = False

                        self.updateState()
                elif (self.board.isSpaceEmpty(coor)):
                    if (self.isP1Turn() and not self.board.isSpaceSurroundedByP2(coor) and self.getP1NBeads() > 0):
                        self.board.setP1(coor)
                        self.updateState()
                    elif (self.isP2Turn() and not self.board.isSpaceSurroundedByP1(coor) and self.getP2NBeads() > 0):
                        self.board.setP2(coor)
                        self.updateState()
                else:
                    self.board.setHighlight(coor)
                    self.inRemoval = True
                    self.stagedForRemoval = coor

            else:
                # Process clearance. Can only remove own beads
                if ((self.isP1Turn() and self.board.isP1(coor)) or (self.isP2Turn() and self.board.isP2(coor))):
                    self.board.setEmpty(coor)
                    self.clearance -= 1
                    assert(self.clearance > -1)
                    self.updateState()


        else:
            logging.info("Click signal received: position ({} {})".format(*pos))


    def processKey(self, key):
        if (key == pygame.K_SPACE and self.isFinished):
            self.reset()


class World:
    '''
    World class
    Manages and runs the simulation
    '''
    def __init__(self, width, height):
        self.surface = pygame.display.set_mode((width, height))

        self.clock = pygame.time.Clock()

        self.input = Input()

        self.display = DisplayInfo()
        self.board = Board(self.surface)
        self.game = Game(self.display, self.board)


    def _processAction(self, action):
        if action.getActionType() == "QUIT":
            pygame.quit()
            sys.exit()
        elif action.getActionType() == "MOUSEBUTTONUP":
            self.game.processClick(action.getPos())
        elif action.getActionType() == "KEYUP":
            self.game.processKey(action.getKey())


    def run(self):
        '''
        Runs the game
        '''
        while True:
            # Process user inputs
            actionQueue = []
            assert(len(actionQueue) == 0)
            self.input.parseInputs(actionQueue)

            for action in actionQueue:
                self._processAction(action)

            # Draw objects
            self.surface.fill(colour.WHITE)
            self.display.draw(self.surface)
            self.board.draw(self.surface)

            # Update display
            pygame.display.flip()

            self.clock.tick(60)


def main():
    '''
    Main function
    '''

    pygame.display.set_caption("Encompass")

    # Define world object
    world = World(720, 720)

    # Run world
    world.run()


if __name__ == "__main__":
    main();
