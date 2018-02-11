import tkinter as tk
import threading
import time
import copy
import random

from source.note_lengths import NoteLengths
from source.scales import Scales
from source.context import Context
from source.parser_my import Parser
from source.evolver import Evolver
from source.wobbler import Wobbler
from source.notes import *
from source.constants import *
from source.sample_frame import SampleFrame
from source.helpful_functions import a, sleep_and_increase_time


class Sequencer:
    def set_sequence(self, _):
        parser = Parser()
        text_ = str(self.entry_sequence.get())
        print("\"%s\"" % text_)
        parser.get_notes(self.context, text_)

        self.entry_str_seq.delete(0, tk.END)
        self.entry_str_seq.insert(0, self.context.str_sequence)

    def __init__(self, midi_):
        self.root = tk.Tk()
        self.root.title("MIDI Sequencer")
        self.root["bg"] = "grey"

        self.context = Context(self.root)
        self.context.drone_seq = [0, 1, -2, -3]
        self.context.each_drone_count = 8
        self.context.root = e2
        self.context.mode = MODE_SIMPLE
        self.context.scale = None
        self.context.playback_on = False

        self.context.midi = midi_

        self.evolver = Evolver(self.context, self.root)
        self.wobblers = []

        self.frame_wobblers = tk.Frame(self.root, bg="black")
        self.frame_wobblers.grid(row=0, column=3, rowspan=5, columnspan=4)

        self.wobblers.append(Wobbler(self.frame_wobblers, self.context, "Keys wobbler 1"))
        self.wobblers.append(Wobbler(self.frame_wobblers, self.context, "Keys wobbler 2"))
        self.wobblers.append(Wobbler(self.frame_wobblers, self.context, "Keys wobbler 3"))
        self.wobblers.append(Wobbler(self.frame_wobblers, self.context, "Keys wobbler 4"))

        self.sample_frame = SampleFrame(self.root, self.context)
        self.sample_frame.grid(row=22, column=4, sticky="we", rowspan=4, padx=2, pady=2)
        self.sample_frame.display()

        abc = 0
        for wob in self.wobblers:
            wob.grid(row=0, column=abc, padx=3, pady=5)
            wob.display()

            threading.Thread(target=wob.wobble).start()
            abc += 1

        self.strvar_tempo_multiplier = tk.StringVar(self.root, "1")
        self.option_tempo_multiplier = tk.OptionMenu(self.root, self.strvar_tempo_multiplier, *[x for x in range(1, 9)])
        self.option_tempo_multiplier.grid()
        self.get_tempo_multiplier = lambda: int(self.strvar_tempo_multiplier.get())

        self.strvar_option_midi_channel = tk.StringVar(self.root, "11")
        self.option_midi_channel = tk.OptionMenu(self.root, self.strvar_option_midi_channel, *[x for x in range(1, 17)])

        self.frame_scale_buttons = tk.Frame(self.root)
        self.frame_scale_buttons.grid(row=5, column=3, rowspan=4, columnspan=3, padx=5, pady=0)

        self.frame_sliders = tk.Frame(self.root)
        self.frame_sliders.grid(row=30, column=3, sticky="wens", padx=10, pady=5, columnspan=3)

        self.frame_roots = tk.Frame(self.root)
        self.frame_roots.grid(row=32, column=3, sticky="wens", padx=10, pady=5, columnspan=3)

        self.frame_prob_sliders = tk.Frame(self.root)
        self.frame_prob_sliders.grid(row=31, column=3, sticky="wens", padx=10, pady=5, columnspan=3)

        label_font = ("Courier", "12")
        self.strvar_status_bar = tk.StringVar(self.root, "")
        self.label_status_bar = tk.Label(self.root, textvariable=self.strvar_status_bar, font=label_font)
        self.label_status_bar.grid(row=100, column=3, columnspan=3, pady=(5, 5), padx=10)

        self.strvar_prob_skip_note = tk.StringVar(self.frame_sliders)
        self.scale_prob_skip_note = tk.Scale(self.frame_sliders, from_=0, to=100, orient=tk.HORIZONTAL, sliderlength=30,
                                             variable=self.context.prob_skip_note, length=500)
        self.scale_prob_skip_note.grid(row=23, column=3, columnspan=3)

        self.strvar_vel_min = tk.StringVar(self.frame_prob_sliders)
        self.strvar_vel_min.set("100")
        self.scale_vel_min = tk.Scale(self.frame_prob_sliders, from_=0, to=127, orient=tk.VERTICAL,
                                      variable=self.strvar_vel_min, length=150)
        self.scale_vel_min.grid(column=0, row=0)

        self.strvar_vel_max = tk.StringVar(self.frame_prob_sliders)
        self.strvar_vel_max.set("127")
        self.scale_vel_max = tk.Scale(self.frame_prob_sliders, from_=0, to=127, orient=tk.VERTICAL,
                                      variable=self.strvar_vel_max, length=150)
        self.scale_vel_max.grid(column=1, row=0)

        self.strvar_prob_skip_poly = tk.StringVar(self.frame_prob_sliders)
        self.strvar_prob_skip_poly.set("50")
        self.scale_prob_skip_poly = tk.Scale(self.frame_prob_sliders, from_=0, to=100, orient=tk.VERTICAL,
                                             variable=self.strvar_prob_skip_poly, length=150)
        self.scale_prob_skip_poly.grid(column=2, row=0)

        self.strvar_bpm = tk.StringVar(self.frame_sliders)
        self.scale_bpm = tk.Scale(self.frame_sliders, from_=5, to=240, orient=tk.HORIZONTAL, sliderlength=30,
                                  variable=self.context.bpm, length=500)
        self.scale_bpm.grid(row=24, column=3, sticky="wens", columnspan=3)

        self.thread_seq = threading.Thread(target=self.play_sequence, args=())
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
        for scale in Scales().get_all():
            scale_name = Scales().get_display_scale_name(scale)

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

        tk.Button(self.root,
                  text="Start sequence",
                  command=self.start_sequence).grid(row=5-5, column=8, padx=10)

        tk.Button(self.root,
                  text="Stop sequence",
                  command=self.stop_sequence).grid(row=6-5, column=8, padx=10)

        tk.Button(self.root,
                  text="All notes off",
                  command=self.end_all_notes).grid(row=7-5, column=8, padx=10)

        tk.Button(self.root,
                  text="Pitch bend ON",
                  command=lambda: self.pitch_bend("on")).grid(row=8-5, column=8, padx=10)

        tk.Button(self.root,
                  text="Pitch bend OFF",
                  command=lambda: self.pitch_bend("off")).grid(row=9-5, column=8, padx=10)

        self.option_midi_channel.grid(row=11-5, column=8, pady=1)

        self.frame_entries = tk.Frame(self.root)

        self.entry_str_seq = tk.Entry(self.frame_entries, width=80)
        self.entry_str_seq.grid(row=1, column=0, sticky='wn', pady=(2, 2), padx=10)

        self.entry_sequence = tk.Entry(self.frame_entries, width=80)
        self.entry_sequence.bind('<Return>', self.set_sequence)
        self.entry_sequence.grid(row=0, column=0, sticky='wn', pady=(2, 2), padx=10)
        self.entry_sequence.delete(0, tk.END)
        self.entry_sequence.insert(0, "032")
        self.set_scale("lydian")
        self.set_sequence(None)

        self.entry_off_array = tk.Entry(self.frame_entries, width=80)
        self.entry_off_array.bind('<Return>', self.set_off_array)
        self.entry_off_array.grid(row=2, column=0, sticky='wn', pady=(2, 2), padx=10)

        self.entry_poly = tk.Entry(self.frame_entries, width=80)
        self.entry_poly.bind('<Return>', self.set_poly)
        self.entry_poly.grid(row=3, column=0, sticky='wn', pady=(2, 2), padx=10)

        self.entry_skip_note = tk.Entry(self.frame_entries, width=80)
        self.entry_skip_note.bind('<Return>', self.set_skip_note)
        self.entry_skip_note.grid(row=4, column=0, sticky='wn', pady=(2, 2), padx=10)

        self.frame_entries.grid(row=22, column=3, sticky="w")

    def show(self):
        self.root.mainloop()

    def set_poly(self, _):
        voices = self.entry_poly.get().split()
        self.context.poly = list(map(int, voices))
        print("Poly: %s" % self.context.poly)

    def set_skip_note(self, _):
        skips = self.entry_skip_note.get().split()
        self.context.skip_notes = list(map(int, skips))
        print("Skip notes: %s" % self.context.skip_notes)

    def set_scale(self, scale_):
        self.context.scale = Scales().get_scale_by_name(scale_)
        print("Scale: %s" % Scales().get_display_scale_name(scale_))
        self.strvar_status_bar.set("%s --- %s" % (Scales().get_display_scale_name(scale_), self.context.scale))
        # self.end_all_notes()

    def set_off_array(self, _):
        indices = self.entry_off_array.get().split()
        self.context.off_list = list(map(int, indices))
        print("Off list: %s" % self.context.off_list)

    def stop_sequence(self):
        self.context.playback_on = False
        print("Sequence stopped.")

    def start_sequence(self):
        self.context.playback_on = True
        print("Sequence started.")

    def end_all_notes(self):
        msg = [0b10110000 + int(self.strvar_option_midi_channel.get()) - 1, 123, 0]
        self.context.midi.send_message(msg)
        print("All notes off.")

    def pitch_bend(self, what):
        if what == "on":
            msg = [0b11100000 + int(self.strvar_option_midi_channel.get()) - 1, 0x00, 0x60]
        elif what == "off":
            msg = [0b11100000 + int(self.strvar_option_midi_channel.get()) - 1, 0b0, 0b1000000]

        self.context.midi.send_message(msg)
        print("Pitch bend sent.")

    def get_velocity_min_max(self):
        slider_min = int(self.strvar_vel_min.get())
        slider_max = int(self.strvar_vel_max.get())

        vel_min = slider_min if slider_min < slider_max else slider_max
        vel_max = slider_max if slider_max > slider_min else slider_min

        return vel_min, vel_max

    def skip_current_note(self, idx):
        if self.context.skip_notes:
            skip = False
            for i in range(0, self.context.skip_notes.__len__()):
                if idx % self.context.skip_notes[i] == 0:
                    skip = True
            return skip

    def play_poly_notes(self, note):
        if self.context.poly:
            for poly in self.context.poly:
                if a() < float(int(self.strvar_prob_skip_poly.get()) / 100.0):
                    self.context.midi.send_message([note[0], note[1] + poly, note[2]])

    def play_sample_notes(self, idx):
        for channel, sample_seq in enumerate(self.context.sample_seqs):
            if sample_seq:
                sample_idx = idx % len(sample_seq)
                print("Sample_idx: %s" % sample_idx)

                step = (idx - 1) % len(sample_seq)
                self.sample_frame.update_label_with_current_step(channel, step, sample_seq[step])

                if sample_seq[sample_idx]:
                    self.context.midi.send_message(sample_seq[sample_idx])

    def get_orig_note(self, note):
        vel_min, vel_max = self.get_velocity_min_max()
        orig_note = copy.copy(note)
        orig_note[0] += int(self.strvar_option_midi_channel.get()) - 1
        orig_note[1] += self.context.root - c2
        orig_note[2] = random.randint(vel_min, vel_max)
        return orig_note

    def play_sequence(self):
        print("Play sequence is running.")
        # mc = MidiClock(self.context)

        time.sleep(0.1)

        ########################################################
        ########################################################
        ################    M A I N   L O O P   ################
        ########################################################
        ########################################################

        idx = 0
        idx_2 = 0
        off_note_idx = 0
        elapsed_time = 0.0

        while True:
            idx += 1
            idx_2 += 1

            if not self.context.playback_on or not self.context.sequence:
                sleep_and_increase_time(0.1, elapsed_time)
                continue

            loop_idx = (idx//self.get_tempo_multiplier()) % len(self.context.sequence)
            note = self.context.sequence[loop_idx]
            orig_note = self.get_orig_note(note)

            if (a() > float(self.context.prob_skip_note.get())/100
                    and idx % self.get_tempo_multiplier() == 0):

                if self.context.off_list:
                    loop_off_note_idx = off_note_idx % len(self.context.off_list)

                    if idx_2 % (self.context.off_list[loop_off_note_idx]) == 0:
                        if idx_2 > 0:
                            self.end_all_notes()
                            off_note_idx += 1
                            idx_2 = 0

                if note[1] != NOTE_PAUSE:
                    if note[1] == GO_TO_START:
                        idx -= idx % len(self.context.sequence) + 1
                        continue
                    elif not self.skip_current_note(idx):
                        self.context.midi.send_message(orig_note)
                        self.play_poly_notes(orig_note)

            self.play_sample_notes(idx)

            bpm = float(self.context.bpm.get())
            sleep_time = NoteLengths(bpm).eigtht

            sleep_and_increase_time(sleep_time, elapsed_time)
