import tkinter as tk
import random

from source.constants import MODE_SAMPLE


class SampleFrame(tk.Frame):
    def __init__(self, parent, context):
        tk.Frame.__init__(self, parent, padx=5, pady=5)

        self.context = context

        self.seq_entries = []
        self.labels = []
        self.strvars = []

        self.parser = context.parser

        cnt = 10
        for i in range(0, cnt):
            e = tk.Entry(self, width=40)
            self.seq_entries.append(e)
            self.seq_entries[i].bind('<Return>', lambda event, x=i: self.set_sequence(event, x))

            s = tk.StringVar(self, "")
            label_font = ("Courier", "10")
            
            l = tk.Label(self, text=random.choice("?:_#&"), textvariable=s, font=label_font)
            self.labels.append(l)
            self.strvars.append(s)

    def update_label_with_current_step(self, channel, step, click):
        notes, str_seq = self.parser.get_notes(self.context, self.seq_entries[channel].get(), mode=MODE_SAMPLE)

        msg = "|"
        for i, note in enumerate(notes):
            if i == step:
                msg += "#"
            else:
                msg += " "

        spac = 3
        temp = len(str(step + 1))
        msg += "|" + (spac - temp)*" "

        str_slash = str(step + 1) + "/" + str(len(notes))
        msg += str_slash
        msg += (spac if not click else spac - 1)*" "

        if click:
            msg += "X"

        self.strvars[channel].set(msg)

    def display(self):
        offset = 5
        for i, e in enumerate(self.seq_entries):
            e.grid(row=offset + i, column=10, pady=2, sticky="w")

        for i, l in enumerate(self.labels):
            l.grid(row=offset + i, column=11, pady=2, sticky="w")

    def set_sequence(self, event, channel):
        notes, str_seq = self.parser.get_notes(self.context, event.widget.get(), mode=MODE_SAMPLE)

        for note in notes:
            if note:
                note[0] += channel

        print("Ch%s: (%s)\t\"%s\"" % (channel+1, len(notes), notes))

        self.context.sample_seqs[channel] = notes
        self.update_label_with_current_step(channel, 0, False)
