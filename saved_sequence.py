class SavedSequence:
    def __init__(self, context):
        self.seq = context.sequence
        self.root = context.root
        self.seq_len = len(self.seq)
        self.scale = context.scale
        self.bpm = context.bpm
        self.midi_port = context.midi_port
        self.date_created = None
        self.name = ""
