import tkinter as tk

from source.scales import Scales
from source.parser_my import Parser
from source.constants import SetSequenceModes
from source.functions import insert_into_entry, log
from source.notes import *


class Context:
    def __init__(self, root, sequencer):
        self.midi = None
        self.sequencer = sequencer

        self.scale = None
        self.current_scales = [""] * 7
        self.bpm = tk.StringVar(root, "60")
        self.sequence = None
        self.str_sequence = None
        self.root = None
        self.roots = [0] * 7
        self.mode = None
        self.scale_mode = 0

        self.memory_sequences = {"main melody": []}
        self.memory_filepath = "../memory/"
        self.memory_dir = r"I:\Pycharm projects\MIDI\memory"
        self.state_dir = r"../state/"
        self.logfile = open("../other/logfile.txt", "a")

        self.get_delay_multiplier = sequencer.strvar_delay_multiplier.get

        self.scales = Scales(context=self)
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
        # self.mode_sequences = [[], [], [], [], [], [], []]
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
        self.mode_sequence = []
        self.sample_seqs = [[], [], [], [], [], [], [], [], [], []]

        self.playback_on = False
        self.solo_on = False
        self.scale_mode_changing_on = False
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

    def get_current_mode_wrap(self, steps_played):
        return self.mode_sequence[(steps_played % self.mode_sequence.__len__())]  if self.mode_sequence \
            else self.sequencer.entry_mode.get()

    def change_mode(self, offset=None, set_to=None):
        if set_to is not None:
            self.scale_mode = set_to
        else:
            if offset < 0 and not self.scale_mode:
                return
            self.scale_mode += offset

        insert_into_entry(self.sequencer.entry_mode, str(self.scale_mode))
        self.sequencer.set_memory_sequence(None)
        self.sequencer.set_status_bar_content()
        self.sequencer.frame_status.update()

        log(msg="Mode set to: %s" % self.scale_mode)
