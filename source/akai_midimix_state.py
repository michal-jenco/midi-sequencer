class AkaiMidimixStates:
    MAIN = "Main"
    SAMPLE_FRAME = "Sample Frame"


class AkaiMidimixState(object):
    def __init__(self, sequencer):
        self.sequencer = sequencer
        self.states = [AkaiMidimixStates.MAIN,
                       AkaiMidimixStates.SAMPLE_FRAME]
        self.state_index = 0

    def next(self):
        self.state_index += 1
        self.sequencer.status_frame.midi_input_listener_state_changed()
        print("AkaiMidimixState is now: %s" % self.get())

    def previous(self):
        self.state_index -= 1
        self.sequencer.status_frame.midi_input_listener_state_changed()
        print("AkaiMidimixState is now: %s" % self.get())

    def get(self):
        return self.states[self.state_index % len(self.states)]
