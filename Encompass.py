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
from Actions import *
from Board import Board


class Input:
    def __init__(self):
        pass


    def parseInputs(self, actionQueue):
        for event in pygame.event.get():
            # Detect Quit Action
            if event.type == pygame.locals.QUIT:
                pygame.quit()
                sys.exit()

            elif event.type == pygame.MOUSEBUTTONUP:
                pos = pygame.mouse.get_pos()
                actionQueue.append(ActionMouseClick(pos))


class Game:
    '''
    Handles Game Logic
    '''
    def __init__(self, board):
        # Store a pointer to the board
        self.board = board
        self.p1Turn = True

        self.inRemoval = False
        self.stagedForRemoval = None

        # Used to remove beads when board is full
        self.inClearance = False
        self.clearance = 0


    def isP1Turn(self):
        return self.p1Turn


    def isP2Turn(self):
        return not self.p1Turn


    def updateTurn(self):
        self.p1Turn = not self.p1Turn


    def updateState(self):
        logging.info("Updating game state")
        if (self.board.isVictory()):
            logging.info("Player {} wins!".format("1" if self.isP1Turn() else "2"))
        elif (self.board.isFull()):
            logging.info("Board full. Entering clearance mode")
            self.clearance = 6
            self.inClearance = True
        elif (self.inClearance and self.clearance == 0):
            logging.info("End of clearance mode")

        self.updateTurn()


    def processClick(self, pos):
        if (self.board.isOnGrid(pos)):
            coor = self.board.getCoor(pos)
            logging.info("Click signal received on grid: coordinate ({} {})".format(*coor))

            if (self.clearance == 0):
                if (self.board.isSpaceEmpty(coor)):
                    if (self.isP1Turn() and not self.board.isSpaceSurroundedByP2(coor)):
                        self.board.setP1(coor)
                        self.updateState()
                    elif (self.isP2Turn() and not self.board.isSpaceSurroundedByP1(coor)):
                        self.board.setP2(coor)
                        self.updateState()
                else:
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


class World:
    '''
    World class
    Manages and runs the simulation
    '''
    def __init__(self, width, height):
        self.surface = pygame.display.set_mode((width, height))

        self.clock = pygame.time.Clock()

        self.input = Input()

        self.board = Board(self.surface)
        self.game = Game(self.board)


    def _processAction(self, action):
        if action.getActionType() == "MOUSEBUTTONUP":
            self.game.processClick(action.getPos())


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
