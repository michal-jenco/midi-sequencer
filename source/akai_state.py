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


class AkaiApcStates(object):
    NORMAL = "Normal"
    SHIFT = "Shift"
    WOBBLER = "Wobbler"


class AkaiApcState(object):
    def __init__(self, sequencer):
        self.sequencer = sequencer
        self.sequential_states = [AkaiApcStates.NORMAL]
        self.current_state = AkaiApcStates.NORMAL
        self.sequential_state_index = 0
        self.previous_column = None
        self.wobbler_control_active = False

    def turn_on_shift(self):
        self.current_state = AkaiApcStates.SHIFT

    def turn_off_shift(self):
        self.current_state = self.sequential_states[self.sequential_state_index % len(self.sequential_states)]

    def toggle_wobbler(self):
        self.wobbler_control_active = not self.wobbler_control_active

    def next(self):
        self.sequential_state_index += 1
        self.sequencer.frame_status.midi_input_listener_state_changed()
        print("%s is now: %s" % (self.__class__.__name__, self.get()))

    def previous(self):
        self.sequential_state_index -= 1
        self.sequencer.frame_status.midi_input_listener_state_changed()
        print("%s is now: %s" % (self.__class__.__name__, self.get()))

    def get(self):
        return self.sequential_states[self.sequential_state_index % len(self.sequential_states)]
