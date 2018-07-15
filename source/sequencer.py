import tkinter as tk
from tkinter import filedialog
from collections import OrderedDict
import threading
import time
import copy
import random
import os

from source.note_object import NoteLengthsOld, NoteTypes, NoteSchedulingObject, convert_midi_notes_to_note_objects, NoteContainer
from source.context import Context
from source.wobbler import Wobbler
from source.constants import *
from source.sample_frame import SampleFrame
from source.delay import Delay
from source.helpful_functions import a
from source.functions import log, get_date_string, insert_into_entry
from source.memory import Memory
from source.internal_state import InternalState
from source.midi_input_listener import MIDIInputListener
from source.status_frame import StatusFrame


class Sequencer(tk.Frame):
    def __init__(self, midi_):
        self.root = tk.Tk()
        tk.Frame.__init__(self, self.root, bg="darkblue", padx=2, pady=2)

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.root.title("MIDI Sequencer")
        self.root["bg"] = "black"
        self.root.geometry('+0+0')

        self.threads = []

        self.frame_delay = tk.Frame(self.root)
        self.frame_delay["bg"] = "yellow"
        self.strvar_delay_multiplier = tk.StringVar(self.frame_delay)
        self.scale_delay_multiplier = tk.Scale(self.frame_delay, from_=.1, to=10., orient=tk.HORIZONTAL,
                                               sliderlength=30, resolution=.1,
                                               variable=self.strvar_delay_multiplier, length=500)

        self.intvar_checkbox_state = tk.IntVar(self.root)
        self.check_delay_is_on = tk.Checkbutton(self.frame_delay,
                                                text="D e  l   a    y      o  n ?",
                                                variable=self.intvar_checkbox_state)
        self.delay_is_on = lambda: True if self.intvar_checkbox_state.get() == 1 else False

        self.context = Context(self.root, self)
        self.context.root = e2
        self.context.mode = MODE_SIMPLE
        self.context.scale = None
        self.context.playback_on = False

        self.midi_input_listener = MIDIInputListener(sequencer=self,
                                                     context=self.context,
                                                     input_name=StringConstants.AKAI_MIDIMIX_NAME,
                                                     interval=SleepTimes.MIDI_INPUT_MAINLOOP)
        self.frame_memories = tk.Frame(self.root)
        self.memories = []
        self.memories.append(Memory(self.frame_memories, self.context, MemoryType().melody))

        self.frame_channel_enable = tk.Frame(self.root)
        self.frame_channel_enable.grid(row=23, column=4, rowspan=2)
        self.checkboxes_enable_channels = []
        self.intvars_enable_channels = []

        for i in range(NumberOf.CHANNEL_CHECKBOXES):
            self.intvars_enable_channels.append(tk.IntVar(self.root, ENABLED))
            self.checkboxes_enable_channels.append(tk.Checkbutton(self.frame_channel_enable,
                                                                  text="Ch%s" % i,
                                                                  variable=self.intvars_enable_channels[-1]))
            self.checkboxes_enable_channels[i].grid(row=0, column=i)
        self.intvar_solo = tk.IntVar(self.root, DISABLED)
        self.checkbox_solo = tk.Checkbutton(self.frame_channel_enable,
                                            text="Solo",
                                            variable=self.intvar_solo)
        self.checkbox_solo.grid(row=0, column=NumberOf.CHANNEL_CHECKBOXES)

        self.idx_all_off = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.off_note_idx = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.skip_sequential_idx = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.idx_sequential_skip = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

        self.set_sequence_modes = SetSequenceModes()

        self.idx = 0
        self.step_played_counts = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.actual_notes_played_counts = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

        self.frame_status = StatusFrame(parent=self.root, sequencer=self)
        self.context.midi = midi_
        self.bpm = self.context.get_bpm()

        self.delay = Delay(self.context)
        self.delay_functions = DelayFunctions()
        self.delay_constants = DelayConstants()

        self.labels_entry_names = []
        self.entry_names = []

        self.wobbler_count = 6
        self.frame_wobblers = tk.Frame(self.root, bg="black")
        self.wobblers = [Wobbler(self.frame_wobblers, self.context, "Keys wobbler %s" % i)
                         for i in range(self.wobbler_count)]

        self.sample_frame = SampleFrame(self.root, self.context)

        self.frame_buttons = tk.Frame(self.root)
        self.frame_entries = tk.Frame(self.root)
        self.frame_entries["bg"] = "purple"
        self.frame_scale_buttons = tk.Frame(self.root)
        self.frame_sliders = tk.Frame(self.root)
        self.frame_roots = tk.Frame(self.root)
        self.frame_prob_sliders = tk.Frame(self.root)

        self.strvar_tempo_multiplier = tk.StringVar(self.frame_buttons, "1")
        self.option_tempo_multiplier = tk.OptionMenu(self.frame_buttons, self.strvar_tempo_multiplier, *[x for x in range(1, 9)])
        self.get_tempo_multiplier = lambda: int(self.strvar_tempo_multiplier.get())

        label_font = ("Courier", "11")
        self.strvar_status_bar = tk.StringVar(self.root, "")
        self.label_status_bar = tk.Label(self.root, textvariable=self.strvar_status_bar, font=label_font)

        self.strvar_main_seq_len = tk.StringVar(self.frame_entries)
        self.label_main_seq_len = tk.Label(self.frame_entries, textvariable=self.strvar_main_seq_len,
                                           font=label_font, width=4)

        self.strvar_main_seq_current_idx = tk.StringVar(self.frame_entries, "")
        self.label_main_seq_current_idx = tk.Label(self.frame_entries, textvariable=self.strvar_main_seq_current_idx,
                                                   font=label_font, width=4)

        self.velocities_scale_min = []
        self.velocities_scale_max = []
        self.velocities_strvars_min = []
        self.velocities_strvars_max = []
        self.strvars_prob_skip_note = []
        self.scales_prob_skip_note = []
        self.strvars_prob_poly_abs = []
        self.strvars_prob_poly_rel = []
        self.scales_prob_poly_abs = []
        self.scales_prob_poly_rel = []

        self.create_prob_sliders()

        self.scale_bpm = tk.Scale(self.frame_sliders, from_=Ranges.BPM_MIN, to=Ranges.BPM_MAX, orient=tk.HORIZONTAL,
                                  sliderlength=30, variable=self.context.bpm, length=500)

        self.label_a = tk.Label(self.frame_entries, font=label_font,
                                text="Main Sequence".ljust(InitialValues.MAIN_LABEL_JUST), height=1)
        self.label_a2 = tk.Label(self.frame_entries, font=label_font,
                                 text="Memory Sequence".ljust(InitialValues.MAIN_LABEL_JUST), height=1)
        self.label_a3 = tk.Label(self.frame_entries, font=label_font,
                                 text="Scheduling Sequence".ljust(InitialValues.MAIN_LABEL_JUST), height=1)
        self.label_b = tk.Label(self.frame_entries, font=label_font,
                                text="Main Seq Repr".ljust(InitialValues.MAIN_LABEL_JUST), height=1)
        self.label_c = tk.Label(self.frame_entries, font=label_font,
                                text="Stop Notes".ljust(InitialValues.MAIN_LABEL_JUST), height=1)
        self.label_d = tk.Label(self.frame_entries, font=label_font,
                                text="Polyphony".ljust(InitialValues.MAIN_LABEL_JUST), height=1)
        self.label_e = tk.Label(self.frame_entries, font=label_font,
                                text="Polyphony Relative".ljust(InitialValues.MAIN_LABEL_JUST), height=1)
        self.label_f = tk.Label(self.frame_entries, font=label_font,
                                text="Skip Notes Seq".ljust(InitialValues.MAIN_LABEL_JUST), height=1)
        self.label_g = tk.Label(self.frame_entries, font=label_font,
                                text="Skip Notes Par".ljust(InitialValues.MAIN_LABEL_JUST), height=1)
        self.label_h = tk.Label(self.frame_entries, font=label_font,
                                text="Octave Sequence".ljust(InitialValues.MAIN_LABEL_JUST), height=1)
        self.label_i = tk.Label(self.frame_entries, font=label_font,
                                text="Root Sequence".ljust(InitialValues.MAIN_LABEL_JUST), height=1)
        self.label_j = tk.Label(self.frame_entries, font=label_font,
                                text="Scale Sequence".ljust(InitialValues.MAIN_LABEL_JUST), height=1)
        self.label_k = tk.Label(self.frame_entries, font=label_font,
                                text="MIDI Channels".ljust(InitialValues.MAIN_LABEL_JUST), height=1)

        self.thread_seq = threading.Thread(target=self.play_sequence, args=())
        self.thread_seq.daemon = True
        self.threads.append(self.thread_seq)
        self.thread_seq.start()

        roots = [(c2, "C"), (cs2, "C#"), (d2, "D"), (ds2, "Eb"),
                 (e2, "E"), (f2, "F"), (fs2, "F#",), (g2, "G"),
                 (gs2, "G#"), (a2, "A"), (as2, "Bb"), (b2, "B")]

        def set_root(root):
            self.context.root = root

        row_ = 0
        col_ = 0
        for root in roots:
            tk.Button(self.frame_roots,
                      text=root[1],
                      command=lambda x=root[0]: set_root(x)).grid(row=row_, column=col_)
            col_ += 1

        button_font = ("Courier", "8")
        row_ = 0
        col_ = 0
        for scale in self.context.scales.get_all():
            scale_name = self.context.scales.get_display_scale_name(scale)

            tk.Button(self.frame_scale_buttons,
                      text=scale_name,
                      width=18,
                      height=1,
                      font=button_font,
                      command=lambda y=scale: self.set_scale(y)).grid(
                row=row_, column=(col_ % InitialValues.SCALE_BUTTONS_WRAP), sticky="nsew")
            col_ += 1

            if col_ % InitialValues.SCALE_BUTTONS_WRAP == 0:
                row_ += 1
                col_ = 0

        self.entry_str_seq = tk.Entry(self.frame_entries, width=InitialValues.MAIN_ENTRY_WIDTH)
        self.entry_sequence = tk.Entry(self.frame_entries, width=InitialValues.MAIN_ENTRY_WIDTH)
        self.entry_sequence.bind('<Return>', self.set_sequence)
        self.entry_sequence.bind('<Control-Return>', lambda typ=MemoryType().melody: self.add_seq_to_memory(typ))
        self.entry_sequence.delete(0, tk.END)

        self.entry_memory_sequence = tk.Entry(self.frame_entries, width=InitialValues.MAIN_ENTRY_WIDTH)
        self.entry_memory_sequence.bind('<Return>', self.set_memory_sequence)

        self.entry_note_scheduling = tk.Entry(self.frame_entries, width=InitialValues.MAIN_ENTRY_WIDTH)
        self.entry_note_scheduling.bind('<Return>', self.set_note_scheduling_sequence)

        self.entry_off_array = tk.Entry(self.frame_entries, width=InitialValues.MAIN_ENTRY_WIDTH)
        self.entry_off_array.bind('<Return>', self.set_off_array)

        self.entry_poly = tk.Entry(self.frame_entries, width=InitialValues.MAIN_ENTRY_WIDTH)
        self.entry_poly.bind('<Return>', self.set_poly_absolute)

        self.entry_poly_relative = tk.Entry(self.frame_entries, width=InitialValues.MAIN_ENTRY_WIDTH)
        self.entry_poly_relative.bind('<Return>', self.set_poly_relative)

        self.entry_skip_note_parallel = tk.Entry(self.frame_entries, width=InitialValues.MAIN_ENTRY_WIDTH)
        self.entry_skip_note_parallel.bind('<Return>', self.set_skip_note_parallel)

        self.entry_skip_note_sequential = tk.Entry(self.frame_entries, width=InitialValues.MAIN_ENTRY_WIDTH)
        self.entry_skip_note_sequential.bind('<Return>', self.set_skip_note_sequential)

        self.entry_root_sequence = tk.Entry(self.frame_entries, width=InitialValues.MAIN_ENTRY_WIDTH)
        self.entry_root_sequence.bind('<Return>', self.set_root_sequence)

        self.entry_octave_sequence = tk.Entry(self.frame_entries, width=InitialValues.MAIN_ENTRY_WIDTH)
        self.entry_octave_sequence.bind('<Return>', self.set_octave_sequence)

        self.entry_scale_sequence = tk.Entry(self.frame_entries, width=InitialValues.MAIN_ENTRY_WIDTH)
        self.entry_scale_sequence.bind('<Return>', self.set_scale_sequence)

        self.entry_midi_channels = tk.Entry(self.frame_entries, width=InitialValues.MAIN_ENTRY_WIDTH)
        self.entry_midi_channels.bind('<Return>', self.set_midi_channels)

        self.entry_boxes = [self.entry_off_array, self.entry_poly, self.entry_poly_relative, self.entry_memory_sequence,
                            self.entry_note_scheduling, self.entry_skip_note_parallel, self.entry_skip_note_sequential,
                            self.entry_midi_channels, self.entry_root_sequence, self.entry_octave_sequence,
                            self.entry_scale_sequence]

        self.entry_boxes_names = ["off array", "poly", "poly_relative", "memory_seq", "note_scheduling",
                                  "skip_par", "skip_seq", "midi_channels", "root_seq", "octave_seq", "scale_seq"]

        insert_into_entry(self.entry_midi_channels, " 15 | 11 | 10 | 11 | 11 | 11 | 13 ")
        self.init_entries()

    def create_prob_sliders(self):
        for i in range(NumberOf.VELOCITY_SLIDERS):
            self.velocities_strvars_min.append(tk.StringVar(self.frame_prob_sliders))
            self.velocities_strvars_min[-1].set(InitialValues.VELOCITY_MIN)
            self.velocities_scale_min.append(tk.Scale(self.frame_prob_sliders,
                                                      from_=Ranges.MIDI_MAX, to=Ranges.MIDI_MIN,
                                                      orient=tk.VERTICAL,
                                                      variable=self.velocities_strvars_min[i],
                                                      length=InitialValues.VELOCITY_SLIDER_LEN))

            self.velocities_strvars_max.append(tk.StringVar(self.frame_prob_sliders))
            self.velocities_strvars_max[-1].set(InitialValues.VELOCITY_MAX)
            self.velocities_scale_max.append(tk.Scale(self.frame_prob_sliders,
                                                      from_=Ranges.MIDI_MAX, to=Ranges.MIDI_MIN,
                                                      orient=tk.VERTICAL,
                                                      variable=self.velocities_strvars_max[i],
                                                      length=InitialValues.VELOCITY_SLIDER_LEN))

        for i in range(NumberOf.PROB_SKIP_NOTE_SLIDERS):
            self.strvars_prob_skip_note.append(tk.StringVar(self.frame_prob_sliders))
            self.scales_prob_skip_note.append(tk.Scale(self.frame_prob_sliders,
                                                       from_=Ranges.PERC_MAX, to=Ranges.PERC_MIN,
                                                       orient=tk.VERTICAL, sliderlength=30,
                                                       variable=self.strvars_prob_skip_note[-1],
                                                       length=InitialValues.SKIP_NOTE_SLIDER_LEN))

        for i in range(NumberOf.POLYPHONY_SLIDERS):
            self.strvars_prob_poly_abs.append(tk.StringVar(self.frame_prob_sliders))
            self.strvars_prob_poly_rel.append(tk.StringVar(self.frame_prob_sliders))
            self.strvars_prob_poly_abs[-1].set(InitialValues.PROB_POLY)
            self.strvars_prob_poly_rel[-1].set(InitialValues.PROB_POLY)

            self.scales_prob_poly_abs.append(tk.Scale(self.frame_prob_sliders,
                                                      from_=Ranges.PERC_MAX, to=Ranges.PERC_MIN,
                                                      orient=tk.VERTICAL, sliderlength=30,
                                                      variable=self.strvars_prob_poly_abs[-1],
                                                      length=InitialValues.POLY_SLIDER_LEN))

            self.scales_prob_poly_rel.append(tk.Scale(self.frame_prob_sliders,
                                                      from_=Ranges.PERC_MAX, to=Ranges.PERC_MIN,
                                                      orient=tk.VERTICAL, sliderlength=30,
                                                      variable=self.strvars_prob_poly_rel[-1],
                                                      length=InitialValues.POLY_SLIDER_LEN))

        self.velocities_scale_max[-1]["label"] = "Vel"
        self.scales_prob_skip_note[-1]["label"] = "Skip"
        self.scales_prob_poly_abs[-1]["label"] = "Abs"
        self.scales_prob_poly_rel[-1]["label"] = "Rel"

    def on_closing(self):
        log(msg="Window will be destroyed.")
        self.end_all_notes()
        self.root.quit()
        self.root.destroy()

    def show(self):
        tk.Button(self.frame_buttons,
                  text="Start sequence".center(InitialValues.CENTER_JUST_BUTTON),
                  font=("Courier", "8"),
                  command=self.start_sequence).grid(row=0, column=8, padx=0)

        tk.Button(self.frame_buttons,
                  text="Stop sequence".center(InitialValues.CENTER_JUST_BUTTON),
                  font=("Courier", "8"),
                  command=self.stop_sequence).grid(row=1, column=8, padx=0)

        tk.Button(self.frame_buttons,
                  text="All notes off".center(InitialValues.CENTER_JUST_BUTTON),
                  font=("Courier", "8"),
                  command=self.end_all_notes).grid(row=2, column=8, padx=0)

        tk.Button(self.frame_buttons,
                  text="Pitch bend ON".center(InitialValues.CENTER_JUST_BUTTON),
                  font=("Courier", "8"),
                  command=lambda: self.pitch_bend("on")).grid(row=3, column=8, padx=0)

        tk.Button(self.frame_buttons,
                  text="Pitch bend OFF".center(InitialValues.CENTER_JUST_BUTTON),
                  font=("Courier", "8"),
                  command=lambda: self.pitch_bend("off")).grid(row=4, column=8, padx=0)

        tk.Button(self.frame_buttons,
                  text="Reset IDX".center(InitialValues.CENTER_JUST_BUTTON),
                  font=("Courier", "8"),
                  command=self.reset_idx).grid(row=5, column=8, padx=0)

        tk.Button(self.frame_buttons,
                  text="I N I T".center(InitialValues.CENTER_JUST_BUTTON),
                  font=("Courier", "8"),
                  command=self.init_entries).grid(row=12, column=8, padx=0)

        tk.Button(self.frame_buttons,
                  text="E N T E R".center(InitialValues.CENTER_JUST_BUTTON),
                  font=("Courier", "8"),
                  command=self.press_all_enters).grid(row=13, column=8, padx=0)

        tk.Button(self.frame_buttons,
                  text="Save state".center(InitialValues.CENTER_JUST_BUTTON),
                  font=("Courier", "8"),
                  command=self.save_internal_state).grid(row=14, column=8, padx=0)

        tk.Button(self.frame_buttons,
                  text="Load state".center(InitialValues.CENTER_JUST_BUTTON),
                  font=("Courier", "8"),
                  command=self.load_internal_state).grid(row=15, column=8, padx=0)

        tk.Button(self.frame_buttons,
                  text="M U T E".center(InitialValues.CENTER_JUST_BUTTON),
                  font=("Courier", "8"),
                  command=self.mute_all).grid(row=16, column=8, padx=0)

        tk.Button(self.frame_buttons,
                  text="U N - M U T E".center(InitialValues.CENTER_JUST_BUTTON),
                  font=("Courier", "8"),
                  command=self.unmute_all).grid(row=17, column=8, padx=0)

        tk.Button(self.frame_buttons,
                  text="I N V E R T".center(InitialValues.CENTER_JUST_BUTTON),
                  font=("Courier", "8"),
                  command=self.invert_mute).grid(row=18, column=8, padx=0)

        self.frame_wobblers.grid(row=0, column=3, rowspan=1, columnspan=4)
        self.frame_buttons.grid(row=0, column=30, rowspan=20)
        self.sample_frame.grid(row=22, column=4, sticky="we", rowspan=1, padx=2, pady=2)
        self.frame_scale_buttons.grid(row=1, column=3, rowspan=1, columnspan=3, padx=5, pady=0)
        self.frame_sliders.grid(row=30, column=3, sticky="wens", padx=10, pady=2, columnspan=3)
        self.frame_roots.grid(row=32, column=3, sticky="wens", padx=10, pady=2, columnspan=3)
        self.frame_prob_sliders.grid(row=31, column=3, sticky="wens", padx=10, pady=2, columnspan=3)
        self.frame_entries.grid(row=22, column=3, sticky="w", ipadx=2, ipady=2, columnspan=1)
        self.frame_delay.grid(row=22+1, column=3, sticky="w", ipadx=2, ipady=2)
        self.frame_status.grid(row=21, column=30, sticky="w", ipadx=2, ipady=2, rowspan=20)

        for i in range(NumberOf.VELOCITY_SLIDERS):
            self.velocities_scale_min[i].grid(column=i*2, row=0)
            self.velocities_scale_max[i].grid(column=i*2+1, row=0)

        for i in range(NumberOf.PROB_SKIP_NOTE_SLIDERS):
            self.scales_prob_skip_note[i].grid(row=0, column=NumberOf.VELOCITY_SLIDERS*2 + i)

        for i in range(NumberOf.POLYPHONY_SLIDERS):
            col = NumberOf.VELOCITY_SLIDERS*2 + NumberOf.PROB_SKIP_NOTE_SLIDERS + i
            self.scales_prob_poly_abs[i].grid(row=0, column=col)

        for i in range(NumberOf.POLYPHONY_SLIDERS):
            col = NumberOf.VELOCITY_SLIDERS*2 + NumberOf.PROB_SKIP_NOTE_SLIDERS + NumberOf.POLYPHONY_SLIDERS + i
            self.scales_prob_poly_rel[i].grid(row=0, column=col)

        self.scale_bpm.grid(row=24, column=3, sticky="wens", columnspan=3)
        self.scale_delay_multiplier.grid(column=10, row=10)

        self.entry_names = [self.entry_sequence, self.entry_memory_sequence, self.entry_note_scheduling,
                            self.entry_str_seq, self.entry_off_array, self.entry_poly, self.entry_poly_relative,
                            self.entry_skip_note_sequential, self.entry_skip_note_parallel, self.entry_octave_sequence,
                            self.entry_root_sequence, self.entry_scale_sequence, self.entry_midi_channels]

        for i, entry_name in enumerate(self.entry_names):
            entry_name.grid(row=i, column=5, sticky='wn', pady=1, padx=10)

        self.label_status_bar.grid(row=100, column=3, columnspan=3, pady=1, padx=10)
        self.label_main_seq_len.grid(row=0, column=6)
        self.label_main_seq_current_idx.grid(row=1, column=6)

        self.labels_entry_names = [self.label_a, self.label_a2, self.label_a3, self.label_b, self.label_c,
                                   self.label_d, self.label_e, self.label_f, self.label_g, self.label_h, self.label_i,
                                   self.label_j, self.label_k]

        for i, label in enumerate(self.labels_entry_names):
            label.grid(row=i, column=2, sticky="w", padx=(10, 0), pady=1)

        self.check_delay_is_on.grid(row=11, column=10)
        self.option_tempo_multiplier.grid(row=80, column=8)
        self.frame_memories.grid(row=22, column=5, sticky="we", padx=2, pady=1, rowspan=2)

        for i, mem in enumerate(self.memories):
            mem.show()
            mem.grid()

        self.display_wobblers()
        self.sample_frame.display()
        self.root.mainloop()

    def mute_all(self):
        for item in self.intvars_enable_channels:
            item.set(False)

    def unmute_all(self):
        for item in self.intvars_enable_channels:
            item.set(True)

    def invert_mute(self):
        for item in self.intvars_enable_channels:
            item.set(not item.get())

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
        for i, _ in enumerate(self.step_played_counts):
            self.step_played_counts[i] = 0
            self.actual_notes_played_counts[i] = 0
        self.idx = 0
        self.set_current_note_idx(0)
        log(logfile=self.context.logfile, msg="actual_notes_played_count was RESET.")

    def init_entries(self):
        for entry in self.entry_boxes:
            if entry is not self.entry_midi_channels:
                insert_into_entry(entry, StringConstants.initial_empty_sequences)

        insert_into_entry(self.entry_scale_sequence, " lydian | *0 | *0 | *0 | *0 | *0 | *0 ")
        insert_into_entry(self.entry_root_sequence, "e | *0 | *0 | *0 | *0 | *0 | *0 ")
        self.entry_octave_sequence.insert(tk.END, "-2")
        self.entry_off_array.insert(tk.END, "1")
        self.press_all_enters()

    def press_all_enters(self):
        self.set_memory_sequence(None)
        self.set_note_scheduling_sequence(None)
        self.set_off_array(None)
        self.set_poly_absolute(None)
        self.set_poly_relative(None)
        self.set_skip_note_sequential(None)
        self.set_skip_note_parallel(None)
        self.set_octave_sequence(None)
        self.set_root_sequence(None)
        self.set_scale_sequence(None)
        self.set_midi_channels(None)

    def get_internal_state(self, typ=None):
        if typ is None:
            state = OrderedDict()
            memory = self.memories[0].get_all()
            sample_seqs = self.sample_frame.get_all_sequences()

            for i, entry in enumerate(self.entry_boxes):
                state[self.entry_boxes_names[i]] = str(entry.get())

            for i, sample_seq in enumerate(sample_seqs):
                state["sample %s" % i] = sample_seq

            print("State: %s" % state)
            print("Memory: %s" % memory)
            return InternalState(memory, state)

    def save_internal_state(self, typ=None):
        if typ is None:
            f = os.path.join(self.context.state_dir, get_date_string("filename") + ".state")
            internal_state = self.get_internal_state()

            try:
                with open(f, "w") as f:
                    for name, content in internal_state.entries.items():
                        f.write("%s\t%s\n" % (name, content))

                    for seq in internal_state.memory:
                        f.write("memory\t%s\n" % seq)

                    f.write("bpm\t%s" % self.context.get_bpm())
                    f.flush()

            except Exception as e:
                print("Couldn't S A V E state, because: %s" % e)

    def load_internal_state(self, typ=None):
        if typ is None:
            try:
                filename = filedialog.askopenfilename(initialdir=self.context.state_dir, title="Select file",
                                                      filetypes=(("state files", "*.state"), ("all files", "*.*")))
            except Exception as e:
                log(logfile=self.context.logfile, msg="Could not open file dialog, because: %s" % e)

            else:
                try:
                    with open(filename, "r") as f:
                        lines = f.readlines()

                    print(lines)
                    self.memories[0].clear_all()

                    for line in lines:
                        if line != "\n":
                            typ, content = line.split("\t")
                            content = content.replace("\n", "").replace("\t", "")

                            if typ in self.entry_boxes_names:
                                idx = self.entry_boxes_names.index(typ)
                                insert_into_entry(entry=self.entry_boxes[idx], seq=content)

                            elif "sample" in typ:
                                if content:
                                    idx = int(typ.split()[-1])
                                    self.sample_frame.insert(content, idx)
                                    self.sample_frame.set_sequence(event=None, channel=idx, seq=content)

                            elif typ == "memory":
                                self.memories[0].add_seq(content)
                            elif typ == "bpm":
                                self.context.bpm.set(content)
                            else:
                                print("Something weird in state file: %s" % typ)
                except Exception as e:
                    print("Couldn't L O A D state, because: %s" % e)
                else:
                    self.press_all_enters()
                    self.reset_idx()

    def set_sequence(self, _, mode=None):
        parser = self.context.parser
        text = str(self.entry_sequence.get())

        if mode is None:
            log(logfile=self.context.logfile, msg="\"%s\"" % text)
            notes, str_seq = parser.get_notes(self.context, text, None)
            self.context.str_sequence = str_seq

        elif mode is self.context.set_sequence_modes.dont_regenerate:
            notes, str_seq = parser.get_notes(self.context, self.context.str_sequence.replace(" ", ""))

        notes = convert_midi_notes_to_note_objects(self.context, notes)
        self.context.sequence = notes
        insert_into_entry(self.entry_str_seq, self.context.str_sequence)
        self.strvar_main_seq_len.set(str(self.context.sequence.__len__()))

    def set_memory_sequence(self, _):
        parser = self.context.parser
        text = str(self.entry_memory_sequence.get())
        self.context.str_sequence = ""
        self.context.note_sequences = []

        individual_sequences = parser.parse_multiple_sequences_separated(
            separator=StringConstants.multiple_entry_separator,
            sequences=text)

        for i, result in enumerate(individual_sequences):
            result = parser.parse_memory_sequence(result)
            running_seq = []
            aaaaaaaaa = ""
            prev, prev_notes, prev_str_seq = None, None, None

            for idx in result:
                # this is for literal sequence in memory sequence entrybox
                if isinstance(idx, tuple):
                    notes, str_seq = self.context.parser.get_notes(self.context, idx[0][1:], iii=i)
                    notes = convert_midi_notes_to_note_objects(self.context, notes)
                    notes *= idx[1]
                    str_seq *= idx[1]

                else:
                    str_seq = self.memories[0].get_by_index(idx)

                    if prev == idx and prev is not None:
                        notes = prev_notes
                        str_seq = prev_str_seq

                    else:
                        if str_seq is not None:
                            notes, str_seq = parser.get_notes(self.context, str_seq, iii=i)
                            notes = convert_midi_notes_to_note_objects(self.context, notes)
                        else:
                            notes, str_seq = [], ""

                running_seq += notes
                self.context.str_sequence += str_seq
                aaaaaaaaa += str_seq

                prev = idx
                prev_notes = notes
                prev_str_seq = str_seq

            self.context.str_sequences[i] = aaaaaaaaa.split()

            print("Str sequence for idx %s set to: %s" % (i, self.context.str_sequences[i]))

            self.entry_str_seq.delete(0, tk.END)
            self.entry_str_seq.insert(0, self.context.str_sequence)
            self.context.note_sequences.append(running_seq)

            log(logfile=self.context.logfile, msg="Sequence %s set to: %s" % (i, running_seq))

        self.context.sequence = self.context.note_sequences[0]

    def set_note_scheduling_sequence(self, _):
        parser = self.context.parser
        text = str(self.entry_note_scheduling.get())

        individual_sequences = parser.parse_multiple_sequences_separated(
            separator=StringConstants.multiple_entry_separator,
            sequences=text)

        for i, individual_seq in enumerate(individual_sequences):
            parsed_individual_seq = parser.parse_scheduling_sequence(individual_seq)
            self.context.scheduling_sequences[i] = [NoteSchedulingObject(seq) for seq in parsed_individual_seq]

        log(logfile=self.context.logfile, msg="Scheduling sequences set to: %s" % self.context.scheduling_sequences)

    def add_seq_to_memory(self, typ):
        text_ = str(self.entry_sequence.get())
        self.memories[0].add_seq(text_)

    def set_root_sequence(self, _):
        parser = self.context.parser
        text = self.entry_root_sequence.get()

        individual_sequences = parser.parse_multiple_sequences_separated(
            separator=StringConstants.multiple_entry_separator,
            sequences=text)

        for i, seq in enumerate(individual_sequences):
            self.context.root_sequences[i] = parser.parse_root_sequence(seq)
            self.context.roots[i] = self.context.root_sequences[i][0]
        self.context.root_sequence = self.context.root_sequences[0]

        log(logfile=self.context.logfile, msg="Root sequences set to: %s" % self.context.root_sequences)

    def set_octave_sequence(self, _):
        parser = self.context.parser
        text = self.entry_octave_sequence.get()

        individual_sequences = parser.parse_multiple_sequences_separated(
            separator=StringConstants.multiple_entry_separator,
            sequences=text)

        for i, seq in enumerate(individual_sequences):
            self.context.octave_sequences[i] = parser.parse_octave_sequence(seq)
        self.context.octave_sequence = self.context.octave_sequences[0]

        log(logfile=self.context.logfile, msg="Octave sequences set to: %s" % self.context.octave_sequences)

    def set_scale_sequence(self, _):
        parser = self.context.parser
        text = self.entry_scale_sequence.get()

        individual_sequences = parser.parse_multiple_sequences_separated(
            separator=StringConstants.multiple_entry_separator,
            sequences=text)

        for i, seq in enumerate(individual_sequences):
            self.context.scale_sequences[i] = parser.parse_scale_sequence(self.context, seq)
            self.context.scales_individual[i] = self.context.scale_sequences[i][0]
        self.context.scale_sequence = self.context.scale_sequences[0]

        self.set_memory_sequence(None)
        log(logfile=self.context.logfile, msg="Scale sequences set to: %s" % self.context.scale_sequences)

    def set_poly_absolute(self, _):
        parser = self.context.parser
        text = self.entry_poly.get()

        individual_sequences = parser.parse_multiple_sequences_separated(
            separator=StringConstants.multiple_entry_separator,
            sequences=text)

        self.context.poly_sequences = [list(map(int, voices.split())) for voices in individual_sequences]
        self.context.poly = self.context.poly_sequences[0]

        log(logfile=self.context.logfile, msg="Poly: %s" % self.context.poly_sequences)

    def set_poly_relative(self, _):
        parser = self.context.parser
        text = self.entry_poly_relative.get()

        individual_sequences = parser.parse_multiple_sequences_separated(
            separator=StringConstants.multiple_entry_separator,
            sequences=text)

        self.context.poly_relative_sequences = [list(map(int, voices.split())) for voices in individual_sequences]
        self.context.poly_relative = self.context.poly_relative_sequences[0]

        log(logfile=self.context.logfile, msg="Poly relative: %s" % self.context.poly_relative_sequences)

    def set_skip_note_parallel(self, _):
        parser = self.context.parser
        text = self.entry_skip_note_parallel.get()

        individual_sequences = parser.parse_multiple_sequences_separated(
            separator=StringConstants.multiple_entry_separator,
            sequences=text)

        self.context.skip_note_parallel_sequences = [list(map(int, skips.split())) for skips in individual_sequences]
        self.context.skip_notes_parallel = self.context.skip_note_parallel_sequences[0]

        log(logfile=self.context.logfile, msg="Skip notes parallel: %s" % self.context.skip_note_parallel_sequences)

    def set_skip_note_sequential(self, _):
        parser = self.context.parser
        text = self.entry_skip_note_sequential.get()

        individual_sequences = parser.parse_multiple_sequences_separated(
            separator=StringConstants.multiple_entry_separator,
            sequences=text)

        self.context.skip_notes_sequential_sequences = [list(map(int, skips.split())) for skips in individual_sequences]
        self.context.skip_notes_sequential = self.context.skip_notes_sequential_sequences[0]

        log(logfile=self.context.logfile, msg="Skip notes sequential: %s" % self.context.skip_notes_sequential_sequences)

    def set_scale(self, scale_):
        self.context.scale = self.context.scales.get_scale_by_name(scale_)
        log(logfile=self.context.logfile, msg="Scale: %s" % self.context.scales.get_display_scale_name(scale_))
        self.strvar_status_bar.set("%s --- %s" % (self.context.scales.get_display_scale_name(scale_), self.context.scale))

        for i, _ in enumerate(self.context.scale_sequences):
            self.context.scale_sequences[i] = [scale_]

        sequences = self.entry_scale_sequence.get().split(StringConstants.multiple_entry_separator)
        new_content = [" %s " % scale_] + sequences[1:]
        insert_into_entry(self.entry_scale_sequence,
                          StringConstants.multiple_entry_separator.join(new_content))
        self.set_scale_sequence(None)
        self.context.scales_individual = [scale_]*7

    def set_off_array(self, _):
        parser = self.context.parser
        text = self.entry_off_array.get()

        individual_sequences = parser.parse_multiple_sequences_separated(
            separator=StringConstants.multiple_entry_separator,
            sequences=text)

        parsed_individual_sequences = [parser.parse_off_array(seq) for seq in individual_sequences]
        self.context.off_sequences = parsed_individual_sequences
        self.context.off_list = parsed_individual_sequences[0]

        log(logfile=self.context.logfile, msg="Off lists: %s" % self.context.off_sequences)

    def set_midi_channels(self, _):
        parser = self.context.parser
        text = self.entry_midi_channels.get()

        individual_sequences = parser.parse_multiple_sequences_separated(
            separator=StringConstants.multiple_entry_separator,
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

    def end_all_notes(self, i=None):
        if i is None:
            for j in range(16):
                self.context.midi.send_message([0xb0 + j, 123, 0])
        else:
            for chan in self.context.midi_channels[i]:
                self.context.midi.send_message([0xb0 + chan, 123, 0])

    def pitch_bend(self, what):
        if what == "on":
            msg = [0b11100000 + int(self.strvar_option_midi_channel.get()) - 1, 0x00, 0x60]
        elif what == "off":
            msg = [0b11100000 + int(self.strvar_option_midi_channel.get()) - 1, 0b0, 0b1000000]

        self.context.midi.send_message(msg)
        log(logfile=self.context.logfile, msg="Pitch bend sent.")

    def get_velocity_min_max(self, i):
        if i > NumberOf.VELOCITY_SLIDERS:
            return 100, 127

        slider_min = Ranges.MIDI_MAX if i >= len(self.velocities_strvars_min) else int(self.velocities_strvars_min[i].get())
        slider_max = Ranges.MIDI_MAX if i >= len(self.velocities_strvars_max) else int(self.velocities_strvars_max[i].get())

        vel_min = slider_min if slider_min < slider_max else slider_max
        vel_max = slider_max if slider_max > slider_min else slider_min

        return vel_min, vel_max

    def skip_note_parallel(self, idx, j):
        if self.context.skip_note_parallel_sequences:
            if self.context.skip_note_parallel_sequences[j]:
                for i in range(0, self.context.skip_note_parallel_sequences[j].__len__()):
                    if (idx // self.get_tempo_multiplier()) % (self.context.skip_note_parallel_sequences[j][i] + 1) == 0:
                        return True

    def skip_note_sequentially(self, skip_sequential_idx, idx_sequential_skip, i):
        if self.context.skip_notes_sequential_sequences:
            if self.context.skip_notes_sequential_sequences[i]:
                loop_skip_sequential_idx = skip_sequential_idx % len(self.context.skip_notes_sequential_sequences[i])

                if idx_sequential_skip % (self.context.skip_notes_sequential_sequences[i][loop_skip_sequential_idx]) == 0:
                    if idx_sequential_skip > 0:
                        return skip_sequential_idx + 1, 0, True

        return skip_sequential_idx, idx_sequential_skip, False

    def play_poly_notes(self, note, i):
        if self.context.poly_sequences:
            if self.context.poly_sequences[i]:
                for poly in self.context.poly_sequences[i]:
                    if a() < int(self.strvars_prob_poly_abs[i].get()) / 100.:
                        note.play_transposed(poly)

    def play_relative_poly_notes(self, note, note_entry, i):
        if not str(note_entry).isdigit():
            return

        try:
            if self.context.scale_sequences[i]:
                scale = self.context.scale_sequences[i][0]
            else:
                scale = self.context.scale
        except Exception as e:
            print("Exception: %s" % e)

        scales = self.context.scales
        scale = scales.get_scale_by_name(scale)

        if self.context.poly_relative_sequences:
            if self.context.poly_relative_sequences[i]:
                for poly in self.context.poly_relative_sequences[i]:
                    if a() < int(self.strvars_prob_poly_rel[i].get()) / 100.:
                        # THIS TOOK FUCKING FOREVER TO FIGURE OUT
                        added = (int(scales.get_note_by_index_wrap(note_entry + poly, scale))
                                 - int(scales.get_note_by_index_wrap(note_entry, scale)))
                        note.play_transposed(added)

    def play_sample_notes(self):
        for channel, sample_seq in enumerate(self.context.sample_seqs):
            if sample_seq:
                sample_idx = self.idx % len(sample_seq)

                step = (self.idx - 1) % len(sample_seq)
                self.sample_frame.update_label_with_current_step(channel, step, sample_seq[step])

                if sample_seq[sample_idx] and self.sample_frame.intvars_mutes[channel].get():
                    self.context.midi.send_message(sample_seq[sample_idx])

    def get_delay_multiplier(self):
        return float(self.context.get_delay_multiplier())

    def get_orig_note(self, note, octave_idx, i, j=0):
        vel_min, vel_max = self.get_velocity_min_max(i)

        octave_offset = 0
        if self.context.octave_sequences:
            octave_offset = 0 if not self.context.octave_sequences[i] else self.context.octave_sequences[i][octave_idx]

        note_copy = copy.copy(note)
        note_copy.set_channel(self.context.midi_channels[i][j])

        if note_copy.type_ is NoteTypes.NORMAL:
            if isinstance(note_copy, NoteContainer):
                note_copy.pitch = (self.context.roots[i] - c2 - 4 + octave_offset)
            note_copy.pitch += self.context.roots[i] - c2 - 4 + octave_offset

        note_copy.set_velocity(random.randint(vel_min, vel_max))
        return note_copy

    def turn_off_notes(self, off_note_idx, idx_all_off, i):
        if self.context.off_sequences:
            if self.context.off_sequences[i]:
                loop_off_note_idx = off_note_idx % len(self.context.off_sequences[i])

                try:
                    if idx_all_off % (self.context.off_sequences[i][loop_off_note_idx]) == 0:
                        if idx_all_off > 0:
                            self.end_all_notes(i)
                            return off_note_idx + 1, 0
                except:
                    print("Don't modulo by zero pls :D")

        return off_note_idx, idx_all_off

    def play_midi_notes(self):
        if not self.context.note_sequences:
            return

        valid_midi_channels = [channel for channel in self.context.midi_channels if channel]

        for i, valid_channels in enumerate(valid_midi_channels):
            if i < len(self.context.note_sequences) and self.context.note_sequences[i]:
                if (a() > float(self.strvars_prob_skip_note[i].get()) / 100
                        and self.idx % self.get_tempo_multiplier() == 0):

                    loop_idx = self.step_played_counts[i] % len(self.context.note_sequences[i])
                    note_scheduling_idx = (self.actual_notes_played_counts[i] % len(self.context.scheduling_sequences[i])
                                           if self.context.scheduling_sequences[i] else None)

                    octave_idx = self.get_octave_idx(i)
                    self.manage_root_sequence(i)
                    self.manage_scale_sequence(i)

                    try:
                        note = self.context.note_sequences[i][loop_idx]
                    except:
                        time.sleep(.02)
                        continue

                    if not self.intvars_enable_channels[i].get():
                        if note != NoteTypes.NOTE_PAUSE:
                            self.step_played_counts[i] += 1
                            self.actual_notes_played_counts[i] += 1
                        continue

                    orig_note = self.get_orig_note(note, octave_idx, i, 0)

                    self.set_current_note_idx(loop_idx)
                    self.off_note_idx[i], self.idx_all_off[i] = self.turn_off_notes(self.off_note_idx[i], self.idx_all_off[i], i)

                    self.skip_sequential_idx[i], self.idx_sequential_skip[i], skip_sequentially = \
                        self.skip_note_sequentially(self.skip_sequential_idx[i], self.idx_sequential_skip[i], i)

                    if orig_note.type_ is NoteTypes.NOTE_PAUSE:
                        self.step_played_counts[i] += 1
                        continue

                    if orig_note.type_ is not NoteTypes.NOTE_PAUSE:
                        if orig_note.type_ is NoteTypes.GO_TO_START:
                            self.idx = -1
                            self.step_played_counts[i] = 0
                            self.actual_notes_played_counts[i] = 0
                            return "dont sleep"

                        elif not self.skip_note_parallel(self.idx, i) and not skip_sequentially:
                            for j, channel in enumerate(valid_channels):
                                orig_note = self.get_orig_note(note, octave_idx, i, j)

                                if self.context.kick_notes:
                                    self.context.kick_notes[-1].end()
                                    self.context.kick_notes = []

                                if orig_note.channel == 13:
                                    self.context.kick_notes.append(orig_note)

                                if note_scheduling_idx is not None:
                                    scheduling_object = self.context.scheduling_sequences[i][note_scheduling_idx]
                                    if not isinstance(orig_note, NoteContainer):
                                        orig_note.supply_scheduling_object(scheduling_object)
                                orig_note.play()

                            if self.delay_is_on():
                                self.play_delay(i, note, octave_idx, valid_channels)

                            self.step_played_counts[i] += 1
                            self.actual_notes_played_counts[i] += 1
                            self.idx_sequential_skip[i] += 1
                            self.idx_all_off[i] += 1

                            for j, channel in enumerate(valid_channels):
                                orig_note = self.get_orig_note(note, octave_idx, i, j)
                                self.play_poly_notes(orig_note, i)

                            for j, channel in enumerate(valid_channels):
                                if self.context.str_sequences[i][loop_idx].isdigit():
                                    param = int(self.context.str_sequences[i][loop_idx])
                                    orig_note = self.get_orig_note(note, octave_idx, i, j)
                                    self.play_relative_poly_notes(orig_note, param, i)

    def play_delay(self, i, note, octave_idx, valid_channels):
        for j, channel in enumerate(valid_channels):
            orig_note = self.get_orig_note(note, octave_idx, i, j)
            x = lambda: self.delay.run_delay_with_note(
                orig_note,
                60. / self.context.get_bpm() / self.get_delay_multiplier(),
                self.delay_functions.functions[self.delay_constants.CONSTANT_DECAY],
                -10)

            Delay(self.context).create_thread_for_function(x)

    def get_octave_idx(self, i):
        try:
            return self.step_played_counts[i] % len(self.context.octave_sequences[i])
        except:
            return 0

    def manage_root_sequence(self, i):
        try:
            root_idx = self.step_played_counts[i] % len(self.context.root_sequences[i])

            if self.context.root_sequences[i][root_idx] != self.context.roots[i]:
                self.end_all_notes(i)
                self.context.roots[i] = self.context.root_sequences[i][root_idx]

                log(logfile=self.context.logfile,
                    msg="Root for i=%s changed to: %s" % (i, self.context.root_sequences[i][root_idx]))

        except:
            pass

    def manage_scale_sequence(self, i):
        try:
            scale_idx = self.step_played_counts[i] % len(self.context.scale_sequences[i])

            if self.context.scale_sequences[i][scale_idx] != self.context.scales_individual[i]:
                self.end_all_notes(i)
                self.context.scales_individual[i] = self.context.scale_sequences[i][scale_idx]
                self.set_sequence(None, self.context.set_sequence_modes.dont_regenerate)
                self.set_memory_sequence(None)

                log(logfile=self.context.logfile,
                    msg="Scale for i=%s changed to: %s" % (i, self.context.scale_sequences[i][scale_idx]))

        except:
            pass

    def play_sequence(self):
        while True:
            if not self.context.playback_on:
                time.sleep(.02)
                continue

            result = self.play_midi_notes()
            self.frame_status.update()
            self.play_sample_notes()

            if result != "dont sleep":
                sleep_time = NoteLengthsOld(self.context.get_bpm()).eigtht
                time.sleep(sleep_time)

            self.idx += 1
