import random
import itertools
import traceback
from pyparsing import nestedExpr

from source.note_object import (NoteTypes, TupletTypes, NoteContainer, NoteDurationTypes,
                                convert_midi_notes_to_note_objects, gap_count_dict, NoteSchedulingObject)
from source.constants import note_dict as constants_note_dict, StringConstants
from source.constants import MODE_SAMPLE, MODE_SIMPLE
from source.functions import timeit
from source._____G_e__n_e__r_a__t_o__r_________ import _____G_e__n_e__r_a__t_o__r_________


class Parser:
    def __init__(self, context):
        self.context = context
        self.string_constants = StringConstants

    @staticmethod
    def _note_is_container_boundary(note):
        return note in TupletTypes.MAP.keys() and note != TupletTypes.SEPTUPLET

    @staticmethod
    def _note_is_generator_boundary(note):
        return note is StringConstants.generator_delimiter

    
    def get_notes(self, context, text, iii=None, mode=MODE_SIMPLE):
        msg_list = []
        str_seq = ""
        parsing_container = False
        parsing_generator = False
        container_type = None

        if mode == MODE_SIMPLE:
            separator = " "

            if separator in text:
                seq = text.split(separator)[0]
                control = text.split(separator)[1]
            else:
                seq = text
                control = None

            notes = list(seq)
            perm_char = "p"
            skipping_permutations = False

            for idx, note in enumerate(notes):
                if skipping_permutations:
                    if note == perm_char:
                        skipping_permutations = False
                    continue

                msg = [0x90]

                if parsing_generator:
                    if self._note_is_generator_boundary(note):
                        parsing_generator = False
                    continue

                if self._note_is_generator_boundary(note):
                    if not parsing_generator:
                        parsing_generator = True

                    generator_content = "".join(notes[idx + 1:notes[idx + 1:].index(note) + idx + 1])
                    gen = _____G_e__n_e__r_a__t_o__r_________(generator_content)
                    entry_box_repr = gen.get_entrybox_repr()

                    # print("generator_content: %s" % generator_content)
                    # print("generator: %s" % gen)
                    # print("entry_box_repr: %s" % entry_box_repr)

                    str_seq += " ".join([char for char in entry_box_repr])
                    to_append = self.get_notes(context=context,
                                               text=entry_box_repr,
                                               iii=iii)[0]
                    # print("to_append: %s" % to_append)

                    for midi_note in to_append:
                        msg_list.append(midi_note)

                if parsing_container:
                    if self._note_is_container_boundary(note):
                        parsing_container = False
                    continue

                if self._note_is_container_boundary(note):
                    if not parsing_container:
                        parsing_container = True
                        container_type = TupletTypes.MAP[note]
                        container_content = "".join(notes[idx + 1:notes[idx + 1:].index(note) + idx + 1])

                        if StringConstants.container_separator in container_content:
                            container_note_characters = container_content.split(
                                StringConstants.container_separator)[0]
                            gap_duration = container_content.split(StringConstants.container_separator)[1].lower()
                        else:
                            container_note_characters = container_content
                            gap_duration = None

                        container_notes, container_str_seq = self.get_notes(context=context,
                                                                            text=container_note_characters,
                                                                            iii=iii)
                        print("Container type: %s" % container_type)
                        print("Container content: %s" % container_content)
                        print("Container notes: %s" % container_notes)
                        print("Gap duration: %s" % gap_duration)

                        default_length = "%s%s" % (16, note)
                        length = (default_length if
                                  (gap_duration is None or gap_duration not in NoteDurationTypes.MAP.keys())
                                  else gap_duration)
                        note_objects = convert_midi_notes_to_note_objects(context, container_notes)
                        str_seq += " %s " % (container_str_seq[0] if container_str_seq[0].isdigit() else 0)

                        print("Note_objects: %s" % note_objects)
                        note_container = NoteContainer(context=context, notes=note_objects,
                                                       gaps=[NoteDurationTypes.MAP[length]] * gap_count_dict[note])
                        note_container.supply_scheduling_object(NoteSchedulingObject(length))
                        msg_list.append(note_container)
                    continue

                if note.isdigit() or note in {"a", "b", "c", "d", "e"}:
                    oct_ = self.parse_plus_minus(notes, idx)
                    flat_sharp = self.parse_flat_sharp(notes, idx)
                    add = self.get_plus_or_minus_add(oct_)

                    scale_list = context.scales.get_scale_by_name(context.current_scales[iii])
                    note_value = context.scales.get_note_by_index_wrap(int(note, 16), scale_list)
                    str_seq += (str(scale_list.index(note_value))
                                + add + ({"-1": "f", "0": "", "1": "s"}[str(flat_sharp)]) + " ")
                    note_value += context.root + self.get_octave(control) + oct_ + flat_sharp
                    velocity = 100
                    msg.append(note_value)
                    msg.append(velocity)
                    msg_list.append(msg)

                elif note == "r":
                    oct_ = self.parse_plus_minus(notes, idx)
                    flat_sharp = self.parse_flat_sharp(notes, idx)
                    add = self.get_plus_or_minus_add(oct_)

                    note_value = random.choice(context.scales.get_scale_by_name(context.current_scales[iii])[:9])
                    str_seq += (str(context.scales.get_scale_by_name(context.current_scales[iii]).index(note_value))
                                + add + ({"-1": "f", "0": "", "1": "s"}[str(flat_sharp)]) + " ")

                    note_value += context.root + self.get_octave(control) + oct_ + flat_sharp
                    velocity = 100
                    msg.append(note_value)
                    msg.append(velocity)
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

                    _, str_repr = self.get_notes(context, perm_content_notes, mode=MODE_SIMPLE, iii=iii)
                    str_seq_internal = self.parse_permutations(str_repr.replace(" ", ""),
                                                               random_order=random_order,
                                                               output_length=length,
                                                               start=start,
                                                               perm_len=perm_len)
                    perm_notes, str_repr = self.get_notes(context, str_seq_internal, mode=MODE_SIMPLE, iii=iii)

                    for n in perm_notes:
                        if n[1] != NoteTypes.NOTE_PAUSE:
                            msg = [n[0], n[1] + self.get_octave(control), n[2]]
                        else:
                            msg = [n[0], n[1], n[2]]
                    msg_list.append(msg)

                    str_seq += str_repr
                    skipping_permutations = True

                elif note == ",":
                    for i in range(0, context.comma_pause):
                        msg_list.append([0x90, NoteTypes.NOTE_PAUSE, 0])
                        str_seq += " %s " % note

                elif note == ".":
                    for i in range(0, context.dot_pause):
                        msg_list.append([0x90, NoteTypes.NOTE_PAUSE, 0])
                        str_seq += " , "

                elif note == "=":
                    for i in range(0, context.dash_pause):
                        msg_list.append([0x90, NoteTypes.NOTE_PAUSE, 0])
                        str_seq += " , "

                elif note == "&":
                    count = random.randint(context.amper_min, context.amper_max)
                    for i in range(0, count):
                        msg_list.append([0x90, NoteTypes.NOTE_PAUSE, 0])
                        str_seq += " , "

                elif note == "/":
                    msg_list.append([0x90, NoteTypes.GO_TO_START, 0])

                elif note == "§":
                    count = random.randint(context.paragraph_min, context.paragraph_max)

                    for i in range(0, count):
                        note_value = random.choice(context.current_scales[iii])
                        str_seq += str(context.current_scales[iii].index(note_value)) + " "
                        note_value += context.root + self.get_octave(control)
                        msg_list.append([0x90, note_value, 100])

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
                            for _ in range(0, int(note)):
                                msg_list.append([])
                        else:
                            # unknown symbol (not yet defined a use)
                            pass

        return msg_list, str_seq.replace("  ", " ")

    @staticmethod
    def get_plus_or_minus_add(oct_):
        return {-12: "-", 0: "", 12: "+"}[oct_]

    @staticmethod
    def parse_permutations(seq, output_length=None, start=0, random_order=False, count=None, perm_len=None):
        print("seq: %s" % seq)
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
                repetitions = None

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

            for i in range(times):
                result.append(int(seq))

        return result

    def parse_octave_sequence(self, text):
        result = []

        if not text:
            return []

        sequences = list(text.split())

        for seq in sequences:
            times = self.parse_param("x", str(seq))

            if self.is_pointer(seq):
                return self.context.octave_sequences[self.get_pointer_destination(seq)]

            for i in range(times):
                if seq.startswith(("+", "-")):
                    result.append(int(seq[0:2])*12)
                else:
                    result.append(int(seq[0])*12)

        return result

    def parse_transpose_sequence(self, text):
        result = []

        if not text:
            return []

        sequences = list(text.split())

        for seq in sequences:
            times = self.parse_param("x", str(seq))

            if "x" in seq:
                seq = seq[:seq.index("x")]

            if self.is_pointer(seq):
                return self.context.transpose_sequences[self.get_pointer_destination(seq)]

            for i in range(times):
                result.append(int(seq))

        return result

    def parse_pitch_shift_sequence(self, text):
        result = []

        if not text:
            return []

        sequences = list(text.split())

        for seq in sequences:
            times = self.parse_param("x", str(seq))

            if "x" in seq:
                seq = seq[:seq.index("x")]

            if self.is_pointer(seq):
                return self.context.pitch_shift_sequences[self.get_pointer_destination(seq)]

            for i in range(times):
                result.append(seq)

        return result

    def parse_midi_channels(self, text):
        return list(map(int, text.split()))

    def parse_memory_sequence(self, text):
        result = []

        if not text:
            return []

        sequences = list(text.split())

        for iii, seq in enumerate(sequences):
            times = self.parse_param("x", str(seq))

            if "x" in seq:
                idx = seq.index("x")
                seq = seq[0:idx]

            if seq.startswith(self.string_constants.literal_memory_sequence):
                if not len(seq) - 1:
                    pass
                elif seq[1] == "[":
                    seq = seq[seq.index("["):seq.index("]")].replace(
                        self.string_constants.literal_memory_sequence_separator, " ")

                result.append((seq, times))

            else:
                try:
                    for i in range(times):
                        result.append(int(seq))
                except Exception:
                    traceback.print_exc()
        return result

    def parse_root_sequence(self, text):
        result = []
        sequences = list(text.split())

        note_dict = constants_note_dict

        for seq in sequences:
            times = self.parse_param("x", str(seq))

            if self.is_pointer(seq):
                return self.context.root_sequences[self.get_pointer_destination(seq)]

            if "x" in seq:
                idx = seq.index("x")
                seq = seq[0:idx]

            for i in range(times):
                if seq in note_dict:
                    result.append(note_dict[seq])
                else:
                    print("Invalid root skipped: %s" % seq)
        return result

    def parse_scheduling_sequence(self, text):
        result = []
        sequences = text.split()

        for seq in sequences:
            times = self.parse_param("x", str(seq))

            if self.is_pointer(seq):
                return self.context.scheduling_sequences[self.get_pointer_destination(seq)]

            if "x" in seq:
                seq = seq[0:seq.index("x")]

            result += [seq for _ in range(times)]
        return result

    @staticmethod
    def is_pointer(seq):
        return seq.strip().startswith(StringConstants.pointer)

    @staticmethod
    def get_pointer_destination(seq):
        return int(seq[1])

    def parse_scale_sequence(self, context, text):
        result = []
        sequences = list(text.split())
        available_scales = context.scales.get_all_names()

        for seq in sequences:
            times = self.parse_param("x", str(seq))

            if self.is_pointer(seq):
                return context.scale_sequences[self.get_pointer_destination(seq)]

            if "x" in seq and times is not None:
                seq = seq[0:seq.rindex("x")]

            if seq in available_scales:
                for i in range(0, 1 if times is None else times):
                    result.append(seq)

            else:
                print("Scale %s does not exist." % seq)
                return []

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

    
    def parse_multiple_sequences_separated(self, sequences, separator=StringConstants.multiple_entry_separator):
        if separator not in sequences:
            return [sequences]

        else:
            try:
                result = sequences.split(separator)

                for i, individual in enumerate(result[:]):
                    if StringConstants.opening_bracket in individual and StringConstants.closing_bracket in individual:
                        a = " ".join(self.unpack_nested_bracketed_expression(individual))
                        result[i] = a
                    else:
                        result[i] = individual

                return result

            except Exception:
                traceback.print_exc()
                return []

    @staticmethod
    def _recurse_nested_expr_list(input_):
        output = []

        for i, item in enumerate(input_):
            if isinstance(item, str):
                output.append(item)

            elif isinstance(item, list):
                if i < len(input_) - 1 and isinstance(input_[i + 1], str) and input_[i + 1][0] == "x":
                    times = int(input_[i + 1][1:])

                    for _ in range(times):
                        output.append(item)

                    del input_[i + 1]

                else:
                    for j, _ in enumerate(item):
                        output.append(item[j])

        return output
    
    def unpack_nested_bracketed_expression(self, seq):
        seq = "%s%s%s" % (StringConstants.opening_bracket, seq, StringConstants.closing_bracket)
        result = nestedExpr(StringConstants.opening_bracket, StringConstants.closing_bracket).parseString(seq).asList()[
            0]

        while any([isinstance(item, list) for item in result]):
            result = self._recurse_nested_expr_list(result)

        return result
