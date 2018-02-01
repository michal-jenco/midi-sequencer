import tkinter as tk

from source.constants import *


class Evolver:
    def __init__(self, context, root):

        self.running = False
        self.root = root

        self.seq_history = []

        self.original_seq = context.sequence
        self.evolved_seq = self.original_seq

        self.prob_delete_note = .1
        self.prob_delete_pause = .1

        self.prob_replace_note = .1
        self.prob_replace_pause = .1
        self.prob_pause_comma = .1
        self.prob_pause_dot = .1
        self.prob_pause_dash = .1
        self.prob_root = .1
        self.prob_prob_octave_one_up = .1
        self.prob_prob_octave_one_down = .1
        self.prob_prob_octave_two_up = .1
        self.prob_prob_octave_two_up = .1
        self.prob_ = .1

        self.min_replace_notes = 1
        self.max_replace_notes = 8
        self.min_replace_pauses  = 1
        self.max_replace_pauses  = 8
        self.min_ = .1
        self.max_ = .9
        self.min_ = .1
        self.max_ = .9
        self.min_ = .1
        self.max_ = .9
        self.min_ = .1
        self.max_ = .9

        self.i_grow = tk.IntVar(self.root, DISABLED)
        self.i_shrink = tk.IntVar(self.root, DISABLED)
        self.i_replace_pauses = tk.IntVar(self.root, DISABLED)
        self.i_replace_notes = tk.IntVar(self.root, DISABLED)
        self.i_replace_question = tk.IntVar(self.root, DISABLED)
        self.i_save_changes = tk.IntVar(self.root, ENABLED)

    def get_evolved_seq(self):
        return self.evolved_seq

    def get_original_seq(self):
        return self.original_seq

    def do_steps(self, context, i=2):
        for k in range(0, i):
            self.do_step(context)

    def do_step(self, context):
        c = context

        if self.i_grow:
            pass

        if self.i_shrink:
            pass

        if self.i_replace_pauses:
            pass

        if self.i_replace_notes:
            pass

        if self.i_replace_question:
            pass

        if self.i_save_changes:
            self.seq_history.append(self.evolved_seq)

    def loop_through_history(self, direction="up"):
        pass




