import tkinter as tk
import threading
import time
import copy
import random

from source.note_lengths import NoteLengths
from source.context import Context
from source.evolver import Evolver
from source.wobbler import Wobbler
from source.constants import *
from source.sample_frame import SampleFrame
from source.delay import Delay
from source.helpful_functions import a
from source.functions import log
from source.memory import Memory
from source.string_constants import StringConstants


class Sequencer(tk.Frame):

    def __init__(self, midi_):
        self.root = tk.Tk()
        tk.Frame.__init__(self, self.root, bg="darkblue", padx=5, pady=5)

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.root.title("MIDI Sequencer")
        self.root["bg"] = "black"
        self.root.geometry('+0+0')

        self.string_constants = StringConstants()

        self.threads = []

        self.frame_delay = tk.Frame(self.root)
        self.frame_delay["bg"] = "yellow"
        self.strvar_delay_multiplier = tk.StringVar(self.frame_delay)
        self.scale_delay_multiplier = tk.Scale(self.frame_delay, from_=0.1, to=10.0, orient=tk.HORIZONTAL,
                                               sliderlength=30, resolution=0.1,
                                               variable=self.strvar_delay_multiplier, length=500)

        self.intvar_checkbox_state = tk.IntVar(self.root)
        self.check_delay_is_on = tk.Checkbutton(self.frame_delay,
                                                text="D e  l   a    y      o  n ?",
                                                variable=self.intvar_checkbox_state)
        self.delay_is_on = lambda: True if self.intvar_checkbox_state.get() == 1 else False

        self.context = Context(self.root, self)
        self.context.drone_seq = [0, 1, -2, -3]
        self.context.each_drone_count = 8
        self.context.root = e2
        self.context.mode = MODE_SIMPLE
        self.context.scale = None
        self.context.playback_on = False

        self.frame_memories = tk.Frame(self.root)
        self.memories = []
        self.memories.append(Memory(self.frame_memories, self.context, MemoryType().melody))

        self.set_sequence_modes = SetSequenceModes()

        self.idx = 0
        self.actual_notes_played_count = 0

        self.context.midi = midi_

        self.bpm = float(self.context.bpm.get())

        self.d = Delay(self.context)
        self.df = DelayFunctions()
        self.dc = DelayConstants()

        self.evolver = Evolver(self.context, self.root)
        self.wobblers = []

        self.frame_wobblers = tk.Frame(self.root, bg="black")

        self.wobblers.append(Wobbler(self.frame_wobblers, self.context, "Keys wobbler 1"))
        self.wobblers.append(Wobbler(self.frame_wobblers, self.context, "Keys wobbler 2"))
        self.wobblers.append(Wobbler(self.frame_wobblers, self.context, "Keys wobbler 3"))
        self.wobblers.append(Wobbler(self.frame_wobblers, self.context, "Keys wobbler 4"))

        self.sample_frame = SampleFrame(self.root, self.context)

        self.strvar_tempo_multiplier = tk.StringVar(self.root, "3")
        self.option_tempo_multiplier = tk.OptionMenu(self.root, self.strvar_tempo_multiplier, *[x for x in range(1, 9)])
        self.get_tempo_multiplier = lambda: int(self.strvar_tempo_multiplier.get())

        self.strvar_option_midi_channel = tk.StringVar(self.root, "12")
        self.option_midi_channel = tk.OptionMenu(self.root, self.strvar_option_midi_channel, *range(17))

        self.strvar_option_midi_channel2 = tk.StringVar(self.root, "11")
        self.option_midi_channel2 = tk.OptionMenu(self.root, self.strvar_option_midi_channel2, *range(17))

        self.frame_entries = tk.Frame(self.root)
        self.frame_entries["bg"] = "purple"
        self.frame_scale_buttons = tk.Frame(self.root)
        self.frame_sliders = tk.Frame(self.root)
        self.frame_roots = tk.Frame(self.root)
        self.frame_prob_sliders = tk.Frame(self.root)

        label_font = ("Courier", "11")
        self.strvar_status_bar = tk.StringVar(self.root, "")
        self.label_status_bar = tk.Label(self.root, textvariable=self.strvar_status_bar, font=label_font)

        self.strvar_main_seq_len = tk.StringVar(self.frame_entries)
        self.label_main_seq_len = tk.Label(self.frame_entries, textvariable=self.strvar_main_seq_len,
                                           font=label_font, width=4)

        self.strvar_main_seq_current_idx = tk.StringVar(self.frame_entries, "")
        self.label_main_seq_current_idx = tk.Label(self.frame_entries, textvariable=self.strvar_main_seq_current_idx,
                                                   font=label_font, width=4)

        self.strvar_prob_skip_note = tk.StringVar(self.frame_sliders)
        self.scale_prob_skip_note = tk.Scale(self.frame_sliders, from_=0, to=100, orient=tk.HORIZONTAL, sliderlength=30,
                                             variable=self.context.prob_skip_note, length=500)

        self.strvar_vel_min = tk.StringVar(self.frame_prob_sliders)
        self.strvar_vel_min.set("100")
        self.scale_vel_min = tk.Scale(self.frame_prob_sliders, from_=0, to=127, orient=tk.VERTICAL,
                                      variable=self.strvar_vel_min, length=150)

        self.strvar_vel_max = tk.StringVar(self.frame_prob_sliders)
        self.strvar_vel_max.set("127")
        self.scale_vel_max = tk.Scale(self.frame_prob_sliders, from_=0, to=127, orient=tk.VERTICAL,
                                      variable=self.strvar_vel_max, length=150)

        self.strvar_prob_skip_poly = tk.StringVar(self.frame_prob_sliders)
        self.strvar_prob_skip_poly.set("50")
        self.scale_prob_skip_poly = tk.Scale(self.frame_prob_sliders, from_=0, to=100, orient=tk.VERTICAL,
                                             variable=self.strvar_prob_skip_poly, length=150)

        self.strvar_prob_skip_poly_relative = tk.StringVar(self.frame_prob_sliders)
        self.strvar_prob_skip_poly_relative.set("50")
        self.scale_prob_skip_poly_relative = tk.Scale(self.frame_prob_sliders, from_=0, to=100, orient=tk.VERTICAL,
                                                      variable=self.strvar_prob_skip_poly_relative, length=150)

        self.strvar_bpm = tk.StringVar(self.frame_sliders)
        self.scale_bpm = tk.Scale(self.frame_sliders, from_=5, to=600, orient=tk.HORIZONTAL, sliderlength=30,
                                  variable=self.context.bpm, length=500)

        self.label_a = tk.Label(self.frame_entries, font=label_font, text="Main Sequence".ljust(20), height=1)
        self.label_a2 = tk.Label(self.frame_entries, font=label_font, text="Memory Sequence".ljust(20), height=1)
        self.label_b = tk.Label(self.frame_entries, font=label_font, text="Main Seq Repr".ljust(20), height=1)
        self.label_c = tk.Label(self.frame_entries, font=label_font, text="Stop Notes".ljust(20), height=1)
        self.label_d = tk.Label(self.frame_entries, font=label_font, text="Polyphony".ljust(20), height=1)
        self.label_e = tk.Label(self.frame_entries, font=label_font, text="Polyphony Relative".ljust(20), height=1)
        self.label_f = tk.Label(self.frame_entries, font=label_font, text="Skip Notes Seq".ljust(20), height=1)
        self.label_g = tk.Label(self.frame_entries, font=label_font, text="Skip Notes Par".ljust(20), height=1)
        self.label_h = tk.Label(self.frame_entries, font=label_font, text="Octave Sequence".ljust(20), height=1)
        self.label_i = tk.Label(self.frame_entries, font=label_font, text="Root Sequence".ljust(20), height=1)
        self.label_j = tk.Label(self.frame_entries, font=label_font, text="Scale Sequence".ljust(20), height=1)
        self.label_k = tk.Label(self.frame_entries, font=label_font, text="MIDI Channels".ljust(20), height=1)

        self.thread_seq = threading.Thread(target=self.play_sequence, args=())
        self.thread_seq.daemon = True
        self.threads.append(self.thread_seq)
        self.thread_seq.start()

        roots = [(c2, "C"), (cs2, "C#"), (d2, "D"), (ds2, "Eb"),
                 (e2, "E"), (f2, "F"), (fs2, "F#",), (g2, "G"),
                 (gs2, "G#"), (a2, "A"), (as2, "Bb"), (b2, "B")]

        def set_root(root, context):
            context.root = root

        row_ = 0
        col_ = 0
        for root in roots:
            tk.Button(self.frame_roots,
                      text=root[1],
                      command=lambda x=root[0]: set_root(x, self.context)).grid(row=row_, column=col_)
            col_ += 1

        button_font = ("Courier", "8")
        wrap = 8
        row_ = 0
        col_ = 0
        for scale in self.context.scales.get_all():
            scale_name = self.context.scales.get_display_scale_name(scale)

            tk.Button(self.frame_scale_buttons,
                      text=scale_name,
                      width=18,
                      height=1,
                      font=button_font,
                      command=lambda y=scale: self.set_scale(y)) \
                .grid(row=(row_), column=(col_ % wrap), sticky="nsew")

            col_ += 1

            if col_ % wrap == 0:
                row_ += 1
                col_ = 0

        self.entry_str_seq = tk.Entry(self.frame_entries, width=80)
        self.entry_sequence = tk.Entry(self.frame_entries, width=80)
        self.entry_sequence.bind('<Return>', self.set_sequence)
        self.entry_sequence.bind('<Control-Return>', lambda typ=MemoryType().melody: self.add_seq_to_memory(typ))
        self.entry_sequence.delete(0, tk.END)
        self.entry_sequence.insert(0, "054")
        self.set_scale("lydian")
        self.set_sequence(None)

        self.entry_memory_sequence = tk.Entry(self.frame_entries, width=80)
        self.entry_memory_sequence.bind('<Return>', self.set_memory_sequence)

        self.entry_memory_sequence2 = tk.Entry(self.frame_entries, width=80)
        self.entry_memory_sequence2.bind('<Return>', self.set_memory_sequence)

        self.entry_off_array = tk.Entry(self.frame_entries, width=80)
        self.entry_off_array.bind('<Return>', self.set_off_array)

        self.entry_poly = tk.Entry(self.frame_entries, width=80)
        self.entry_poly.bind('<Return>', self.set_poly)

        self.entry_poly_relative = tk.Entry(self.frame_entries, width=80)
        self.entry_poly_relative.bind('<Return>', self.set_poly_relative)

        self.entry_skip_note_parallel = tk.Entry(self.frame_entries, width=80)
        self.entry_skip_note_parallel.bind('<Return>', self.set_skip_note_parallel)

        self.entry_skip_note_sequential = tk.Entry(self.frame_entries, width=80)
        self.entry_skip_note_sequential.bind('<Return>', self.set_skip_note_sequential)

        self.entry_root_sequence = tk.Entry(self.frame_entries, width=80)
        self.entry_root_sequence.bind('<Return>', self.set_root_sequence)

        self.entry_octave_sequence = tk.Entry(self.frame_entries, width=80)
        self.entry_octave_sequence.bind('<Return>', self.set_octave_sequence)

        self.entry_scale_sequence = tk.Entry(self.frame_entries, width=80)
        self.entry_scale_sequence.bind('<Return>', self.set_scale_sequence)

        self.entry_midi_channels = tk.Entry(self.frame_entries, width=80)
        self.entry_midi_channels.bind('<Return>', self.set_midi_channels)

        self.entry_boxes = [self.entry_off_array, self.entry_poly, self.entry_poly_relative,
                            self.entry_skip_note_parallel, self.entry_skip_note_sequential, self.entry_midi_channels,
                            self.entry_root_sequence, self.entry_octave_sequence, self.entry_scale_sequence]

        for entry in self.entry_boxes:
            entry.insert(0, self.string_constants.initial_empty_sequences)

    def on_closing(self):
        log(msg="Window will be destroyed.")
        self.root.quit()
        self.root.destroy()

    def show(self):

        tk.Button(self.root,
                  text="Start sequence",
                  command=self.start_sequence).grid(row=0, column=8, padx=10)

        tk.Button(self.root,
                  text="Stop sequence",
                  command=self.stop_sequence).grid(row=1, column=8, padx=10)

        tk.Button(self.root,
                  text="All notes off",
                  command=self.end_all_notes).grid(row=2, column=8, padx=10)

        tk.Button(self.root,
                  text="Pitch bend ON",
                  command=lambda: self.pitch_bend("on")).grid(row=3, column=8, padx=10)

        tk.Button(self.root,
                  text="Pitch bend OFF",
                  command=lambda: self.pitch_bend("off")).grid(row=4, column=8, padx=10)

        tk.Button(self.root,
                  text="Reset IDX",
                  command=self.reset_idx).grid(row=5, column=8, padx=10)

        self.frame_wobblers.grid(row=0, column=3, rowspan=5, columnspan=4)
        self.sample_frame.grid(row=22, column=4, sticky="we", rowspan=1, padx=2, pady=2)
        self.frame_scale_buttons.grid(row=5, column=3, rowspan=4, columnspan=3, padx=5, pady=0)
        self.frame_sliders.grid(row=30, column=3, sticky="wens", padx=10, pady=2, columnspan=3)
        self.frame_roots.grid(row=32, column=3, sticky="wens", padx=10, pady=2, columnspan=3)
        self.frame_prob_sliders.grid(row=31, column=3, sticky="wens", padx=10, pady=2, columnspan=3)
        self.frame_entries.grid(row=22, column=3, sticky="w", ipadx=2, ipady=2)
        self.frame_delay.grid(row=22+1, column=3, sticky="w", ipadx=2, ipady=2)

        self.scale_prob_skip_note.grid(row=23, column=3, columnspan=3)
        self.scale_vel_min.grid(column=0, row=0)
        self.scale_bpm.grid(row=24, column=3, sticky="wens", columnspan=3)
        self.scale_vel_max.grid(column=1, row=0)
        self.scale_prob_skip_poly.grid(column=2, row=0)
        self.scale_prob_skip_poly_relative.grid(column=3, row=0)
        self.scale_delay_multiplier.grid(column=10, row=10)

        init_row = 0
        self.entry_sequence.grid(row=0, column=5, sticky='wn', pady=1, padx=10)
        self.entry_memory_sequence.grid(row=init_row+1, column=5, sticky='wn', pady=1, padx=10)
        self.entry_str_seq.grid(row=init_row+3, column=5, sticky='wn', pady=1, padx=10)
        self.entry_off_array.grid(row=init_row+4, column=5, sticky='wn', pady=1, padx=10)
        self.entry_poly.grid(row=init_row+5, column=5, sticky='wn', pady=1, padx=10)
        self.entry_poly_relative.grid(row=init_row+6, column=5, sticky='wn', pady=1, padx=10)
        self.entry_skip_note_sequential.grid(row=init_row+7, column=5, sticky='wn', pady=1, padx=10)
        self.entry_skip_note_parallel.grid(row=init_row+8, column=5, sticky='wn', pady=1, padx=10)
        self.entry_octave_sequence.grid(row=init_row+9, column=5, sticky="wn", pady=1, padx=10)
        self.entry_root_sequence.grid(row=init_row+10, column=5, sticky="wn", pady=1, padx=10)
        self.entry_scale_sequence.grid(row=init_row+11, column=5, sticky="wn", pady=1, padx=10)
        self.entry_midi_channels.grid(row=init_row+12, column=5, sticky="wn", pady=1, padx=10)
        del init_row

        self.label_status_bar.grid(row=100, column=3, columnspan=3, pady=1, padx=10)
        self.label_main_seq_len.grid(row=0, column=6)
        self.label_main_seq_current_idx.grid(row=1, column=6)

        self.label_a.grid(row=0, column=2, sticky="w", padx=(10, 0), pady=1)
        self.label_a2.grid(row=1, column=2, sticky="w", padx=(10, 0), pady=1)
        self.label_b.grid(row=1+2, column=2, sticky="w", padx=(10, 0), pady=1)
        self.label_c.grid(row=2+2, column=2, sticky="w", padx=(10, 0), pady=1)
        self.label_d.grid(row=3+2, column=2, sticky="w", padx=(10, 0), pady=1)
        self.label_e.grid(row=4+2, column=2, sticky="w", padx=(10, 0), pady=1)
        self.label_f.grid(row=5+2, column=2, sticky="w", padx=(10, 0), pady=1)
        self.label_g.grid(row=6+2, column=2, sticky="w", padx=(10, 0), pady=1)
        self.label_h.grid(row=7+2, column=2, sticky="w", padx=(10, 0), pady=1)
        self.label_i.grid(row=8+2, column=2, sticky="w", padx=(10, 0), pady=1)
        self.label_j.grid(row=9+2, column=2, sticky="w", padx=(10, 0), pady=1)
        self.label_k.grid(row=10+2, column=2, sticky="w", padx=(10, 0), pady=1)

        self.check_delay_is_on.grid(row=11, column=10)

        self.option_midi_channel.grid(row=11-5, column=8, pady=1)
        self.option_midi_channel2.grid(row=11-4, column=8, pady=1)
        self.option_tempo_multiplier.grid(row=8, column=8)

        self.frame_memories.grid(row=22, column=5, sticky="we", padx=2, pady=1)
        for i, mem in enumerate(self.memories):
            mem.show()
            mem.grid()

        self.display_wobblers()
        self.sample_frame.display()
        self.root.mainloop()

    def display_wobblers(self):
        abc = 0
        for wob in self.wobblers:
            wob.grid(row=0, column=abc, padx=3, pady=5)
            wob.display()

            thread_wobbler = threading.Thread(target=wob.wobble)
            thread_wobbler.daemon = True
            self.threads.append(thread_wobbler)
            thread_wobbler.start()
            abc += 1

    def set_current_note_idx(self, idx):
        self.strvar_main_seq_current_idx.set(str(idx + 1))

    def reset_idx(self):
        self.actual_notes_played_count = 0
        self.set_current_note_idx(self.actual_notes_played_count)
        log(logfile=self.context.logfile, msg="actual_notes_played_count was RESET.")

    def set_sequence(self, _, mode=None):
        parser = self.context.parser
        text_ = str(self.entry_sequence.get())

        if mode is None:
            log(logfile=self.context.logfile, msg="\"%s\"" % text_)
            notes, str_seq = parser.get_notes(self.context, text_)
            self.context.str_sequence = str_seq

        elif mode is self.context.set_sequence_modes.dont_regenerate:
            # log(logfile=self.context.logfile, msg="self.context.str_sequence is %s" % self.context.str_sequence)
            notes, str_seq = parser.get_notes(self.context, self.context.str_sequence.replace(" ", ""))

        self.context.sequence = notes
        self.entry_str_seq.delete(0, tk.END)
        self.entry_str_seq.insert(0, self.context.str_sequence)

        self.strvar_main_seq_len.set(str(self.context.sequence.__len__()))

    def set_memory_sequence(self, _):
        parser = self.context.parser
        text_ = str(self.entry_memory_sequence.get())
        self.context.str_sequence = ""

        result = parser.parse_memory_sequence(text_)

        running_seq = []

        prev = None
        prev_notes = None
        prev_str_seq = None
        for idx in result:
            str_seq = self.memories[0].get_by_index(idx)

            if prev == idx and prev is not None:
                notes = prev_notes
                str_seq = prev_str_seq

            else:
                if str_seq is not None:
                    notes, str_seq = parser.get_notes(self.context, str_seq)
                else:
                    notes, str_seq = [], ""

            running_seq += notes
            self.context.str_sequence += str_seq

            prev = idx
            prev_notes = notes
            prev_str_seq = str_seq

        self.entry_str_seq.delete(0, tk.END)
        self.entry_str_seq.insert(0, self.context.str_sequence)
        self.context.memory_sequences["main melody"] = running_seq
        self.context.sequence = running_seq

        log(logfile=self.context.logfile, msg="Sequence set to: %s" % running_seq)

    def add_seq_to_memory(self, typ):
        text_ = str(self.entry_sequence.get())
        self.memories[0].add_seq(text_)

    def set_root_sequence(self, _):
        parser = self.context.parser
        text = self.entry_root_sequence.get()

        individual_sequences = parser.parse_multiple_sequences_separated(
            separator=self.string_constants.multiple_entry_separator,
            sequences=text)

        self.context.root_sequences = [parser.parse_root_sequence(seq) for seq in individual_sequences]
        self.context.root_sequence = self.context.root_sequences[0]

        log(logfile=self.context.logfile, msg="Root sequences set to: %s" % self.context.root_sequences)

    def set_octave_sequence(self, _):
        parser = self.context.parser
        text = self.entry_octave_sequence.get()

        individual_sequences = parser.parse_multiple_sequences_separated(
            separator=self.string_constants.multiple_entry_separator,
            sequences=text)

        self.context.octave_sequences = [parser.parse_octave_sequence(seq) for seq in individual_sequences]
        self.context.octave_sequence = self.context.octave_sequences[0]

        log(logfile=self.context.logfile, msg="Octave sequences set to: %s" % self.context.octave_sequences)

    def set_scale_sequence(self, _):
        parser = self.context.parser
        text = self.entry_scale_sequence.get()

        individual_sequences = parser.parse_multiple_sequences_separated(
            separator=self.string_constants.multiple_entry_separator,
            sequences=text)

        self.context.scale_sequences = [parser.parse_scale_sequence(self.context, seq) for seq in individual_sequences]
        self.context.scale_sequence = self.context.scale_sequences[0]

        log(logfile=self.context.logfile, msg="Scale sequences set to: %s" % self.context.scale_sequences)

    def set_poly(self, _):
        parser = self.context.parser
        text = self.entry_poly.get()

        individual_sequences = parser.parse_multiple_sequences_separated(
            separator=self.string_constants.multiple_entry_separator,
            sequences=text)

        self.context.poly_sequences = [list(map(int, voices.split())) for voices in individual_sequences]
        self.context.poly = self.context.poly_sequences[0]

        log(logfile=self.context.logfile, msg="Poly: %s" % self.context.poly_sequences)

    def set_poly_relative(self, _):
        parser = self.context.parser
        text = self.entry_poly_relative.get()

        individual_sequences = parser.parse_multiple_sequences_separated(
            separator=self.string_constants.multiple_entry_separator,
            sequences=text)

        self.context.poly_relative_sequences = [list(map(int, voices.split())) for voices in individual_sequences]
        self.context.poly_relative = self.context.poly_relative_sequences[0]

        log(logfile=self.context.logfile, msg="Poly relative: %s" % self.context.poly_relative_sequences)

    def set_skip_note_parallel(self, _):
        parser = self.context.parser
        text = self.entry_skip_note_parallel.get()

        individual_sequences = parser.parse_multiple_sequences_separated(
            separator=self.string_constants.multiple_entry_separator,
            sequences=text)

        self.context.skip_note_parallel_sequences = [list(map(int, skips.split())) for skips in individual_sequences]
        self.context.skip_notes_parallel = self.context.skip_note_parallel_sequences[0]

        log(logfile=self.context.logfile, msg="Skip notes parallel: %s" % self.context.skip_note_parallel_sequences)

    def set_skip_note_sequential(self, _):
        parser = self.context.parser
        text = self.entry_skip_note_sequential.get()

        individual_sequences = parser.parse_multiple_sequences_separated(
            separator=self.string_constants.multiple_entry_separator,
            sequences=text)

        self.context.skip_notes_sequential_sequences = [list(map(int, skips.split())) for skips in individual_sequences]
        self.context.skip_notes_sequential = self.context.skip_notes_sequential_sequences[0]

        log(logfile=self.context.logfile, msg="Skip notes sequential: %s" % self.context.skip_notes_sequential_sequences)

    def set_scale(self, scale_):
        self.context.scale = self.context.scales.get_scale_by_name(scale_)
        log(logfile=self.context.logfile, msg="Scale: %s" % self.context.scales.get_display_scale_name(scale_))
        self.strvar_status_bar.set("%s --- %s" % (self.context.scales.get_display_scale_name(scale_), self.context.scale))
        # self.end_all_notes()

    def set_off_array(self, _):
        parser = self.context.parser
        text = self.entry_off_array.get()

        individual_sequences = parser.parse_multiple_sequences_separated(
            separator=self.string_constants.multiple_entry_separator,
            sequences=text)

        parsed_individual_sequences = [parser.parse_off_array(seq) for seq in individual_sequences]
        self.context.off_sequences = parsed_individual_sequences
        self.context.off_list = parsed_individual_sequences[0]

        log(logfile=self.context.logfile, msg="Off lists: %s" % self.context.off_sequences)

    def set_midi_channels(self, _):
        parser = self.context.parser
        text = self.entry_midi_channels.get()

        individual_sequences = parser.parse_multiple_sequences_separated(
            separator=self.string_constants.multiple_entry_separator,
            sequences=text)

        parsed_individual_sequences = [parser.parse_midi_channels(seq) for seq in individual_sequences]
        self.context.midi_channels = parsed_individual_sequences

        log(logfile=self.context.logfile, msg="MIDI Channels: %s" % self.context.midi_channels)

    def stop_sequence(self):
        self.context.playback_on = False
        log(logfile=self.context.logfile, msg="Sequence stopped.")

    def start_sequence(self):
        self.context.playback_on = True
        log(logfile=self.context.logfile, msg="Sequence started.")

    def end_all_notes(self):
        msg = [0b10110000 + int(self.strvar_option_midi_channel.get()) - 1, 123, 0]
        self.context.midi.send_message(msg)
        # log(logfile=self.context.logfile, msg="All notes off.")

    def pitch_bend(self, what):
        if what == "on":
            msg = [0b11100000 + int(self.strvar_option_midi_channel.get()) - 1, 0x00, 0x60]
        elif what == "off":
            msg = [0b11100000 + int(self.strvar_option_midi_channel.get()) - 1, 0b0, 0b1000000]

        self.context.midi.send_message(msg)
        log(logfile=self.context.logfile, msg="Pitch bend sent.")

    def get_velocity_min_max(self):
        slider_min = int(self.strvar_vel_min.get())
        slider_max = int(self.strvar_vel_max.get())

        vel_min = slider_min if slider_min < slider_max else slider_max
        vel_max = slider_max if slider_max > slider_min else slider_min

        return vel_min, vel_max

    def skip_note_parallel(self, idx):
        if self.context.skip_notes_parallel:
            for i in range(0, self.context.skip_notes_parallel.__len__()):
                if (idx // self.get_tempo_multiplier()) % (self.context.skip_notes_parallel[i] + 1) == 0:
                    return True

    def skip_note_sequentially(self, skip_sequential_idx, idx_sequential_skip):
        if self.context.skip_notes_sequential:
            loop_skip_sequential_idx = skip_sequential_idx % len(self.context.skip_notes_sequential)

            if idx_sequential_skip % (self.context.skip_notes_sequential[loop_skip_sequential_idx]) == 0:
                if idx_sequential_skip > 0:
                    return skip_sequential_idx + 1, 0, True
        return skip_sequential_idx, idx_sequential_skip, False

    def play_poly_notes(self, note):
        if self.context.poly:
            for poly in self.context.poly:
                if a() < int(self.strvar_prob_skip_poly.get()) / 100.0:
                    self.context.midi.send_message([note[0], note[1] + poly, note[2]])

    def play_relative_poly_notes(self, note, note_entry):
        scale = self.context.scale
        scales = self.context.scales

        if self.context.poly_relative:
            for poly in self.context.poly_relative:
                if a() < int(self.strvar_prob_skip_poly_relative.get()) / 100.0:
                    # THIS TOOK FUCKING FOREVER TO FIGURE OUT
                    added = (scales.get_note_by_index_wrap(note_entry + poly, scale)
                             - scales.get_note_by_index_wrap(note_entry, scale))
                    self.context.midi.send_message([note[0], note[1] + added, note[2]])

    def play_sample_notes(self, idx):
        for channel, sample_seq in enumerate(self.context.sample_seqs):
            if sample_seq:
                sample_idx = idx % len(sample_seq)
                # log(logfile=self.context.logfile, msg="Sample_idx: %s" % sample_idx)

                step = (idx - 1) % len(sample_seq)
                self.sample_frame.update_label_with_current_step(channel, step, sample_seq[step])

                if sample_seq[sample_idx]:
                    self.context.midi.send_message(sample_seq[sample_idx])

    def get_delay_multiplier(self):
        return float(self.context.get_delay_multiplier())

    def get_orig_note(self, note, octave_idx):
        vel_min, vel_max = self.get_velocity_min_max()
        octave_offset = 0 if not self.context.octave_sequence else self.context.octave_sequence[octave_idx]

        orig_note = copy.copy(note)
        orig_note[0] += int(self.strvar_option_midi_channel.get()) - 1
        orig_note[1] += self.context.root - c2 - 4 + octave_offset
        orig_note[2] = random.randint(vel_min, vel_max)

        return orig_note

    def turn_off_notes(self, off_note_idx, idx_all_off):
        if self.context.off_list:
            loop_off_note_idx = off_note_idx % len(self.context.off_list)

            # TODO - fix integer modulo by 0
            if idx_all_off % (self.context.off_list[loop_off_note_idx]) == 0:
                if idx_all_off > 0:
                    self.end_all_notes()
                    return off_note_idx + 1, 0

        return off_note_idx, idx_all_off

    def play_midi_notes(self):
        valid_midi_channels = [channel for channel in self.context.midi_channels if channel]

        for valid_channel in valid_midi_channels:
            pass

    def play_sequence(self):
        log(logfile=self.context.logfile, msg="Play sequence is running.")
        # mc = MidiClock(self.context)

        idx_all_off = 0
        off_note_idx = 0

        skip_sequential_idx = 0
        idx_sequential_skip = 0

        ########################################################
        ########################################################
        ################    M A I N   L O O P   ################
        ########################################################
        ########################################################

        while True:
            self.idx += 1

            if not self.context.playback_on:
                time.sleep(0.02)
                continue

            if self.context.sequence:
                if (a() > float(self.context.prob_skip_note.get())/100
                        and self.idx % self.get_tempo_multiplier() == 0):

                    loop_idx = self.actual_notes_played_count % len(self.context.sequence)

                    # TODO make this a function
                    try:
                        octave_idx = self.actual_notes_played_count % len(self.context.octave_sequence)
                    except:
                        octave_idx = 0

                    # TODO make this a function
                    try:
                        root_idx = self.actual_notes_played_count % len(self.context.root_sequence)

                        if self.context.root_sequence[root_idx] != self.context.root:
                            self.end_all_notes()
                            self.context.root = self.context.root_sequence[root_idx]

                            log(logfile=self.context.logfile, msg="Root changed to: %s" % self.context.root_sequence[root_idx])
                    except:
                        pass

                    # TODO make this a function
                    try:
                        sc = self.context.scales
                        scale_idx = self.actual_notes_played_count % len(self.context.scale_sequence)

                        if self.context.scale != sc.get_scale_by_name(self.context.scale_sequence[scale_idx]):
                            self.end_all_notes()
                            self.context.scale = sc.get_scale_by_name(self.context.scale_sequence[scale_idx])
                            self.set_sequence(None, self.context.set_sequence_modes.dont_regenerate)

                            log(logfile=self.context.logfile, msg="Scale changed to: %s" % self.context.scale_sequence[scale_idx])

                    except:
                        pass

                    try:
                        note = self.context.sequence[loop_idx]
                    except:
                        time.sleep(0.02)
                        continue

                    orig_note = self.get_orig_note(note, octave_idx)

                    self.set_current_note_idx(loop_idx)

                    off_note_idx, idx_all_off = self.turn_off_notes(off_note_idx, idx_all_off)

                    skip_sequential_idx, idx_sequential_skip, skip_sequentially = \
                        self.skip_note_sequentially(skip_sequential_idx, idx_sequential_skip)

                    if note[1] == NOTE_PAUSE:
                        self.actual_notes_played_count += 1

                    if note[1] != NOTE_PAUSE:
                        if note[1] == GO_TO_START:
                            # -1 because right at the start of while True there is idx += 1
                            self.idx = -1
                            self.actual_notes_played_count = 0
                            continue

                        elif not self.skip_note_parallel(self.idx) and not skip_sequentially:
                            self.context.midi.send_message(orig_note)

                            if self.delay_is_on():
                                x = lambda: self.d.run_delay_with_note(orig_note,
                                                                       60 / self.bpm / self.get_delay_multiplier(),
                                                                       self.df.functions[self.dc.CONSTANT_DECAY], -10)

                                Delay(self.context).create_thread_for_function(x)

                            self.actual_notes_played_count += 1
                            idx_sequential_skip += 1
                            idx_all_off += 1

                            self.play_poly_notes(orig_note)

                            try:
                                param = int(self.entry_str_seq.get().split()[loop_idx][0])
                                self.play_relative_poly_notes(orig_note, param)

                            except Exception as e:
                                log(logfile=self.context.logfile, msg="There was this exception: %s" % e)

            self.play_sample_notes(self.idx)

            sleep_time = NoteLengths(float(self.context.bpm.get())).eigtht
            time.sleep(sleep_time)
