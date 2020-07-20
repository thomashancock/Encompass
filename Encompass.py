import sys
import itertools

# Setup logging
import logging

if __debug__:
    logging.basicConfig(
        format='%(asctime)s %(levelname)-8s %(message)s',
        level=logging.DEBUG,
        datefmt='%Y-%m-%d %H:%M:%S')
else:
    logging.basicConfig(
        format='%(asctime)s %(levelname)-8s %(message)s',
        level=logging.INFO,
        datefmt='%Y-%m-%d %H:%M:%S')

# Setup pygame
import pygame
import pygame.locals
pygame.init()
pygame.font.init()

fontComicSans = pygame.font.SysFont('Comic Sans MS', 30)

# Define colors
WHITE = (255,255,255)
GREY = (128,128,128)
BLACK = (0,0,0)
RED = (255,0,0)
BLUE = (0,0,255)


class Space:
    '''
    Records the status of a single space. Can be empty, P1 or P2
    '''
    def __init__(self):
        self.state="P1"
        # self.state="empty"


    def __repr__(self):
        return '{space state:{0}}'.format(self.state)


    def __str__(self):
        if not self._validateState():
            return f"Error.Invalid state: {self.state}"
        if self.state == "empty":
            return 0
        if self.state == "P1":
            return 1
        if self.state == "P2":
            return 2


    def _validateState():
        return (self.state in ["empty", "p1", "p2"])


    def setEmpty(self):
        self.state = "empty"


    def setP1(self):
        self.state = "P1"


    def setP2(self):
        self.state = "P2"


    def isEmpty(self):
        return self.state == "empty"


    def isP1(self):
        return self.state == "P1"


    def isP2(self):
        return self.state == "P2"


class Board:
    def __init__(self):
        self.size = 5
        self.array = [[Space() for _ in range(self.size)] for _ in range(self.size)]


    def getSpace(self, xCoor, yCoor):
        return self.array[xCoor][yCoor]


    def _getSpaceCoor(self, spaceCoor, surface):
        x, y = spaceCoor
        assert(x > -1)
        assert(x < self.size)
        assert(y > -1)
        assert(y < self.size)

        def getAlongAxis(n, max):
            return (1.5 + n)*max/float(7)

        xMax, yMax = surface.get_size()
        return int(getAlongAxis(x, xMax)), int(getAlongAxis(y, yMax))


    def draw(self, surface):
        xMax, yMax = surface.get_size()

        # Draw 5x5 grid
        for i in range(2,6):
            # Horizontal lines
            pygame.draw.line(surface, GREY, (i*xMax/float(7), 1*yMax/float(7)), (i*xMax/float(7), 6*yMax/float(7)))

            # Vertical lines
            pygame.draw.line(surface, GREY, (1*xMax/float(7), i*yMax/float(7)), (6*xMax/float(7), i*yMax/float(7)))

        # Draw beads
        for x, y in itertools.product(range(self.size), range(self.size)):
            if (self.getSpace(x,y).isP1()):
                pygame.draw.circle(surface, RED, self._getSpaceCoor((x,y), surface), int(xMax/float(20)))


class Input:
    def __init__(self):
        pass

    def parseInputs(self):
        for event in pygame.event.get():
            # Detect Quit Action
            if event.type == pygame.locals.QUIT:
                pygame.quit()
                sys.exit()


class World:
    '''
    World class
    Manages and runs the simulation
    '''
    def __init__(self, width, height):
        self.surface = pygame.display.set_mode((width, height))

        self.clock = pygame.time.Clock()

        self.input = Input()

        self.entities = [Board()]


    def run(self):
        '''
        Runs the game
        '''
        while True:
            self.input.parseInputs()

            # Update objects
            self.surface.fill(WHITE)

            for entity in self.entities:
                entity.draw(self.surface)

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
