import tkinter as tk
from source.functions import insert_into_entry

from source.constants import MODE_SAMPLE


class SampleFrame(tk.Frame):
    def __init__(self, parent, context):
        tk.Frame.__init__(self, parent, padx=5, pady=5)
        self["bg"] = "darkred"

        self.context = context
        self.parser = context.parser

        self.seq_entries = []
        self.labels = []
        self.strvars = []
        self.mutes = []
        self.intvars_mutes = []

        self.intvar_solo = tk.IntVar(self, False)
        self.checkbutton_solo = tk.Checkbutton(self, variable=self.intvar_solo, text="Solo")

        self.cnt = 10
        for i in range(0, self.cnt):
            e = tk.Entry(self, width=40)
            self.seq_entries.append(e)
            self.seq_entries[i].bind('<Return>', lambda event, x=i: self.set_sequence(event, x))

            s = tk.StringVar(self, "")
            label_font = ("Courier", "10")

            intvar_mute = tk.IntVar(self, True)
            mute = tk.Checkbutton(self, variable=intvar_mute)

            l = tk.Label(self, text="", textvariable=s, font=label_font)
            self.labels.append(l)
            self.strvars.append(s)
            self.mutes.append(mute)
            self.intvars_mutes.append(intvar_mute)

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

        self.strvars[channel].set(msg[:40])

    def display(self):
        offset = 5
        for i in range(self.cnt):
            self.mutes[i].grid(row=offset + i, column=9, pady=2, padx=(0, 3), sticky="w")
            self.seq_entries[i].grid(row=offset + i, column=10, pady=2, sticky="w")
            self.labels[i].grid(row=offset + i, column=11, pady=2, sticky="w")
        self.checkbutton_solo.grid(row=offset + self.cnt + 1, column=9, pady=2, sticky="w")

    def set_sequence(self, event, channel, seq=None):
        seq = event.widget.get() if seq is None else seq
        notes, str_seq = self.parser.get_notes(self.context, seq, mode=MODE_SAMPLE)

        for note in notes:
            if note:
                note[0] += channel

        print("Ch%s: (%s)\t\"%s\"" % (channel+1, len(notes), notes))

        self.context.sample_seqs[channel] = notes
        self.update_label_with_current_step(channel, 0, False)

    def mute_all(self):
        for i in range(self.cnt):
            self.intvars_mutes[i].set(False)

    def unmute_all(self):
        for i in range(self.cnt):
            self.intvars_mutes[i].set(True)

    def invert_mute(self):
        for i in range(self.cnt):
            self.intvars_mutes[i].set(not self.intvars_mutes[i].get())

    def get_all_sequences(self):
        return [entry.get() for entry in self.seq_entries]

    def insert(self, seq, idx):
        insert_into_entry(self.seq_entries[idx], seq)
