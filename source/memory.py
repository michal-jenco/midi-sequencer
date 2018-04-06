import tkinter as tk

from source.constants import MemoryType


class Memory(tk.Frame):
    def __init__(self, parent, context, typ):
        tk.Frame.__init__(self, parent, padx=5, pady=5)

        self.context = context
        self.memory_types = MemoryType()
        self.typ = typ

    def show(self):
        pass
