import tkinter as tk
import threading
import time
import copy
import random

from source.note_lengths import NoteLengths
from scales import Scales
from context import Context
from parser_my import Parser
from source.evolver import Evolver
from source.wobbler import Wobbler
from source.midi_clock import MidiClock
from notes import *
from source.constants import *
from sample_frame import SampleFrame

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
        self.frame_wobblers.grid(row=0, column=3, rowspan=5)

        self.wobblers.append(Wobbler(self.frame_wobblers, self.context, "Keys wobbler 1"))
        self.wobblers.append(Wobbler(self.frame_wobblers, self.context, "Keys wobbler 2"))
        self.wobblers.append(Wobbler(self.frame_wobblers, self.context, "Keys wobbler 3"))
        self.wobblers.append(Wobbler(self.frame_wobblers, self.context, "Keys wobbler 4"))

        self.sample_frame = SampleFrame(self.root, self.context)
        self.sample_frame.grid(row=22, column=3, sticky="", rowspan=5)
        self.sample_frame.display()

        a = 0
        for wob in self.wobblers:
            wob.grid(row=0, column=a, padx=3, pady=5)
            wob.display()

            threading.Thread(target=wob.wobble).start()

            a += 1

        self.strvar_option_midi_channel = tk.StringVar(self.root, "11")
        self.option_midi_channel = tk.OptionMenu(self.root, self.strvar_option_midi_channel,
                                                 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16)

        self.frame_scale_buttons = tk.Frame(self.root)
        self.frame_scale_buttons.grid(row=5, column=3, rowspan=4, columnspan=4, padx=5, pady=0)

        self.frame_sliders = tk.Frame(self.root)
        self.frame_sliders.grid(row=30, column=3, sticky="wens", padx=10, pady=5)

        self.frame_roots = tk.Frame(self.root)
        self.frame_roots.grid(row=32, column=3, sticky="wens", padx=10, pady=5)

        self.frame_prob_sliders = tk.Frame(self.root)
        self.frame_prob_sliders.grid(row=31, column=3, sticky="wens", padx=10, pady=5)

        label_font = ("Courier", "12")
        self.strvar_status_bar = tk.StringVar(self.root, "")
        self.label_status_bar = tk.Label(self.root, textvariable=self.strvar_status_bar, font=label_font)
        self.label_status_bar.grid(row=100, column=3, columnspan=1, pady=(5, 5), padx=10)

        self.strvar_prob_skip_note = tk.StringVar(self.frame_sliders)
        self.scale_prob_skip_note = tk.Scale(self.frame_sliders, from_=0, to=100, orient=tk.HORIZONTAL, sliderlength=30,
                                             variable=self.context.prob_skip_note, length=500)
        self.scale_prob_skip_note.grid(row=23, column=3)

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

        self.strvar_bpm = tk.StringVar(self.frame_sliders)
        self.scale_bpm = tk.Scale(self.frame_sliders, from_=5, to=240, orient=tk.HORIZONTAL, sliderlength=30,
                                  variable=self.context.bpm, length=500)
        self.scale_bpm.grid(row=24, column=3, sticky="wens")


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

        # tk.OptionMenu(self.root, self.context.drone_freq, 1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16).grid(row=10-5, column=8)

        self.option_midi_channel.grid(row=11-5, column=8, pady=1)

        self.entry_sequence = tk.Entry(self.root, width=80)
        self.entry_sequence.bind('<Return>', self.set_sequence)
        self.entry_sequence.grid(row=20, column=3, sticky='wn', pady=(2, 2), padx=10)
        self.entry_sequence.delete(0, tk.END)
        self.entry_sequence.insert(0, "032")

        self.entry_str_seq = tk.Entry(self.root, width=80)
        self.entry_str_seq.grid(row=21, column=3, sticky='wn', pady=(2, 2), padx=10)

        self.entry_off_array = tk.Entry(self.root, width=80)
        self.entry_off_array.bind('<Return>', self.set_off_array)
        self.entry_off_array.grid(row=22, column=3, sticky='wn', pady=(2, 2), padx=10)

        self.entry_poly = tk.Entry(self.root, width=80)
        self.entry_poly.bind('<Return>', self.set_poly)
        self.entry_poly.grid(row=23, column=3, sticky='wn', pady=(2, 2), padx=10)

    def set_poly(self, _):
        voices = self.entry_poly.get().split()
        self.context.poly = list(map(int, voices))
        print("Poly: %s" % self.context.poly)

    def show(self):
        self.set_scale("lydian")
        self.root.mainloop()

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


    def play_sequence(self):

        print("Play sequence is running.")

        mc = MidiClock(self.context)

        note_cnt = 0
        drone_cnt = 0

        time.sleep(0.1)

        idx = 0
        idx_2 = 0
        off_note_idx = 0
        clock_division_factor = 16

        while True:

            idx += 1
            idx_2 += 1

            if not self.context.playback_on:
                time.sleep(0.1)
                continue

            loop_idx = idx % len(self.context.sequence)

            if self.context.off_list:
                loop_off_note_idx = off_note_idx % len(self.context.off_list)

            print(loop_idx)

            note = self.context.sequence[loop_idx]

            orig_note = copy.copy(note)
            orig_note[0] += int(self.strvar_option_midi_channel.get()) - 1
            orig_note[1] += self.context.root-c2

            slider_min = int(self.strvar_vel_min.get())
            slider_max = int(self.strvar_vel_max.get())

            vel_min = slider_min if slider_min < slider_max else slider_max
            vel_max = slider_max if slider_max > slider_min else slider_min

            orig_note[2] = random.randint(vel_min, vel_max)
            print(orig_note)

            if random.random() > float(self.context.prob_skip_note.get())/100:

                if self.context.off_list:
                    print("Idx = %s" % idx_2)
                    print("mod = %s" % (idx_2 % (self.context.off_list[loop_off_note_idx])))
                    if idx_2 % (self.context.off_list[loop_off_note_idx]) == 0:
                        if idx_2 > 0:
                            self.end_all_notes()
                            off_note_idx += 1
                            idx_2 = 0

                if note[1] != NOTE_PAUSE:
                    if note[1] == GO_TO_START:
                        idx -= idx % len(self.context.sequence) + 1
                        continue
                    else:
                        self.context.midi.send_message(orig_note)
                        if self.context.poly:

                            for poly in self.context.poly:
                                if random.random() > 0.5:
                                    self.context.midi.send_message([orig_note[0], orig_note[1]+poly, orig_note[2]])

                        print("orig_note: %s" % orig_note[1])

            note_off = copy.copy(orig_note)
            note_off[2] = 0

            for channel, sample_seq in enumerate(self.context.sample_seqs):
                if sample_seq:
                    sample_idx = idx % len(sample_seq)

                    if sample_seq[sample_idx]:
                        self.context.midi.send_message(sample_seq[sample_idx])

            sleep_time = NoteLengths(float(self.context.bpm.get())).quarter
            time.sleep(sleep_time)

            # self.context.midi.send_message(note_off)

        # noinspection PyUnreachableCode
        """
        while True:
            note_value = random.choice(scale)
            octave = random.choice([-12, 0, 12, 24])
            velocity = 90
            note_value = context.root + octave + note_value

            note_on = [0x90, note_value, velocity]
            note_off = [0x80, note_value, 0]

            if note_cnt % context.drone_freq.get() == 0:
                nt = scale[context.drone_seq[(drone_cnt//context.each_drone_count) % (len(context.drone_seq))]] + context.root-12
                print(nt)

                note_on = [0x90, nt, 100]
                #note_off = [0x80, nt, 0]

                drone_cnt += 1

            scale = context.scale

            self.context.midi.send_message(note_on)
            time.sleep(NoteLengths(context.bpm).get_random())
            self.context.midi.send_message(note_off)

            note_cnt += 1
        """
