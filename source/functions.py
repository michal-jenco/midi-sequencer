import datetime
import tkinter as tk

from source.constants import StringConstants


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


def insert_into_entry(entry, seq):
    entry.delete(0, tk.END)
    entry.insert(0, seq)


def range_to_range(r1, r2, value):
    """Scale value with range1 to range2"""

    OldMin, OldMax = r1
    NewMin, NewMax = r2

    OldRange = OldMax - OldMin

    if OldRange == 0:
        NewValue = NewMin

    else:
        NewRange = NewMax - NewMin
        NewValue = (((value - OldMin) * NewRange) / OldRange) + NewMin

    return NewValue


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
