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

        self.beadsRemaining = {1: 17, -1:17}
        # self.activePlayer = None
        # self.hasEnded = False

        self.topStr = None
        self.bottomStr = None


    # def setActivePlayer(self, player):
    #     self.activePlayer = player


    # def setVictory(self):
    #     self.hasEnded = True

    def setTopText(self, str):
        self.topStr = str


    def setBottomText(self, str):
        self.bottomStr = str


    def eraseBottomText(self):
        self.bottomStr = None


    def setP1BeadsRemaining(self, nBeads):
        self.beadsRemaining[1] = nBeads


    def setP2BeadsRemaining(self, nBeads):
        self.beadsRemaining[-1] = nBeads


    def draw(self, surface):
        xMax, yMax = surface.get_size()

        # Draw active player
        topText = self.font.render(self.topStr, False, colour.BLACK)
        topTextRect = topText.get_rect(center=(xMax/float(2), yMax/float(14)))
        surface.blit(topText, topTextRect)

        if self.bottomStr:
            bottomText = self.font.render(self.bottomStr, False, colour.BLACK)
            bottomTextRect = bottomText.get_rect(center=(xMax/float(2), 13*yMax/float(14)))
            surface.blit(bottomText, bottomTextRect)

        # Draw beads remaining
        for i, nBeads in self.beadsRemaining.items():
            textPos = (int(((6 - i*5)*xMax)/float(12)), int(yMax/float(14)))

            radius = int(xMax/float(24))
            pygame.draw.circle(surface, colour.RED if i == 1 else colour.BLUE, textPos, radius)

            textBeadsRemaining = self.font.render("{}".format(nBeads), False, colour.BLACK)
            textBeadsRemainingRect = textBeadsRemaining.get_rect(center=textPos)
            surface.blit(textBeadsRemaining, textBeadsRemainingRect)
