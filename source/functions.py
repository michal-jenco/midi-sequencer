import os
import time
import datetime
import tkinter as tk

from source.note_object import NoteObject
from source.note_container import NoteContainer
from source.constants import StringConstants
from source.note_types import NoteTypes


def log(logfile=None, msg=""):
    result = "[%s]: \"%s\"" % (str(datetime.datetime.now()), msg)

    if logfile is not None:
        logfile.write(result)
        logfile.flush()
    print(result)


def get_date_string(type):
    result = ""

    if type == "filename":
        result = str(datetime.datetime.now()).split(".")[0].replace(":", "-").replace(" ", "-")
    return result


def timeit(method):
    def timed(*args, **kw):
        start = time.time()
        result = method(*args, **kw)
        end = time.time()
        print('%r  %2.2f ms' % (method.__name__, (end - start) * 1000))
        return result
    return timed


def insert_into_entry(entry, seq):
    entry.delete(0, tk.END)
    entry.insert(0, seq)


def range_to_range(r1, r2, value, cast=None):
    """Scale value with range1 to range2."""

    old_min, old_max = r1
    new_min, new_max = r2
    old_range = old_max - old_min

    if old_range == 0:
        result = new_min
    else:
        new_range = new_max - new_min
        result = (((value - old_min) * new_range) / old_range) + new_min

    if cast:
        return cast(result)
    return result


def rotate(list_, n):
    return list_[-n:] + list_[:-n]


def get_note_name_from_integer(note_int):
    note_letters = ["C", "Db", "D", "Eb", "E", "F", "F#", "G", "Ab", "A", "Bb", "B"]
    return "%s%s" % (note_letters[note_int % 12], note_int // 12 - 2)


def get_inverse_dict(dic):
    return {value: key for key, value in dic.items()}


def get_all_indices(in_, of=StringConstants.multiple_entry_separator):
    return [i for i, ltr in enumerate(in_) if ltr == of]


def get_closest_index_of(indices, value):
    distance, distance_idx = 9999999, 0

    for i, index in enumerate(indices):
        if abs(value - index) < distance:
            distance = abs(value - index)
            distance_idx = i

    return distance_idx


def convert_midi_notes_to_note_objects(context, midi_notes):
    result = []

    for note in midi_notes:
        if isinstance(note, list):
            ch, pitch, vel = note

            result.append(
                NoteObject(context=context,
                           channel=ch,
                           pitch=pitch if isinstance(pitch, int) else None,
                           velocity=vel,
                           type_=NoteTypes.NORMAL if isinstance(pitch, int) else pitch))

        elif isinstance(note, NoteContainer):
            result.append(note)
    return result


def print_dict(d):
    for key, value in d.items():
        print("\"{}\": \"{}\"".format(key, value))