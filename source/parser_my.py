import random
import itertools

from source.scales import Scales
from source.constants import note_dict as constants_note_dict
from source.constants import MODE_SAMPLE, MODE_SIMPLE, NOTE_PAUSE, GO_TO_START


class Parser:
    def __init__(self):
        pass

    def get_notes(self, context, text, iii=None, mode=MODE_SIMPLE):

        # print("text inside: %s\n" % text)

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

            # print("Control: %s" % control)

            notes = list(seq)
            seq_length = len(notes)

            perm_char = "p"
            skipping_permutations = False

            for idx, note in enumerate(notes):

                if skipping_permutations:
                    if note != perm_char:
                        continue
                    else:
                        skipping_permutations = False
                        continue

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

                    note_value = Scales.get_note_by_index_wrap(int(note), context.scales.get_scale_by_name(context.scales_individual[iii]))
                    str_seq += (str(context.scales.get_scale_by_name(context.scales_individual[iii]).index(note_value))
                                + add + ({"-1": "f", "0": "", "1": "s"}[str(flat_sharp)]) + " ")
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

                    note_value = random.choice(context.scales.get_scale_by_name(context.scales_individual[iii])[:9])
                    str_seq += (str(context.scales.get_scale_by_name(context.scales_individual[iii]).index(note_value))
                                + add + ({"-1": "f", "0": "", "1": "s"}[str(flat_sharp)]) + " ")

                    note_value += context.root + self.get_octave(control) + oct_ + flat_sharp
                    msg.append(note_value)
                    msg.append(100)

                    msg_list.append(msg)

                elif note == perm_char:
                    idx_end_p = notes[idx + 1:].index(perm_char)
                    perm_content = notes[idx + 1: idx + idx_end_p + 1]

                    if ";" in perm_content:
                        perm_content_notes = perm_content[:perm_content.index(";")]
                        perm_content_control = "".join(perm_content[perm_content.index(";")+1:])
                    else:
                        perm_content_notes = perm_content
                        perm_content_control = None

                    length = self.parse_param("l", perm_content_control)
                    start = self.parse_param("s", perm_content_control)
                    random_order = self.parse_param("r", perm_content_control)
                    count_of_permutations = self.parse_param("c", perm_content_control)
                    perm_len = self.parse_param("L", perm_content_control)

                    _, str_repr = self.get_notes(context, perm_content_notes, mode=MODE_SIMPLE)
                    str_seq_internal = self.parse_permutations(str_repr.replace(" ", ""),
                                                               random_order=random_order,
                                                               output_length=length,
                                                               start=start,
                                                               perm_len=perm_len)
                    perm_notes, str_repr = self.get_notes(context, str_seq_internal, mode=MODE_SIMPLE)

                    for n in perm_notes:
                        if n[1] != NOTE_PAUSE:
                            msg_list.append([n[0], n[1] + self.get_octave(control), n[2]])
                        else:
                            msg_list.append([n[0], n[1], n[2]])

                    str_seq += str_repr
                    skipping_permutations = True

                elif note == ",":
                    for i in range(0, context.comma_pause):
                        msg_list.append([0x90, NOTE_PAUSE, 0])
                        str_seq += " %s " % note

                elif note == ".":
                    for i in range(0, context.dot_pause):
                        msg_list.append([0x90, NOTE_PAUSE, 0])
                        str_seq += " , "

                elif note == "=":
                    for i in range(0, context.dash_pause):
                        msg_list.append([0x90, NOTE_PAUSE, 0])
                        str_seq += " , "

                elif note == "&":
                    count = random.randint(context.amper_min, context.amper_max)
                    for i in range(0, count):
                        msg_list.append([0x90, NOTE_PAUSE, 0])
                        str_seq += " , "

                elif note == "/":
                    msg_list.append([0x90, GO_TO_START, 0])

                elif note == "§":
                    count = random.randint(context.paragraph_min, context.paragraph_max)
                    for i in range(0, count):
                        note_value = random.choice(context.scales_individual[iii])
                        str_seq += str(context.scales_individual[iii].index(note_value)) + " "

                        note_value += context.root + self.get_octave(control)
                        msg_list.append([0x90, note_value, 100])

                elif note.isalpha():
                    pass
                    """
                    idx = ord(hashlib.sha256(note.encode('utf-8')).hexdigest()[0])
                    note_value = context.scales.get_note_by_index_wrap(idx, context.scale)
                    str_seq += str(context.scale.index(note_value)) + " "

                    print("%s: %s" % (note, str(note_value)))

                    note_value += context.root + self.get_octave(control)
                    msg_list.append([0x90, note_value, 100])
                    """

        elif mode == MODE_SAMPLE:
            sequences = text.split()

            repetitions = 1
            for seq in sequences:

                if seq == "/":
                    break

                elif "x" in seq:
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

                        else:
                            # unknown symbol (not yet defined a use)
                            pass

        return msg_list, str_seq.replace("  ", " ")

    @staticmethod
    def parse_permutations(seq, output_length=None, start=0, random_order=False, count=None, perm_len=None):
        individual_permutations = ["".join(x) for x in itertools.permutations(seq, perm_len)]

        if start is None:
            start = 0

        if random_order:
            random.shuffle(individual_permutations)

        if count is not None:
            individual_permutations = individual_permutations[:count]

        output_string = "".join(individual_permutations)

        if not output_length:
            output_length = len(output_string)

        return output_string[start:start + output_length]

    @staticmethod
    def parse_param(param, seq):
        repetitions = None

        if not seq:
            return None

        if param in seq:
            param_index = seq.rindex(param)
            if seq[param_index + 1:] and not seq[param_index + 1].isalpha():

                next_param_index = None

                for i, char in enumerate(seq[param_index + 1:]):
                    if char.isalpha():
                        next_param_index = i + param_index + 1
                        break

                if next_param_index is None:
                    repetitions = int(seq[param_index + 1:])
                else:
                    repetitions = int(seq[param_index + 1:next_param_index])
            else:
                repetitions = True

        elif param == "x" and param not in seq:
            repetitions = 1

        return repetitions

    def parse_off_array(self, text):
        result = []
        sequences = list(text.split())

        for seq in sequences:
            times = self.parse_param("x", str(seq))

            if "x" in seq:
                idx = seq.index("x")
                seq = seq[0:idx]

            for i in range(0, times):
                result.append(int(seq))

        return result

    def parse_octave_sequence(self, text):
        result = []

        if not text:
            return []

        sequences = list(text.split())

        for seq in sequences:
            times = self.parse_param("x", str(seq))

            for i in range(0, times):
                if seq.startswith(("+", "-")):
                    result.append(int(seq[0:2])*12)
                else:
                    result.append(int(seq[0])*12)

        return result

    def parse_midi_channels(self, text):
        return list(map(int, text.split()))

    def parse_memory_sequence(self, text):
        result = []

        if not text:
            return []

        sequences = list(text.split())

        for seq in sequences:
            times = self.parse_param("x", str(seq))

            if "x" in seq:
                idx = seq.index("x")
                seq = seq[0:idx]

            for i in range(0, times):
                result.append(int(seq))

        return result

    def parse_root_sequence(self, text):
        result = []
        sequences = list(text.split())

        note_dict = constants_note_dict

        for seq in sequences:
            times = self.parse_param("x", str(seq))

            if "x" in seq:
                idx = seq.index("x")
                seq = seq[0:idx]

            for i in range(0, times):
                if seq in note_dict:
                    result.append(note_dict[seq])
                else:
                    print("Invalid root skipped: %s" % seq)

        return result

    def parse_scale_sequence(self, context, text):
        result = []
        sequences = list(text.split())
        available_scales = context.scales.get_all()

        for seq in sequences:
            times = self.parse_param("x", str(seq))

            if "x" in seq:
                idx = seq.rindex("x")
                seq = seq[0:idx]

            if seq in available_scales:
                for i in range(0, times):
                    result.append(seq)

            else:
                print("Scale %s does not exist." % seq)

        return result

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

    def parse_multiple_sequences_separated(self, separator, sequences):
        if separator not in sequences:
            return [sequences]

        else:
            try:
                result = sequences.split(separator)
                return result

            except Exception as e:
                print("Could not parse_multiple_sequences_separated(self, separator, sequences), because: %s" % e)
                return []