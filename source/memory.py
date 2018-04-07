import tkinter as tk

from source.constants import MemoryType


class Memory(tk.Frame):
    def __init__(self, parent, context, typ):
        tk.Frame.__init__(self, parent, padx=5, pady=5)

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

    def show(self):
        self.listbox_indices.grid(row=5, column=4, pady=2)
        self.listbox_sequences.grid(row=5, column=5, pady=2)
        self.listbox_lengths.grid(row=5, column=6, pady=2)

        self.scrollbar.grid(row=5, column=7, sticky="ens")

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

    def save(self, f):
        pass

    def load(self, f):
        pass

    def _regenerate_indices(self):
        self.listbox_indices.delete(0, tk.END)

        for i in range(0, self.listbox_sequences.size()):
            self.listbox_indices.insert(tk.END, i)

    def _regenerate_lengths(self):
        self.listbox_lengths.delete(0, tk.END)

        for i in range(0, self.listbox_sequences.size()):
            notes, _ = self.context.parser.get_notes(self.context, str(self.listbox_sequences.get(i)))
            self.listbox_lengths.insert(tk.END, str(len(notes)))

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

