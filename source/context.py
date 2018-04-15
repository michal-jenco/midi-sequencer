import tkinter as tk

from source.scales import Scales
from source.parser_my import Parser
from source.constants import SetSequenceModes


class Context:
    def __init__(self, root, sequencer):
        self.midi = None

        self.scale = None
        self.bpm = tk.StringVar(root, "150")
        self.sequence = None
        self.str_sequence = None
        self.root = None
        self.mode = None

        self.memory_sequences = {}
        self.memory_sequences["main melody"] = []
        self.memory_filepath = "../memory/"
        self.memory_dir = r"I:\Pycharm projects\MIDI\memory"

        self.logfile = open("../other/logfile.txt", "a")

        self.get_delay_multiplier = sequencer.strvar_delay_multiplier.get

        self.scales = Scales()
        self.parser = Parser()
        self.set_sequence_modes = SetSequenceModes()

        self.note_sequences = []
        self.poly_sequences = []
        self.poly_relative_sequences = []
        self.skip_notes_sequential_sequences = []
        self.skip_note_parallel_sequences = []
        self.octave_sequences = []
        self.root_sequences = []
        self.scale_sequences = []
        self.off_sequences = []

        self.midi_channels = []

        self.poly = []
        self.poly_relative = []
        self.skip_notes_parallel = []
        self.skip_notes_sequential = []

        self.octave_sequence = []
        self.root_sequence = []
        self.scale_sequence = []

        self.sample_seqs = []
        for i in range(0, 10):
            self.sample_seqs.append([])

        self.playback_on = False
        self.off_list = []
        self.prob_skip_note = tk.StringVar(root)

        self.comma_pause = 1
        self.dot_pause = 2
        self.dash_pause = 4

        self.question_min = 1
        self.question_max = 8

        self.paragraph_min = 1
        self.paragraph_max = 8

        self.amper_min = 1
        self.amper_max = 8

        self.midi_port = None
