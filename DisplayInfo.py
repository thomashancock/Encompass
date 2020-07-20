import pygame
pygame.font.init()

# Setup logging
import logging
logger = logging.getLogger(__file__)

# Local Imports
import Colours as colour


class DisplayInfo:
    def __init__(self):
        self.font = pygame.font.SysFont('Comic Sans MS', 30)

        self.activePlayer = None
        self.beadsRemaining = {1: 17, -1:17}


    def setActivePlayer(self, player):
        self.activePlayer = player


    def setP1BeadsRemaining(self, nBeads):
        self.beadsRemaining[1] = nBeads


    def setP2BeadsRemaining(self, nBeads):
        self.beadsRemaining[-1] = nBeads


    def draw(self, surface):
        xMax, yMax = surface.get_size()

        # Draw active player
        textPlayerTurn = self.font.render(f"Active Player: {self.activePlayer}", False, colour.BLACK)
        textPlayerTurnRect = textPlayerTurn.get_rect(center=(xMax/float(2), yMax/float(14)))
        surface.blit(textPlayerTurn, textPlayerTurnRect)

        # Draw beads remaining
        for i, nBeads in self.beadsRemaining.items():
            textPos = (int(((6 - i*5)*xMax)/float(12)), int(yMax/float(14)))

            radius = int(xMax/float(24))
            pygame.draw.circle(surface, colour.RED if i == 1 else colour.BLUE, textPos, radius)

            textBeadsRemaining = self.font.render("{}".format(nBeads), False, colour.BLACK)
            textBeadsRemainingRect = textBeadsRemaining.get_rect(center=textPos)
            surface.blit(textBeadsRemaining, textBeadsRemainingRect)
