import tkinter as tk

from source.scales import Scales
from source.parser_my import Parser
from source.constants import SetSequenceModes
from source.notes import *


class Context:
    def __init__(self, root, sequencer):
        self.midi = None

        self.scale = None
        self.scales_individual = [""]*7
        self.bpm = tk.StringVar(root, "60")
        self.sequence = None
        self.str_sequence = None
        self.root = None
        self.roots = [0]*7
        self.mode = None

        self.memory_sequences = {"main melody": []}
        self.memory_filepath = "../memory/"
        self.memory_dir = r"I:\Pycharm projects\MIDI\memory"
        self.state_dir = r"../state/"
        self.logfile = open("../other/logfile.txt", "a")

        self.get_delay_multiplier = sequencer.strvar_delay_multiplier.get

        self.scales = Scales()
        self.parser = Parser(self)
        self.set_sequence_modes = SetSequenceModes()

        self.note_sequences = []
        self.scheduling_sequences = [[], [], [], [], [], [], []]
        self.str_sequences = [0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.poly_sequences = []
        self.poly_relative_sequences = []
        self.skip_notes_sequential_sequences = []
        self.skip_note_parallel_sequences = []
        self.octave_sequences = [[], [], [], [], [], [], [-2]]
        self.root_sequences = [[e2], [], [], [], [], [], []]
        self.scale_sequences = [["lydian"], [], [], [], [], [], []]
        self.off_sequences = [[], [], [], [], [], [], [1]]
        self.midi_channels = [[], [], [], [], [], [], []]
        self.kick_notes = []

        self.poly = []
        self.poly_relative = []
        self.skip_notes_parallel = []
        self.skip_notes_sequential = []
        self.octave_sequence = []
        self.root_sequence = []
        self.scale_sequence = []
        self.sample_seqs = [[], [], [], [], [], [], [], [], [], []]

        self.playback_on = False
        self.solo_on = False
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

    def get_bpm(self):
        return float(self.bpm.get())
