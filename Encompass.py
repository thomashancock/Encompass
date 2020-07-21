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
from Game import Game
from Board import Board
from DisplayInfo import DisplayInfo
import Colours as colour


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
            self.game.processClick(action.getPos(), self.surface)
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
