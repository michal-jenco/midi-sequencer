import tkinter as tk
import math as m
import time
import random
from collections import OrderedDict

from source.cc import CCKeys, CCFM, CCKick, CCSample, CCMonologue
from source.functions import range_to_range
from source.constants import *


class Wobbler(tk.Frame):
    def __init__(self, parent, context, name_):
        tk.Frame.__init__(self, parent, bg="darkblue", padx=0, pady=0)

        self.name = name_
        self.context = context
        self.parent = parent

        self.cc = None
        self.devices = OrderedDict((("Keys", CCKeys), ("FM", CCFM), ("Sample", CCSample), ("Kick", CCKick),
                                    ("Monologue", CCMonologue)))

        self.functions = ["sin", *["sin_%s" % i for i in range(2, 10)],
                          *["tilt_sin_%s" % i for i in range(1, 10)],
                          "cycloid", "rand", "min_max"]

        self.control_change = None
        self.function = None
        self.speed = None
        self.min = None
        self.max = None

        self.running = False

        self.label_name = tk.Label(self, text=self.name)

        self.strvar_label_value = tk.StringVar(self, "Value: ?")
        self.label_value = tk.Label(self, textvariable=self.strvar_label_value, width=10)

        self.strvar_scale_min = tk.StringVar(self, "0")
        self.scale_min = tk.Scale(self, from_=0, to=127, orient=tk.VERTICAL, variable=self.strvar_scale_min)

        self.strvar_scale_max = tk.StringVar(self, "127")
        self.scale_max = tk.Scale(self, from_=0, to=127, orient=tk.VERTICAL, variable=self.strvar_scale_max)

        self.strvar_scale_wait_time = tk.StringVar(self, "100")
        self.scale_wait_time = tk.Scale(self, from_=0, to=100, length=150, orient=tk.VERTICAL, variable=self.strvar_scale_wait_time)

        self.strvar_scale_func_factor = tk.StringVar(self, "20")
        self.scale_func_factor = tk.Scale(self, from_=1, to=50, length=150, orient=tk.VERTICAL, variable=self.strvar_scale_func_factor)

        self.button_toggle = tk.Button(self, text="Start", command=self.toggle)

        self.strvar_option_volca = tk.StringVar(self, list(self.devices.keys())[0])
        self.option_volca = tk.OptionMenu(self, self.strvar_option_volca, *self.devices.keys(), command=self.update_cc_list)
        self.cc = self.devices[self.strvar_option_volca.get()]()

        self.strvar_option_func = tk.StringVar(self, "sin")
        self.option_func = tk.OptionMenu(self, self.strvar_option_func, *self.functions)

        self.cc_all = self.cc.get_all()
        self.strvar_option_cc = tk.StringVar(self, self.cc_all[0])
        self.option_cc = tk.OptionMenu(self, self.strvar_option_cc, *self.cc_all)

        self.strvar_option_midi_channel = tk.StringVar(self, "12")
        self.option_midi_channel = tk.OptionMenu(self, self.strvar_option_midi_channel, *range(1, 17))

        self.intvar_check_10x = tk.IntVar(DISABLED)
        self.check_x10 = tk.Checkbutton(self, text="x10", variable=self.intvar_check_10x)

        # self.output_file = open("../other/" + self.name + ".txt", "a")
        print("%s created" % self.name)

    def update_cc_list(self, _):
        menu = self.option_cc["menu"]
        menu.delete(0, "end")

        all_ccs = self.devices[self.strvar_option_volca.get()]().get_all()

        for string in all_ccs:
            menu.add_command(label=string,
                             command=lambda value=string: self.strvar_option_cc.set(value))
        self.strvar_option_cc.set(all_ccs[0])

    def display(self):
        self.label_value.grid(row=5, column=0, pady=(0, 10), columnspan=2)

        self.scale_min.grid(row=5, column=0, rowspan=7, padx=0)
        self.scale_max.grid(row=5, column=1, rowspan=7, padx=0)
        self.scale_wait_time.grid(row=5, column=2, rowspan=7, padx=0)
        self.scale_func_factor.grid(row=5, column=3, rowspan=7, padx=0)

        self.button_toggle.grid(row=7, column=20, pady=0)

        self.option_volca.grid(row=4, column=20, pady=0)
        self.option_func.grid(row=6, column=20, pady=0)
        self.option_cc.grid(row=5, column=20, pady=0)
        self.option_midi_channel.grid(row=9, column=20, pady=0)

        self.check_x10.grid(row=10, column=20)

    def wobble(self):
        loop_cnt = 0
        
        while True:
            if not self.running:
                time.sleep(0.1)
                continue

            slider_max = int(self.strvar_scale_max.get())
            slider_min = int(self.strvar_scale_min.get())

            min_ = slider_min if slider_min < slider_max else slider_max
            max_ = slider_max if slider_max > slider_min else slider_min

            scale = int(self.strvar_scale_func_factor.get())
            func = self.strvar_option_func.get()

            # self.funcs = {"sin": lambda: self.sin_func(loop_cnt, scale)}
            # value = self.funcs[func]

            if func == "sin":
                value = self.sin_func(loop_cnt, scale)

            elif "tilt_sin_" in func:
                value = self.tilted_sine(loop_cnt, scale, int(func.split("_")[-1]))

            elif "sin_" in func:
                value = self.combined_sines(loop_cnt, int(func.split("_")[-1]), scale, mode="times_scale")

            elif func == "cycloid":
                value = self.cycloid(loop_cnt, scale)

            elif func == "rand":
                value = self.rand_func()

            elif func == "min_max":
                value = self.square_func(loop_cnt)

            value = range_to_range((0, 1), (min_, max_), value)

            # visual output
            # print("#"*int(value/3))

            cc = self.devices[self.strvar_option_volca.get()]().get_cc_by_name(self.strvar_option_cc.get())
            msg = [0xb0 + int(self.strvar_option_midi_channel.get()) - 1, cc, value]

            self.context.midi.send_message(msg)
            self.strvar_label_value.set("Value: %s" % int(value))

            sleep_time = float(self.strvar_scale_wait_time.get()) * 0.001

            if self.intvar_check_10x.get() == ENABLED:
                sleep_time *= 10

            time.sleep(sleep_time)

            loop_cnt += 1

    @staticmethod
    def tilted_sine(x, scale, times):
        x /= scale
        sin = m.sin

        value = sin(x+sin(x)/.2)

        for i in range(times-1):
            value = (value + sin(x)) / 2

        value = (value + 1) / 2
        value = range_to_range((0, 1), (0, 1), value)
        return value

    def cycloid(self, loop_cnt, scale):
        x = loop_cnt - m.sin(loop_cnt / scale)
        y = (1 - m.cos(x / scale)) / 2
        return y

    def combined_sines(self, loop_cnt, how_many, scale, mode):
        if mode == "times_scale":
            individual_values = [self.sin_func(loop_cnt, scale * (i+1)) for i in range(how_many)]

        elif mode == "rand_scale":
            individual_values = [self.sin_func(loop_cnt+(i*random.randint(1, 10)), scale * (i + 1)) for i in range(how_many)]

        value = sum(individual_values) / how_many
        return value

    @staticmethod
    def square_func(loop_cnt):
        return loop_cnt % 2

    @staticmethod
    def rand_func():
        return random.random()

    @staticmethod
    def sin_func(loop_cnt, scale):
        return (m.sin(loop_cnt / scale) + 1) / 2

    def toggle(self):
        if self.running:
            self.running = False
            self.button_toggle["text"] = "Start"
            self["bg"] = "darkblue"

        else:
            self.running = True
            self.button_toggle["text"] = "Stop"
            self["bg"] = "gold"

    @staticmethod
    def stretch( value, min_, max_):
        return value * (max_ - min_) + min_


