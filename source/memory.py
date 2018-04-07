import tkinter as tk

from source.constants import MemoryType


class Memory(tk.Frame):
    def __init__(self, parent, context, typ):
        tk.Frame.__init__(self, parent, padx=5, pady=5)

        self.context = context
        self.memory_types = MemoryType()
        self.typ = typ

        self.sequences = []

        self.listbox_indices = tk.Listbox(self, width=2)
        self.listbox_sequences = tk.Listbox(self, width=35)

    def show(self):
        self.listbox_indices.grid(row=5, column=4, pady=2)
        self.listbox_sequences.grid(row=5, column=5, pady=2)

    def add_seq(self, seq):
        self.listbox_sequences.insert(tk.END, seq)

        idx = str(self.listbox_sequences.size() - 1)
        self.listbox_indices.insert(tk.END, idx)

    def clear_all(self):
        self.listbox_sequences.delete(0, tk.END)
        self.listbox_indices.delete(0, tk.END)

    def get_all(self):
        return "Not implemented yet."
