class StringConstants(object):
    def __init__(self):
        self.multiple_entry_separator = "|"
        self.initial_empty_sequences = ("   %s " % self.multiple_entry_separator)*6
        self.saved_state_separator = "########"
        self.literal_memory_sequence = "&"
        self.literal_memory_sequence_separator = ";"

        self.AKAI_MIDIMIX_NAME = "MIDI Mix"
        self.BESPECO_MIDI_NAME = "USB MIDI Interface"
