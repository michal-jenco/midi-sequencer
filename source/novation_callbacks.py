class NovationCallbacks(object):
    def __init__(self, sequencer, context):
        self.sequencer = sequencer
        self.context = context

    def midi_channel_left(self):
        self.context.novation_launchkey_notes_channel -= 1
        self.sequencer.label_novation_launchkey_note_channel.config(
            text=str(self.context.novation_launchkey_notes_channel))

    def midi_channel_right(self):
        self.context.novation_launchkey_notes_channel += 1
        self.sequencer.label_novation_launchkey_note_channel.config(
            text=str(self.context.novation_launchkey_notes_channel))

    def slider_1(self, value):
        self.context.novation_velocity_min = value

    def slider_2(self, value):
        self.context.novation_velocity_max = value

    def slider_3(self, value):
        ...

    def slider_4(self, value):
        ...

    def slider_5(self, value):
        ...

    def slider_6(self, value):
        ...

    def slider_7(self, value):
        ...

    def slider_8(self, value):
        ...

    def slider_9(self, value):
        ...

    def knob_1(self, value):
        ...

    def knob_2(self, value):
        ...

    def knob_3(self, value):
        ...

    def knob_4(self, value):
        ...

    def knob_5(self, value):
        ...

    def knob_6(self, value):
        ...

    def knob_7(self, value):
        ...

    def knob_8(self, value):
        ...

    def button_1(self):
        self.context.novation_dont_end_notes = not self.context.novation_dont_end_notes

    def button_2(self):
        for i in range(128):
            self.context.midi.send_message(
                [0x90 + self.context.novation_launchkey_notes_channel, i, 0])
