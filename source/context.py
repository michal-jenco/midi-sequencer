from notes import *
import tkinter as tk


class Context:
    def __init__(self, root):
        self.midi = None

        self.scale = None
        self.bpm = tk.StringVar(root, "40")
        self.sequence = None
        self.str_sequence = None
        self.root = c3
        self.mode = None

        self.poly = []
        self.skip_notes = []

        self.sample_seqs = []
        for i in range(0, 10):
            self.sample_seqs.append([])

        self.playback_on = False

        self.off_list = []

        self.prob_skip_note = tk.StringVar(root)

        self.drone_seq = []
        self.each_drone_count = 2*2
        self.drone_freq = tk.IntVar(root)
        self.drone_freq.set(8)

        self.scale_freq = 8

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
