import random
import hashlib

from source.scales import Scales
from source.constants import *


class Parser:
    def __init__(self):
        pass

    def get_notes(self, context, text, mode=MODE_SIMPLE):

        print("text inside: %s\n" % text)

        msg_list = []
        str_seq = ""

        if mode == MODE_SIMPLE:
            separator = " "

            if separator in text:
                seq = text.split(separator)[0]
                control = text.split(separator)[1]
            else:
                seq = text
                control = None

            print("Control: %s" % control)

            notes = list(seq)
            seq_length = len(notes)

            for idx, note in enumerate(notes):
                msg = [0x90]

                if note.isdigit():
                    oct_ = self.parse_plus_minus(notes, idx)
                    flat_sharp = self.parse_flat_sharp(notes, idx)

                    if oct_ == -12:
                        add = "-"
                    elif oct_ == 0:
                        add = ""
                    elif oct_ == 12:
                        add = "+"

                    note_value = Scales.get_note_by_index_wrap(int(note), context.scale)
                    str_seq += str(context.scale.index(note_value)) + add + \
                               ({"-1": "f", "0": "", "1": "s"}[str(flat_sharp)]) + " "
                    note_value += context.root + self.get_octave(control) + oct_ + flat_sharp
                    msg.append(note_value)
                    msg.append(100)
                    msg_list.append(msg)

                elif note == "r":
                    oct_ = self.parse_plus_minus(notes, idx)
                    flat_sharp = self.parse_flat_sharp(notes, idx)

                    if oct_ == -12:
                        add = "-"
                    elif oct_ == 0:
                        add = ""
                    elif oct_ == 12:
                        add = "+"

                    note_value = random.choice(context.scale)
                    str_seq += str(context.scale.index(note_value)) + add + \
                               ({"-1": "f", "0": "", "1": "s"}[str(flat_sharp)]) + " "

                    note_value += context.root + self.get_octave(control) + oct_ + flat_sharp
                    msg.append(note_value)
                    msg.append(100)

                    msg_list.append(msg)

                elif note == ",":
                    for i in range(0, context.comma_pause):
                        msg_list.append([0x90, NOTE_PAUSE, 0])
                        str_seq += note

                elif note == ".":
                    for i in range(0, context.dot_pause):
                        msg_list.append([0x90, NOTE_PAUSE, 0])
                        str_seq += ","

                elif note == "=":
                    for i in range(0, context.dash_pause):
                        msg_list.append([0x90, NOTE_PAUSE, 0])
                        str_seq += ","

                elif note == "&":
                    count = random.randint(context.amper_min, context.amper_max)
                    for i in range(0, count):
                        msg_list.append([0x90, NOTE_PAUSE, 0])
                        str_seq += ","

                elif note == "*":
                    pass

                elif note == "/":
                    msg_list.append([0x90, GO_TO_START, 0])

                elif note == "§":
                    count = random.randint(context.paragraph_min, context.paragraph_max)
                    for i in range(0, count):
                        note_value = random.choice(context.scale)
                        str_seq += str(context.scale.index(note_value)) + " "

                        note_value += context.root + self.get_octave(control)
                        msg_list.append([0x90, note_value, 100])

                elif note == ";":
                    pass

                elif note == "+":
                    pass

                elif note.isalpha():
                    pass
                    """
                    idx = ord(hashlib.sha256(note.encode('utf-8')).hexdigest()[0])
                    note_value = Scales().get_note_by_index_wrap(idx, context.scale)
                    str_seq += str(context.scale.index(note_value)) + " "

                    print("%s: %s" % (note, str(note_value)))

                    note_value += context.root + self.get_octave(control)
                    msg_list.append([0x90, note_value, 100])
                    """

        elif mode == MODE_SAMPLE:
            sequences = text.split()

            repetitions = 1
            for seq in sequences:
                if "x" in seq:
                    x_index = seq.index("x")
                    if seq[x_index+1:]:
                        repetitions = int(seq[x_index+1:])

                else:
                    repetitions = 1

                try:
                    x_index
                    notes = list(seq[:x_index])
                except:
                    notes = list(seq)

                for i in range(0, repetitions):
                    for idx, note in enumerate(notes):

                        if note == "0":
                            msg_list.append([])

                        elif note == "1":
                            msg_list.append([0x90, 127, 127])

                        elif note.isdigit() and note not in {"0", "1"}:
                            for i in range(0, int(note)):
                                msg_list.append([])

        print("Sequence set to: %s\n" % msg_list)

        if mode == MODE_SIMPLE:
            context.sequence = msg_list
            context.str_sequence = str_seq

        return msg_list

    @staticmethod
    def get_octave(control):
        octave = 0

        if not control:
            return 0

        elif "o" in control:
            pos_plus = control.find("+")
            pos_minus = control.find("-")

            if pos_plus > -1:
                plus_octaves = int(control[pos_plus + 1])
                octave = plus_octaves * 12
            else:
                plus_octaves = 0

            if pos_minus > -1:
                minus_octaves = int(control[pos_minus + 1])
                octave = minus_octaves * (-12)
            else:
                minus_octaves = 0

            if "ro" in control:
                octave_selection = [0]

                for i in range(1, minus_octaves + 1):
                    octave_selection.append(-12 * i)

                for i in range(1, plus_octaves + 1):
                    octave_selection.append(12 * i)

                octave = random.choice(octave_selection)
        return octave

    @staticmethod
    def parse_plus_minus(notes, idx):
        try:
            if notes[idx + 1] == "+":
                oct_ = 12
            elif notes[idx + 1] == "-":
                oct_ = -12
            else:
                oct_ = 0

        except IndexError:
            oct_ = 0

        return oct_

    @staticmethod
    def parse_flat_sharp(notes, idx):
        offset = 0

        try:
            if notes[idx + 1] == "s" or (
                    idx + 2 < len(notes) and notes[idx + 2] == "s" and notes[idx + 1] in {"+", "-"}):
                offset = 1
            elif notes[idx + 1] == "f" or (
                    idx + 2 < len(notes) and notes[idx + 2] == "f" and notes[idx + 1] in {"+", "-"}):
                offset = -1
            else:
                offset = 0

        except IndexError:
            offset = 0

        return offset
