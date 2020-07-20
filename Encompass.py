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


    def _processAction(self, action):
        if action.getActionType() == "MOUSEBUTTONUP":
            self.board.processClick(action.getPos())


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
