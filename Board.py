import itertools
import pygame

# Setup logging
import logging
logger = logging.getLogger(__file__)

# Local Imports
import Colours as colour


class Grid:
    '''
    Draws the grid and handles grid collisions and coordinate transformations
    '''
    def __init__(self, nSpaces, origin, dimensions):
        self.nSpaces = nSpaces
        self.origin = origin
        self.dimensions = dimensions
        self.victoryCoor = None


    def reset(self):
        self.victoryCoor = None


    def setVictoryCoor(self, coor):
        self.victoryCoor = coor


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

        if self.victoryCoor:
            x, y = self.getBoxCentre(self.victoryCoor)
            vert = pygame.locals.Rect(
                x - 10, y - 1.5*yDim/float(self.nSpaces),
                20, 3*yDim/float(self.nSpaces)
                )
            horiz = pygame.locals.Rect(
                x - 1.5*xDim/float(self.nSpaces), y - 10,
                3*xDim/float(self.nSpaces), 20
                )
            pygame.draw.rect(surface, colour.BLACK, vert)
            pygame.draw.rect(surface, colour.BLACK, horiz)


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
    '''
    Manages and draws the game board and pieces
    '''
    def __init__(self, surface):
        self.size = 5

        self.array = [[0 for _ in range(self.size)] for _ in range(self.size)]

        # Define grid size to be 5/7ths of the width of the window
        xMax, yMax = surface.get_size()
        self.grid = Grid(
            self.size,
            (1*xMax/float(7), 1*yMax/float(7)),
            (5*xMax/float(7), 5*yMax/float(7)),
        )

        self.beadRadius = int(xMax/float(20))

        # Used to highlight beads during removal
        self.highlight = None


    def reset(self):
        '''
        Resets the board, removing all beads and highlights
        '''
        self.grid.reset()
        for x, y in itertools.product(range(self.size), range(self.size)):
            self.setEmpty((x,y))
        self.highlight = None


    def draw(self, surface):
        # Draw grid
        self.grid.draw(surface)

        # Draw beads
        for x, y in itertools.product(range(self.size), range(self.size)):
            coor = (x,y)
            width = 1 if self.highlight == coor else 0
            if self._getSpace(coor) > 0:
                pygame.draw.circle(surface, colour.RED, self.grid.getBoxCentre(coor), self.beadRadius, width)
            elif self._getSpace(coor) < 0:
                pygame.draw.circle(surface, colour.BLUE, self.grid.getBoxCentre(coor), self.beadRadius, width)


    ### Position Detection Functions

    def getCoor(self, pos):
        '''
        Returns the grid coordinate of a given global position
        '''
        return self.grid.getGridCoor(pos)


    def isOnGrid(self, pos):
        '''
        Detect if position is on the grid
        '''
        return self.grid.isOnGrid(pos)


    def isOnBead(self, coor, pos):
        '''
        Detect if position is on a bead
        '''
        if (self.isSpaceEmpty(coor)):
            # If space is empty, cannot be on a bead
            return False
        else:
            # If space has a bead, check position falls within radius
            centre = self.grid.getBoxCentre(coor)
            return ((centre[0] - pos[0])**2) + ((centre[1] - pos[1])**2) < self.beadRadius**2

    ### Space-related Functions

    def _getSpace(self, coor):
        '''
        Helper function for accessing the space at a specific coordinate
        '''
        xCoor, yCoor = coor
        assert(xCoor > -1)
        assert(xCoor < self.size)
        assert(yCoor > -1)
        assert(yCoor < self.size)
        return self.array[xCoor][yCoor]


    def _setSpace(self, coor, val):
        '''
        Helper function for accessing the space at a specific coordinate
        '''
        xCoor, yCoor = coor
        assert(xCoor > -1)
        assert(xCoor < self.size)
        assert(yCoor > -1)
        assert(yCoor < self.size)
        self.array[xCoor][yCoor] = val


    def isSpaceEmpty(self, coor):
        return (self._getSpace(coor) == 0)


    def setEmpty(self, coor):
        self._setSpace(coor, 0)


    def setP1(self, coor):
        self._setSpace(coor, 1)


    def setP2(self, coor):
        self._setSpace(coor, -1)


    def isP1(self, coor):
        return (self._getSpace(coor) == 1)


    def isP2(self, coor):
        return (self._getSpace(coor) == -1)


    def areP1AndP2(self, coor1, coor2):
        '''
        Returns whether two spaces are controled by different players
        '''
        return ((self._getSpace(coor1) * self._getSpace(coor2)) < 0)


    def setHighlight(self, coor):
        self.highlight = coor


    def unsetHighlight(self):
        self.highlight = None

    ### Board-related Functions

    def countP1Beads(self):
        return sum([i.count(1) for i in self.array])


    def countP2Beads(self):
        return sum([i.count(-1) for i in self.array])


    def isFull(self):
        '''
        Returns whether the board has no empty spaces
        '''
        if sum([i.count(0) for i in self.array]) == 0:
            return True
        else:
            return False


    def _isOnBorder(self, coor):
        return ((0 in coor) or (self.size -1 in coor))


    def _isSpaceSurrounded(self, coor, matches=[4, -4]):
        if (self._isOnBorder(coor)):
            # Border squares cannot be surrounded
            return False
        else:
            permuts = [
                (coor[0], coor[1]+1),
                (coor[0], coor[1]-1),
                (coor[0]+1, coor[1]),
                (coor[0]-1, coor[1]) ]
            count = sum(self._getSpace(perm) for perm in permuts)
            if count in matches:
                return True
            else:
                return False


    def isSpaceSurrounded(self, coor):
        return self._isSpaceSurrounded(coor, matches=[4, -4])


    def isSpaceSurroundedByP1(self, coor):
        return self._isSpaceSurrounded(coor, matches=[4])


    def isSpaceSurroundedByP2(self, coor):
        return self._isSpaceSurrounded(coor, matches=[-4])


    def _isRowEmpty(self, rowNo):
        for x in range(self.size):
            if (not self._getSpace((x, rowNo)) == 0):
                return False
        return True


    def _isColEmpty(self, colNo):
        for y in range(self.size):
            if (not self._getSpace((colNo, y)) == 0):
                return False
        return True


    def canShiftUp(self):
        return self._isRowEmpty(0)


    def canShiftDown(self):
        return self._isRowEmpty(self.size - 1)


    def canShiftLeft(self):
        return self._isColEmpty(0)


    def canShiftRight(self):
        return self._isColEmpty(self.size - 1)


    def shiftUp(self):
        assert(self.canShiftUp())
        for y in range(1, self.size):
            for x in range(self.size):
                self._setSpace((x,y - 1), self._getSpace((x,y)))
                if (y == self.size - 1):
                    self.setEmpty((x, y))


    def shiftDown(self):
        assert(self.canShiftDown())
        for y in range(self.size - 1, 0, -1):
            for x in range(self.size):
                self._setSpace((x,y), self._getSpace((x, y - 1)))
                if (y == 1):
                    self.setEmpty((x, y - 1))


    def shiftLeft(self):
        assert(self.canShiftLeft())
        for x in range(1, self.size):
            for y in range(self.size):
                self._setSpace((x - 1, y), self._getSpace((x,y)))
                if (x == self.size - 1):
                    self.setEmpty((x, y))


    def shiftRight(self):
        assert(self.canShiftRight())
        for x in range(self.size - 1, 0, -1):
            for y in range(self.size):
                self._setSpace((x,y), self._getSpace((x - 1, y)))
                if (x == 1):
                    self.setEmpty((x - 1, y))


    def isVictory(self):
        for x, y in itertools.product(range(1, self.size-1), range(1, self.size-1)):
            coor = (x,y)
            if self.isSpaceSurrounded(coor):
                # Check if centre and outside have different coloured beads
                if self.areP1AndP2(coor, (x, y+1)):
                    self.grid.setVictoryCoor(coor)
                    return True
        return False
