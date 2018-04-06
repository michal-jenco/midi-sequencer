from source.notes import *

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


class SetSequenceModes:
    def __init__(self):
        self.regenerate = "regenerate"
        self.dont_regenerate = "don't regenerate"


note_dict = {"c": c2, "cs": cs2, "d": d2, "ds": ds2, "e": e2, "f": f2, "fs": fs2, "g": g2, "gs": gs2,
             "a": a2, "as": as2, "h": b2, "b": b2, "df": cs2, "ef": ds2, "gf": fs2, "af": gs2, "bf": as2}
