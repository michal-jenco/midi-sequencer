import tkinter as tk


class StatusFrame(tk.Frame):
    def __init__(self, parent, sequencer):
        tk.Frame.__init__(self, parent, padx=5, pady=5)

        self.sequencer = sequencer
        self.midi_input_listener = sequencer.midi_input_listener
        self.midi_input_listener_state = self.midi_input_listener.state

        self.big_font = "Courier New", "15", "bold"

        self.frame_midi_input_listener_state = tk.Frame(self)
        self.strvar_midi_input_listener_state = tk.StringVar(self.frame_midi_input_listener_state)
        self.label_midi_input_listener_state = tk.Label(self.frame_midi_input_listener_state,
                                                        textvariable=self.strvar_midi_input_listener_state,
                                                        font=self.big_font)

        self["bg"] = "gold"
        self._grid()
        self._init()

    def _grid(self):
        self.frame_midi_input_listener_state.grid(row=10, column=10)

        self.label_midi_input_listener_state.grid()

    def _init(self):
        self.label_midi_input_listener_state["bg"] = "darkorange"
        self.midi_input_listener_state_changed()

    def midi_input_listener_state_changed(self):
        value = self.midi_input_listener_state.get().center(14)
        self.strvar_midi_input_listener_state.set(value)
