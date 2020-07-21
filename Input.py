import pygame
from Actions import *

class Input:
    def __init__(self):
        pass


    def parseInputs(self, actionQueue):
        for event in pygame.event.get():
            # Detect Quit Action
            if event.type == pygame.locals.QUIT:
                actionQueue.append(Action("QUIT"))

            elif event.type == pygame.MOUSEBUTTONUP:
                pos = pygame.mouse.get_pos()
                actionQueue.append(ActionMouseClick(pos))

            elif event.type == pygame.KEYUP:
                actionQueue.append(ActionKeyPressed(event.key))
