class AkaiMidimixStates:
    MAIN = "Main"
    SAMPLE_FRAME = "Sample Frame"


class AkaiMidimixState(object):
    def __init__(self):
        self.states = [AkaiMidimixStates.MAIN,
                       AkaiMidimixStates.SAMPLE_FRAME]
        self.state_index = 0

    def next(self):
        self.state_index += 1
        print("AkaiMidimixState is now: %s" % self.get())

    def previous(self):
        self.state_index -= 1
        print("AkaiMidimixState is now: %s" % self.get())

    def get(self):
        return self.states[self.state_index % len(self.states)]
