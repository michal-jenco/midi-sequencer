import tkinter as tk

from source.constants import MemoryType


class Memory(tk.Frame):
    def __init__(self, parent, context, typ):
        tk.Frame.__init__(self, parent, padx=5, pady=5)

        self.context = context
        self.memory_types = MemoryType()
        self.typ = typ

        self.sequences = []

        self.scrollbar = tk.Scrollbar(self, command=self._scroll_both)

        self.height = 16
        self.listbox_indices = tk.Listbox(self, width=2, height=self.height,
                                          selectmode=tk.EXTENDED, yscrollcommand=self.scrollbar.set)
        self.listbox_sequences = tk.Listbox(self, width=35, height=self.height,
                                            selectmode=tk.EXTENDED, yscrollcommand=self.scrollbar.set)

        self.listbox_sequences.bind('<Delete>', self._delete_selection)
        self.listbox_sequences.bind('<MouseWheel>', self._scroll_both_mouse)

    def _scroll_both(self, *args):
        self.listbox_indices.yview(*args)
        self.listbox_sequences.yview(*args)

    def _scroll_both_mouse(self, event):
        arg = -event.delta // 120, "units"
        self.listbox_indices.yview_scroll(*arg)
        self.listbox_sequences.yview_scroll(*arg)

    def show(self):
        self.listbox_indices.grid(row=5, column=4, pady=2)
        self.listbox_sequences.grid(row=5, column=5, pady=2)

        self.scrollbar.grid(row=5, column=6, sticky="ens")

    def add_seq(self, seq):
        self.listbox_sequences.insert(tk.END, seq)

        idx = str(self.listbox_sequences.size() - 1)
        self.listbox_indices.insert(tk.END, idx)

    def clear_all(self):
        self.listbox_sequences.delete(0, tk.END)
        self.listbox_indices.delete(0, tk.END)

    def get_all(self):
        return "Not implemented yet."

    def save(self):
        pass

    def load(self):
        pass

    def _regenerate_indices(self):
        self.listbox_indices.delete(0, tk.END)

        for i in range(0, self.listbox_sequences.size()):
            self.listbox_indices.insert(tk.END, i)

    def _delete_selection(self, _):
        items = self.listbox_sequences.curselection()

        for pos, i in enumerate(items):
            idx = int(i) - pos
            self.listbox_sequences.delete(idx, idx)

        self._regenerate_indices()

