import tkinter as tk

from source.akai_state import AkaiMidimixStateNames
from source.functions import get_note_name_from_integer


class StatusFrame(tk.Frame):
    def __init__(self, parent, sequencer):
        tk.Frame.__init__(self, parent, padx=5, pady=5)

        self.sequencer = sequencer
        self.context = self.sequencer.context
        self.midi_input_listener = sequencer.midi_input_listener

        self.big_font = "Courier New", "15", "bold"
        self.small_font = "Courier New", "10"

        self.limit = 7

        self.state_colors = {AkaiMidimixStateNames.MAIN: "lightgreen", AkaiMidimixStateNames.SAMPLE_FRAME: "lightgray"}
        self.mode_colors = {True: "lightgreen", False: "orange"}

        self.frame_midi_input_listener_state = tk.Frame(self)
        self.strvar_midi_input_listener_state = tk.StringVar(self.frame_midi_input_listener_state)
        self.label_midi_input_listener_state = tk.Label(self.frame_midi_input_listener_state,
                                                        textvariable=self.strvar_midi_input_listener_state,
                                                        font=self.big_font)
        self.frame_scale_mode = tk.Frame(self)
        self.strvar_scale_mode = tk.StringVar(self.frame_scale_mode)
        self.label_scale_mode = tk.Label(self.frame_scale_mode, textvariable=self.strvar_scale_mode, font=self.big_font)

        self.frame_sequence_indices = tk.Frame(self)
        self.strvar_sequence_indices = tk.StringVar(self.frame_sequence_indices)
        self.label_sequence_indices = tk.Label(self.frame_sequence_indices, textvariable=self.strvar_sequence_indices,
                                               font=self.small_font)
        self.frame_scales = tk.Frame(self)
        self.strvar_scales = tk.StringVar(self.frame_scales)
        self.label_scales = tk.Label(self.frame_scales, textvariable=self.strvar_scales, font=self.small_font)

        self.frame_roots = tk.Frame(self)
        self.strvar_roots = tk.StringVar(self.frame_roots)
        self.label_roots = tk.Label(self.frame_roots, textvariable=self.strvar_roots, font=self.small_font)

        self.strvar_sequence_lengths = tk.StringVar(self)
        self.label_sequence_lengths = tk.Label(self, textvariable=self.strvar_sequence_lengths, font="courier 8")

        self["bg"] = "gold"
        self._grid()
        self._init()

    def _grid(self):
        self.frame_midi_input_listener_state.grid(row=10, column=10)
        self.frame_scale_mode.grid(row=11, column=10, pady=(10, 0))
        self.frame_sequence_indices.grid(row=15, column=10, pady=(10, 0))
        self.frame_scales.grid(row=20, column=10, pady=(10, 0))
        self.frame_roots.grid(row=25, column=10, pady=(10, 0))

        self.label_midi_input_listener_state.grid()
        self.label_scale_mode.grid()
        self.label_sequence_indices.grid()
        self.label_scales.grid()
        self.label_roots.grid()
        self.label_sequence_lengths.grid(column=10, pady=(10, 0))

    def _init(self):
        self.update()

    def midi_input_listener_state_changed(self):
        state = self.midi_input_listener.akai_state_midimix.get()
        value = state.center(14)
        self.strvar_midi_input_listener_state.set(value)
        self.label_midi_input_listener_state["bg"] = self.state_colors[state]

    def _update_sequence_indices(self):
        msg = ""
        for i, item in enumerate(self.sequencer.step_played_counts[:self.limit]):
            msg += ("Seq %s: %s" % (i, item)).center(18) + ("\n" if i < self.limit - 1 else "")
        self.strvar_sequence_indices.set(msg)

    def _update_scales(self):
        msg = ""
        for i, item in enumerate(self.context.current_scales[:self.limit]):
            msg += ("Seq %s: %s" % (i, item)).center(18) + ("\n" if i < self.limit - 1 else "")
        self.strvar_scales.set(msg)

    def _update_roots(self):
        msg = ""
        for i, item in enumerate(self.context.roots[:self.limit]):
            msg += ("Seq %s: %s" % (i, get_note_name_from_integer(item))).center(18)\
                   + ("\n" if i < self.limit - 1 else "")
        self.strvar_roots.set(msg)

    def update_scale_mode(self):
        self.strvar_scale_mode.set(("Scale mode: %s"
                                   % ("ON" if self.context.scale_mode_changing_on else "OFF")).center(16))
        self.label_scale_mode["bg"] = self.mode_colors[self.context.scale_mode_changing_on]

    def update_sequence_lengths(self):
        self.strvar_sequence_lengths.set((" | ".join([str(len(seq)) for seq in self.context.note_sequences])).center(30))

    def update(self):
        self.midi_input_listener_state_changed()
        self.update_scale_mode()
        self._update_sequence_indices()
        self._update_scales()
        self._update_roots()
        self.update_sequence_lengths()