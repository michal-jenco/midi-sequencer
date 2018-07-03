import tkinter as tk


class StatusFrame(tk.Frame):
    def __init__(self, parent, context, akai_midimix_state):
        tk.Frame.__init__(self, parent, padx=5, pady=5)
        self["bg"] = "darkred"
        self.context = context
        self.akai_midimix_state = akai_midimix_state
