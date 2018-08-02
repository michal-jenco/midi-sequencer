class AkaiMidimixStateNames(object):
    MAIN = "Main"
    SAMPLE_FRAME = "Sample Frame"


class AkaiMidimixState(object):
    def __init__(self, sequencer):
        self.sequencer = sequencer
        self.states = [AkaiMidimixStateNames.MAIN,
                       AkaiMidimixStateNames.SAMPLE_FRAME]
        self.state_index = 0

    def next(self):
        self.state_index += 1
        self.sequencer.frame_status.midi_input_listener_state_changed()
        print("AkaiMidimixState is now: %s" % self.get())

    def previous(self):
        self.state_index -= 1
        self.sequencer.frame_status.midi_input_listener_state_changed()
        print("AkaiMidimixState is now: %s" % self.get())

    def get(self):
        return self.states[self.state_index % len(self.states)]


class AkaiApcStateNames(object):
    pass


class AkaiApcState(object):
    def __init__(self, sequencer):
        self.sequencer = sequencer
        self.states = []
        self.state_index = 0

    def next(self):
        self.state_index += 1
        self.sequencer.frame_status.midi_input_listener_state_changed()
        print("%s is now: %s" % (self.__class__.__name__, self.get()))

    def previous(self):
        self.state_index -= 1
        self.sequencer.frame_status.midi_input_listener_state_changed()
        print("%s is now: %s" % (self.__class__.__name__, self.get()))

    def get(self):
        return self.states[self.state_index % len(self.states)]
