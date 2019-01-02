import tkinter as tk

from source.scales import Scales
from source.parser_my import Parser
from source.constants import SetSequenceModes
from source.functions import insert_into_entry, log
from source.notes import *
from source.loggger import Loggger


class Context:
    def __init__(self, root, sequencer):
        self.midi = None
        self.sequencer = sequencer

        self.scale = None
        self.current_scales = [""] * 8
        self.bpm = tk.StringVar(root, "60")
        self.sequence = None
        self.str_sequence = None
        self.root = None
        self.roots = [0] * 8
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
        self.scheduling_sequences = [[], [], [], [], [], [], [], []]
        self.str_sequences = [[], [], [], [], [], [], [], []]
        self.poly_sequences = []
        self.poly_relative_sequences = []
        self.skip_notes_sequential_sequences = [[], [], [], [], [], [], [], []]
        self.skip_note_parallel_sequences = [[], [], [], [], [], [], [], []]
        self.octave_sequences = [[], [], [], [], [], [], [], [-2]]
        self.transpose_sequences = [[], [], [], [], [], [], [], []]
        self.root_sequences = [[e2], [], [], [], [], [], [], []]
        self.scale_sequences = [["lydian"], [], [], [], [], [], [], []]
        self.pitch_shift_sequences = [[], [], [], [], [], [], [], []]
        self.off_sequences = [[], [], [], [], [], [], [], []]
        self.midi_channels = [[], [], [], [], [], [], [], []]
        self.kick_notes = []

        self.poly = []
        self.poly_relative = []
        self.skip_notes_parallel = []
        self.skip_notes_sequential = []
        self.octave_sequence = []
        self.root_sequence = []
        self.scale_sequence = []
        self.mode_sequence = []
        self.reset_sequence = []
        self.reset_index = 0
        self.bpm_sequence = []
        self.sample_seqs = [[], [], [], [], [], [], [], [], [], []]

        self.playback_on = False
        self.solo_on = False
        self.scale_mode_changing_on = False
        self.off_list = []
        self.prob_skip_note = tk.StringVar(root)
        self.novation_midi_channel = None
        self.novation_logger = Loggger("../other")
        self.novation_dont_end_notes = False
        self.novation_record_on = False
        self.volca_fm_send_velocity = False

        self.novation_velocity_min = 0
        self.novation_velocity_max = 127
        self.get_novation_velocity_range = lambda: (self.novation_velocity_min, self.novation_velocity_max)

        self.midi_port = None

    def get_bpm(self):
        return float(self.bpm.get())

    def get_current_reset_object(self):
        return self.reset_sequence[self.reset_index % len(self.reset_sequence)]

    def get_current_mode_wrap(self, steps_played):
        return self.mode_sequence[(steps_played % self.mode_sequence.__len__())] if self.mode_sequence \
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
