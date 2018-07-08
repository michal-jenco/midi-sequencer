import tkinter as tk

from source.akai_midimix_state import AkaiMidimixStates
from source.functions import get_note_name_from_integer


class StatusFrame(tk.Frame):
    def __init__(self, parent, sequencer):
        tk.Frame.__init__(self, parent, padx=5, pady=5)

        self.sequencer = sequencer
        self.midi_input_listener = sequencer.midi_input_listener
        self.midi_input_listener_state = self.midi_input_listener.state

        self.big_font = "Courier New", "15", "bold"
        self.small_font = "Courier New", "10"

        self.limit = 7

        self.state_colors = {AkaiMidimixStates.MAIN: "lightgreen",
                             AkaiMidimixStates.SAMPLE_FRAME: "lightgray"}

        self.frame_midi_input_listener_state = tk.Frame(self)
        self.strvar_midi_input_listener_state = tk.StringVar(self.frame_midi_input_listener_state)
        self.label_midi_input_listener_state = tk.Label(self.frame_midi_input_listener_state,
                                                        textvariable=self.strvar_midi_input_listener_state,
                                                        font=self.big_font)
        self.frame_sequence_indices = tk.Frame(self)
        self.strvar_sequence_indices = tk.StringVar(self.frame_sequence_indices)
        self.label_sequence_indices = tk.Label(self.frame_sequence_indices,
                                               textvariable=self.strvar_sequence_indices,
                                               font=self.small_font)

        self.frame_scales = tk.Frame(self)
        self.strvar_scales = tk.StringVar(self.frame_scales)
        self.label_scales = tk.Label(self.frame_scales,
                                     textvariable=self.strvar_scales,
                                     font=self.small_font)

        self.frame_roots = tk.Frame(self)
        self.strvar_roots = tk.StringVar(self.frame_roots)
        self.label_roots = tk.Label(self.frame_roots,
                                    textvariable=self.strvar_roots,
                                    font=self.small_font)

        self["bg"] = "gold"
        self._grid()
        self._init()

    def _grid(self):
        self.frame_midi_input_listener_state.grid(row=10, column=10)
        self.frame_sequence_indices.grid(row=15, column=10, pady=(10, 0))
        self.frame_scales.grid(row=20, column=10, pady=(10, 0))
        self.frame_roots.grid(row=25, column=10, pady=(10, 0))

        self.label_midi_input_listener_state.grid()
        self.label_sequence_indices.grid()
        self.label_scales.grid()
        self.label_roots.grid()

    def _init(self):
        self.update()

    def midi_input_listener_state_changed(self):
        state = self.midi_input_listener_state.get()
        value = state.center(14)
        self.strvar_midi_input_listener_state.set(value)
        self.label_midi_input_listener_state["bg"] = self.state_colors[state]

    def update_sequence_indices(self):
        msg = ""
        for i, item in enumerate(self.sequencer.step_played_counts[:self.limit]):
            msg += ("Seq %s: %s" % (i, item)).center(18) + ("\n" if i < self.limit - 1 else "")
        self.strvar_sequence_indices.set(msg)

    def update_scales(self):
        msg = ""
        for i, item in enumerate(self.sequencer.context.scales_individual[:self.limit]):
            msg += ("Seq %s: %s" % (i, item)).center(18) + ("\n" if i < self.limit - 1 else "")
        self.strvar_scales.set(msg)

    def update_roots(self):
        msg = ""
        for i, item in enumerate(self.sequencer.context.roots[:self.limit]):
            msg += ("Seq %s: %s" % (i, get_note_name_from_integer(item))).center(18) + ("\n" if i < self.limit - 1 else "")
        self.strvar_roots.set(msg)

    def update(self):
        self.midi_input_listener_state_changed()
        self.update_sequence_indices()
        self.update_scales()
        self.update_roots()