class Action:
    '''
    Base class for actions
    '''
    def __init__(self, aType):
        self.aType = aType


    def getActionType(self):
        return self.aType


class ActionMouseClick(Action):
    '''
    Action for mouse clicks
    '''
    def __init__(self, pos):
        Action.__init__(self, "MOUSEBUTTONUP")
        self.pos = pos


    def getPos(self):
        return self.pos
