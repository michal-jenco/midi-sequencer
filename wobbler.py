import tkinter as tk
import math as m
import time
import random

from cc import CCKeys
from constants import *


class Wobbler(tk.Frame):
    def __init__(self, parent, context, name_):
        tk.Frame.__init__(self, parent, bg="darkblue", padx=5, pady=5)

        self.name = name_
        self.context = context

        self.cc_keys = CCKeys()

        self.control_change = None
        self.function = None
        self.speed = None
        self.min = None
        self.max = None

        self.running = False

        self.label_name = tk.Label(self, text=self.name)

        self.strvar_label_value = tk.StringVar(self, "Value: ?")
        self.label_value = tk.Label(self, textvariable=self.strvar_label_value, width=10)

        self.strvar_scale_min = tk.StringVar(self, "70")
        self.scale_min = tk.Scale(self, from_=0, to=127, orient=tk.VERTICAL, variable=self.strvar_scale_min)

        self.strvar_scale_max = tk.StringVar(self, "110")
        self.scale_max = tk.Scale(self, from_=0, to=127, orient=tk.VERTICAL, variable=self.strvar_scale_max)

        self.strvar_scale_wait_time = tk.StringVar(self, "100")
        self.scale_wait_time = tk.Scale(self, from_=0, to=100, length=150, orient=tk.VERTICAL, variable=self.strvar_scale_wait_time)

        self.strvar_scale_func_factor = tk.StringVar(self, "20")
        self.scale_func_factor = tk.Scale(self, from_=1, to=50, length=150, orient=tk.VERTICAL, variable=self.strvar_scale_func_factor)

        self.button_toggle = tk.Button(self, text="Start", command=self.toggle)

        self.strvar_option_func = tk.StringVar(self, "sin")
        self.option_func = tk.OptionMenu(self, self.strvar_option_func, "sin", "cos", "rand", "min_max")

        self.cc_all = self.cc_keys.get_all()
        self.strvar_option_cc = tk.StringVar(self, self.cc_all[0])
        self.option_cc = tk.OptionMenu(self, self.strvar_option_cc, *self.cc_all)

        self.strvar_option_midi_channel = tk.StringVar(self, "10")
        self.option_midi_channel = tk.OptionMenu(self, self.strvar_option_midi_channel, 1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16)

        self.intvar_check_10x = tk.IntVar(DISABLED)
        self.check_x10 = tk.Checkbutton(self, text="x10", variable=self.intvar_check_10x)

        self.output_file = open(self.name + ".txt", "a")

        print("%s created" % self.name)

    def display(self):
        # self.label_name.grid(row=0, column=0, columnspan=2)
        self.label_value.grid(row=0, column=0, columnspan=2)

        self.scale_min.grid(row=5, column=0, rowspan=7, padx=2)
        self.scale_max.grid(row=5, column=1, rowspan=7, padx=2)
        self.scale_wait_time.grid(row=5, column=2, rowspan=7, padx=2)
        self.scale_func_factor.grid(row=5, column=3, rowspan=7, padx=2)

        self.button_toggle.grid(row=7, column=20, pady=1)

        self.option_func.grid(row=6, column=20, pady=1)
        self.option_cc.grid(row=5, column=20, pady=1)
        self.option_midi_channel.grid(row=9, column=20, pady=1)

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

            scale_ = int(self.strvar_scale_func_factor.get())
            func_ = self.strvar_option_func.get()

            if func_ == "sin":
                value1 = m.sin((loop_cnt/scale_)+1)/2
                value2 = m.sin((loop_cnt/scale_*3)+1)/2
                value3 = m.sin((loop_cnt/scale_*5)+1)/2

                (m.cos(loop_cnt / scale_) + 1) / 2 * (max_ - min_) + min_

                sum_ = value1 + value2 + value3

                value = int((m.sin(loop_cnt / scale_) + 1) / 2 * (max_ - min_) + min_)

            elif func_ == "cos":
                value = int((m.cos(loop_cnt / scale_) + 1) / 2 * (max_ - min_) + min_)

            elif func_ == "rand":
                value = random.randint(min_, max_)

            elif func_ == "min_max":
                if loop_cnt % 2 == 0:
                    value = min_
                else:
                    value = max_

            cc = self.cc_keys.get_cc_by_name(self.strvar_option_cc.get())

            msg = [0xb0 + int(self.strvar_option_midi_channel.get()), cc, value]

            print(msg)

            self.context.midi.send_message(msg)
            self.strvar_label_value.set("Value: %s" % value)
            self.output_file.write("%s %s\n" % (time.time(), value))

            sleep_time = float(self.strvar_scale_wait_time.get()) / 1000

            if self.intvar_check_10x.get() == ENABLED:
                sleep_time *= 10

            time.sleep(sleep_time)

            loop_cnt += 1

    def toggle(self):
        if self.running:
            self.running = False
            self.button_toggle["text"] = "Start"
            self["bg"] = "darkblue"
        else:
            self.running = True
            self.button_toggle["text"] = "Stop"
            self["bg"] = "gold"

    def stretch(self, value, min_, max_):
        return value * (max_ - min_) + min_


