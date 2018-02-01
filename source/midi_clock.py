class MidiClock:
    def __init__(self, context):
        self.context = context


    def step(self):
        msg = [248]
        self.context.midi.send_message(msg)
