import itertools
import pygame

# Setup logging
import logging
logger = logging.getLogger(__file__)

# Local Imports
import Colours as colour


class Space:
    '''
    Records the status of a single space. Can be empty, P1 or P2
    '''
    def __init__(self):
        self.state="empty"


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


class Grid:
    def __init__(self, nSpaces, origin, dimensions):
        self.nSpaces = nSpaces
        self.origin = origin
        self.dimensions = dimensions


    def draw(self, surface):
        '''
        Draw the game grid without side edges
        '''
        xOrig, yOrig = self.origin # Coordinate of upper left corner of grid
        xDim, yDim = self.dimensions # Dimensions of grid

        for i in range(1, self.nSpaces):
            # Horizontal lines
            pygame.draw.line(surface, colour.GREY,
                (xOrig + i*xDim/float(self.nSpaces), yOrig),
                (xOrig + i*xDim/float(self.nSpaces), yOrig + yDim))

            # Vertical lines
            pygame.draw.line(surface, colour.GREY,
                (xOrig       , yOrig + i*yDim/float(self.nSpaces)),
                (xOrig + xDim, yOrig + i*yDim/float(self.nSpaces)))


    def getBoxCentre(self, coor):
        '''
        Returns the pixel coordinate at the centre of a grid box
        '''
        x, y = coor
        assert(x > -1)
        assert(x < self.nSpaces)
        assert(y > -1)
        assert(y < self.nSpaces)

        def getAlongAxis(n, max):
            return (0.5 + n)*max/float(self.nSpaces)

        xOrig, yOrig = self.origin
        xDim, yDim = self.dimensions
        return int(xOrig + getAlongAxis(x, xDim)), int(yOrig + getAlongAxis(y, yDim))


    def isOnGrid(self, pos):
        for i in [0, 1]:
            if (pos[i] < self.origin[i] or pos[i] > self.origin[i] + self.dimensions[i]):
                return False
        return True


    def getGridCoor(self, pos):
        xPosRel, yPosRel = pos[0] - self.origin[0], pos[1] - self.origin[1]

        if (xPosRel < 0 or yPosRel < 0):
            return (-1, -1)
        else:
            xCoor = int(self.nSpaces * (xPosRel/float(self.dimensions[0])))
            yCoor = int(self.nSpaces * (yPosRel/float(self.dimensions[1])))
            if (xCoor > self.nSpaces - 1 or yCoor > self.nSpaces - 1):
                return (-1, -1)
            return xCoor, yCoor


class Board:
    def __init__(self, surface):
        self.size = 5
        self.array = [[Space() for _ in range(self.size)] for _ in range(self.size)]

        # Define grid size to be 5/7ths of the width of the window
        xMax, yMax = surface.get_size()
        self.grid = Grid(
            self.size,
            (1*xMax/float(7), 1*yMax/float(7)),
            (5*xMax/float(7), 5*yMax/float(7)),
        )


    def getSpace(self, coor):
        xCoor, yCoor = coor
        return self.array[xCoor][yCoor]


    def processClick(self, pos):
        if (self.grid.isOnGrid(pos)):
            clickCoor = self.grid.getGridCoor(pos)
            logging.info("Click signal received: coordinate {} {}".format(*clickCoor))

            space = self.getSpace(clickCoor)
            if (space.isEmpty()):
                space.setP1()
            elif (space.isP1()):
                space.setP2()
            else:
                space.setEmpty()

        else:
            logging.info("Click signal received: position {} {}".format(*pos))


    def draw(self, surface):
        surface.fill(colour.WHITE)

        xMax, yMax = surface.get_size()

        # Draw 5x5 grid
        self.grid.draw(surface)

        # Draw beads
        for x, y in itertools.product(range(self.size), range(self.size)):
            if (self.getSpace((x,y)).isP1()):
                pixelCoor = self.grid.getBoxCentre((x,y))
                pygame.draw.circle(surface, colour.RED, pixelCoor, int(xMax/float(20)))
            if (self.getSpace((x,y)).isP2()):
                pixelCoor = self.grid.getBoxCentre((x,y))
                pygame.draw.circle(surface, colour.BLUE, pixelCoor, int(xMax/float(20)))
