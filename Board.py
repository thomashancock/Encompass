import itertools
import pygame

# Setup logging
import logging
logger = logging.getLogger(__file__)

# Local Imports
import Colours as colour


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

        self.array = [[0 for _ in range(self.size)] for _ in range(self.size)]

        # Define grid size to be 5/7ths of the width of the window
        xMax, yMax = surface.get_size()
        self.grid = Grid(
            self.size,
            (1*xMax/float(7), 1*yMax/float(7)),
            (5*xMax/float(7), 5*yMax/float(7)),
        )

        self.beadRadius = int(xMax/float(20))


    def getCoor(self, pos):
        '''
        Returns the grid coordinate of a given global position
        '''
        return self.grid.getGridCoor(pos)


    def isOnGrid(self, pos):
        return self.grid.isOnGrid(pos)


    def isOnBead(self, coor, pos):
        centre = self.grid.getBoxCentre(coor)
        return ((centre[0] - pos[0])**2) + ((centre[1] - pos[1])**2) < self.beadRadius**2


    def _getSpace(self, coor):
        xCoor, yCoor = coor
        return self.array[xCoor][yCoor]


    def _setSpace(self, coor, val):
        xCoor, yCoor = coor
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
            up = (coor[0], coor[1]+1)
            down = (coor[0], coor[1]-1)
            left = (coor[0]+1, coor[1])
            right = (coor[0]-1, coor[1])
            permuts = [up, down, left, right]
            count = sum(self._getSpace(perm) for perm in permuts)
            logging.info("{} {}: {}".format(*coor, count))
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


    def isVictory(self):
        logging.info("Checking for victory")
        for x, y in itertools.product(range(1, self.size-1), range(1, self.size-1)):
            coor = (x,y)
            if self.isSpaceSurrounded(coor):
                # Check if centre and outside have different coloured beads
                if self._getSpace(coor) * self._getSpace((x, y+1)) < 0:
                    return True
        return False


    def draw(self, surface):
        surface.fill(colour.WHITE)

        # Draw 5x5 grid
        self.grid.draw(surface)

        # Draw beads
        for x, y in itertools.product(range(self.size), range(self.size)):
            coor = (x,y)
            if self._getSpace(coor) > 0:
                pygame.draw.circle(surface, colour.RED, self.grid.getBoxCentre(coor), self.beadRadius)
            elif self._getSpace(coor) < 0:
                pygame.draw.circle(surface, colour.BLUE, self.grid.getBoxCentre(coor), self.beadRadius)
