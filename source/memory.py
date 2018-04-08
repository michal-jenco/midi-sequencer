import tkinter as tk
import os

from source.constants import MemoryType
from source.functions import get_date_string, log


class Memory(tk.Frame):
    def __init__(self, parent, context, typ):
        tk.Frame.__init__(self, parent, padx=5, pady=5)

        self["bg"] = "gray"

        self.context = context
        self.memory_types = MemoryType()
        self.typ = typ

        self.sequences = []
        self.note_sequences = []

        self.scrollbar = tk.Scrollbar(self, command=self._scroll_all)

        self.height = 16
        self.listbox_indices = tk.Listbox(self, width=2, height=self.height,
                                          selectmode=tk.EXTENDED, yscrollcommand=self.scrollbar.set)
        self.listbox_sequences = tk.Listbox(self, width=35, height=self.height,
                                            selectmode=tk.EXTENDED, yscrollcommand=self.scrollbar.set)
        self.listbox_lengths = tk.Listbox(self, width=3, height=self.height,
                                          selectmode=tk.EXTENDED, yscrollcommand=self.scrollbar.set)

        self.listbox_sequences.bind('<Delete>', self._delete_selection)
        self.listbox_sequences.bind('<MouseWheel>', self._scroll_all_mouse)

        self.frame_buttons = tk.Frame(self)

        self.button_save = tk.Button(self.frame_buttons, text="  S a v e  ", command=self.save)
        self.button_load = tk.Button(self.frame_buttons, text="  L o a d  ", command=self.load)
        self.button_clear_all = tk.Button(self.frame_buttons, text="  C l e a r  ", command=self.clear_all)

    def show(self):
        self.listbox_indices.grid(row=5, column=4, pady=2)
        self.listbox_sequences.grid(row=5, column=5, pady=2)
        self.listbox_lengths.grid(row=5, column=6, pady=2)

        self.scrollbar.grid(row=5, column=7, sticky="ens")

        self.frame_buttons.grid(row=15, column=4, columnspan=3, sticky="w", padx=5, pady=2)

        self.button_save.grid(row=10, column=10, sticky="w", padx=5, pady=2)
        self.button_load.grid(row=10, column=20, sticky="w", padx=5, pady=2)
        self.button_clear_all.grid(row=10, column=30, sticky="w", padx=5, pady=2)

    def add_seq(self, seq):
        self.listbox_sequences.insert(tk.END, seq)
        self._regenerate_indices()
        self._regenerate_lengths()

    def clear_all(self):
        self.listbox_sequences.delete(0, tk.END)
        self.listbox_indices.delete(0, tk.END)
        self.listbox_lengths.delete(0, tk.END)

    def get_all(self):
        size = self.listbox_sequences.size()
        result = [self.listbox_sequences.get(i, i)[0] for i in range(0, size)]
        return result

    def get_by_index(self, idx):
        try:
            result = str(self.listbox_sequences.get(idx, idx)[0])
        except:
            result = None

        return result

    def save(self):
        datestring = get_date_string(type="filename")
        filename = "-".join(datestring.split("-")[0:3]) + ".memory"
        time_ = ":".join(datestring.split("-")[3:])
        abspath = os.path.join(self.context.memory_filepath, filename)

        try:
            with open(abspath, "a") as f:
                for seq in self.get_all():
                    f.write(time_ + " " + seq + "\n")
                f.flush()

        except Exception as e:
            log("Saving memory sequences failed, because: %s" % e)

        else:
            log(msg="Sequences saved to file %s" % abspath)

    def load(self):
        pass

    def _regenerate_indices(self):
        self.listbox_indices.delete(0, tk.END)

        for i in range(0, self.listbox_sequences.size()):
            self.listbox_indices.insert(tk.END, i)

    def _regenerate_lengths(self):
        self.listbox_lengths.delete(0, tk.END)

        for i in range(0, self.listbox_sequences.size()):
            self.listbox_lengths.insert(tk.END, str(len(self.listbox_sequences.get(i))))

    def _delete_selection(self, _):
        items = self.listbox_sequences.curselection()

        for pos, i in enumerate(items):
            idx = int(i) - pos
            self.listbox_sequences.delete(idx, idx)

        self._regenerate_indices()
        self._regenerate_lengths()

    def _scroll_all(self, *args):
        self.listbox_indices.yview(*args)
        self.listbox_sequences.yview(*args)
        self.listbox_lengths.yview(*args)

    def _scroll_all_mouse(self, event):
        arg = -event.delta // 120*5, "units"
        self.listbox_indices.yview_scroll(*arg)
        self.listbox_sequences.yview_scroll(*arg)
        self.listbox_lengths.yview_scroll(*arg)

