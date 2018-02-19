MODE_SIMPLE = 100
MODE_SAMPLE = 102

NOTE_PAUSE = 9999
GO_TO_START = 9999+1

DISABLED = 0
ENABLED = 1


class DelayFunctions:
    def __init__(self):
        self.dc = DelayConstants
        self.functions = {}

        self.functions[self.dc.CONSTANT_DECAY] = (lambda note, value:
                                                  [note[0], note[1], note[2] + value])


class DelayConstants:
    CONSTANT_DECAY = "Constant decay"

    UP = 1
    DOWN = -1