import tkinter as tk

from parser_my import Parser
from constants import MODE_SAMPLE


class SampleFrame(tk.Frame):
    def __init__(self, parent, context):
        tk.Frame.__init__(self, parent, padx=5, pady=5)

        self.context = context

        self.seq_entries = []

        for i in range(0, 10):
            e = tk.Entry(self)
            e.bind('<Return>', lambda event, x=i: self.set_sequence(event, x))

            self.seq_entries.append(e)

    def display(self):

        offset = 5
        for i, e in enumerate(self.seq_entries):
            e.grid(row=offset + i, column=10, pady=2)

    def set_sequence(self, event, channel):

        parser = Parser()
        notes = parser.get_notes(self.context, event.widget.get(), mode=MODE_SAMPLE)

        for note in notes:
            if note:
                note[0] += channel

        print("Ch%s: (%s)\t\"%s\"" % (channel+1, len(notes), notes))

        self.context.sample_seqs[channel] = notes
        print("a: %s" % (self.context.sample_seqs[channel]))
