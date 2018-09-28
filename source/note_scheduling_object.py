from copy import copy

from source.note_duration_types import NoteDurationTypes
from source.note_object import TupletTypes
from source.note_object_decay import DecayFunction


class NoteSchedulingObject:
    def __init__(self, seq):
        self.seq = str(seq.strip())
        self.type_ = None
        self.duration_object = None
        self.attack_object = None
        self.repeat_count = 0
        self.times = 1
        self.decay_function = None
        self.number_of_dots = (lambda: self._get_number_of_dots(self.seq))()
        self.is_dotted = (lambda: self._get_number_of_dots(self.seq) > 0)()
        self.is_times = (lambda: self.times > 1)

        if self._has_times(self.seq):
            self.times = self._get_times(self.seq)
        else:
            self.times = 1

        if self._has_attack(self.seq):
            self.attack_object = self._get_attack(self.seq)

        if self._has_repeat(self.seq):
            self.repeat_count = self._get_repeat_count(self.seq)

        if self._has_decay_function(self.seq):
            self.decay_function = DecayFunction(self._get_decay_function(self.seq))

        if self._is_just_note_length(seq):
            self.type_ = NoteSchedulingTypes.JUST_LENGTH
        elif self._is_just_tuplet(seq):
            self.type_ = NoteSchedulingTypes.JUST_TUPLET

        pure_seq = self._get_pure_seq(seq)

        if pure_seq in NoteDurationTypes.MAP.keys():
            self.duration_object = copy(NoteDurationTypes.MAP[pure_seq])

            if self.is_dotted:
                self.duration_object.divider /= (3 / 2.) * self.number_of_dots
            self.duration_object.divider /= self.times
        else:
            self.duration_object = NoteDurationTypes.UNKNOWN

    def __repr__(self):
        return "%s%s%s%s%s" % (
            "%sx " % self.times if self.times - 1 else "",
            self.duration_object.name,
            "-%sx" % self.get_play_count() if self.get_play_count() - 1 else "",
            " %s%s" % (self.number_of_dots, "x dotted") if self.is_dotted else "",
            (" (%s: %s, params: %s)" % (self.decay_function.__class__.__name__,
                                        self.decay_function.name, self.decay_function.parameters))
            if self.decay_function is not None else "")

    def _debug_print(self):
        print("duration obj: %s" % (None if self.duration_object is None else self.duration_object.name))
        print("divider: %s" % (None if self.duration_object is None else self.duration_object.divider))
        print("attack obj: %s" % (None if self.attack_object is None else self.attack_object.name))
        print("repeat count: %s" % self.repeat_count)
        print("dotted: %s times" % self.number_of_dots)
        print("times: %s" % self.times)

    def _get_pure_seq(self, seq):
        for bound in NoteSchedulingSequenceConstants.BOUNDED:
            seq = self._remove_subsequence(seq, bounded_by=bound)

        seq = seq.replace(NoteSchedulingSequenceConstants.DOT, "")
        seq = self._remove_times_subseq(seq)
        return seq

    def _is_just_note_length(self, seq):
        try:
            int(self._get_pure_seq(seq))
            return True
        except:
            return False

    def _is_just_tuplet(self, seq):
        return seq[-1] in TupletTypes.MAP.keys() and self._is_just_note_length(seq[:-1])

    @staticmethod
    def _is_dotted(seq):
        return NoteSchedulingSequenceConstants.DOT in seq

    @staticmethod
    def _has_attack(seq):
        return NoteSchedulingSequenceConstants.ATTACK in seq

    @staticmethod
    def _has_repeat(seq):
        return NoteSchedulingSequenceConstants.REPEAT in seq

    @staticmethod
    def _has_times(seq):
        return NoteSchedulingSequenceConstants.TIMES in seq

    @staticmethod
    def _has_decay_function(seq):
        return NoteSchedulingSequenceConstants.DECAY_FUNCTION in seq

    @staticmethod
    def _get_times(seq):
        comma_idx = seq.index(NoteSchedulingSequenceConstants.TIMES)

        try:
            return int(seq[comma_idx + 1])
        except (IndexError, ValueError):
            return 1

    def _remove_times_subseq(self, seq):
        if not self._has_times(seq):
            return seq

        comma_idx = seq.index(NoteSchedulingSequenceConstants.TIMES)
        return seq[:comma_idx] + seq[comma_idx + 2:]

    def _get_attack(self, seq):
        attack_seq_start_index = seq.index(NoteSchedulingSequenceConstants.ATTACK)
        attack_seq_end_index = seq.rindex(NoteSchedulingSequenceConstants.ATTACK)
        attack_seq = seq[attack_seq_start_index + 1:attack_seq_end_index]

        times = self._get_times(attack_seq) if self._has_times(attack_seq) else 1
        pure_attack_seq = self._get_pure_seq(attack_seq)

        if pure_attack_seq in NoteDurationTypes.MAP.keys():
            duration_obj = copy(NoteDurationTypes.MAP[pure_attack_seq])
            duration_obj.divider /= times
            return duration_obj
        else:
            return None

    @staticmethod
    def _get_number_of_dots(seq):
        indices = []

        for item in NoteSchedulingSequenceConstants.BOUNDED:
            if item in seq:
                indices.append(seq.index(item))

        return seq[:min(indices) if indices else len(seq)].count(NoteSchedulingSequenceConstants.DOT)

    def get_play_count(self):
        return self.repeat_count + 1

    @staticmethod
    def _get_repeat_count(seq):
        repeat_seq_start_index = seq.index(NoteSchedulingSequenceConstants.REPEAT)
        repeat_seq_end_index = seq.rindex(NoteSchedulingSequenceConstants.REPEAT)
        repeat_seq = seq[repeat_seq_start_index + 1:repeat_seq_end_index]
        return int(repeat_seq)

    @staticmethod
    def _get_decay_function(seq):
        start_index = seq.index(NoteSchedulingSequenceConstants.DECAY_FUNCTION)
        end_index = seq.rindex(NoteSchedulingSequenceConstants.DECAY_FUNCTION)
        decay_function_seq = seq[start_index + 1:end_index]
        return decay_function_seq

    @staticmethod
    def _remove_subsequence(seq, bounded_by):
        if bounded_by not in seq:
            return seq

        start_index = seq.index(bounded_by)
        end_index = seq.rindex(bounded_by)
        return seq[:start_index] + seq[end_index + 1:]


class NoteSchedulingTypes:
    JUST_LENGTH = "Just note length"
    JUST_TUPLET = "Just tuplet"


class NoteSchedulingSequenceConstants:
    ATTACK = "a"
    REPEAT = "r"
    DOT = "."
    TIMES = ","
    DECAY_FUNCTION = "f"

    BOUNDED = ATTACK, REPEAT, DECAY_FUNCTION