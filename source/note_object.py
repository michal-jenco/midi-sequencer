import random
import math
from time import sleep
from threading import Thread
from copy import copy

gap_count_dict = {"t": 2, "q": 4, "s": 6, "n": 8}


class NoteTypes:
    NORMAL = "Normal"
    NOTE_PAUSE = "Note Pause"
    GO_TO_START = "Go To Start"


class DecayFunctions:
    sine = lambda step, smooth: math.sin(float(step / smooth))


class NoteObject(object):
    def __init__(self, context, pitch=None, channel=None, velocity=None, attack=None, duration=None, play_count=1,
                 type_=NoteTypes.NORMAL):
        self.context = context
        self.duration = duration
        self.attack = attack
        self.channel = channel
        self.pitch = pitch
        self.velocity = velocity
        self.repetitions = play_count
        self.type_ = type_

        self._channel_prefix = 0x90

    def __repr__(self):
        return "[NoteObject - Channel: %s, Pitch: %s, Velocity: %s]" % (self.channel, self.pitch, self.velocity)

    def __str__(self):
        return self.__repr__()

    def supply_scheduling_object(self, obj):
        self.duration = obj.duration_object
        self.attack = obj.attack_object
        self.repetitions = obj.get_play_count()

    def get_type(self):
        return self.type_

    def set_channel(self, channel):
        self.channel = int(channel)

    def set_velocity(self, velocity):
        self.velocity = int(velocity)

    def set_duration(self, duration):
        self.duration = duration

    def get_midi_repr(self):
        return [self._channel_prefix + self.channel, self.pitch, self.velocity]

    def get_end_note_midi_repr(self):
        return self.get_midi_repr()[:2] + [0]

    def play(self):
        if self.type_ is NoteTypes.NORMAL:
            Thread(target=self._play).start()

    def _play(self):
        for i in range(self.repetitions):
            if self.attack is not None and not i:
                sleep(self.attack.get_duration_in_seconds(bpm=self.context.get_bpm()))

            self.context.midi.send_message(self.get_midi_repr())

            if self.duration is not None:
                sleep_time = self.duration.get_duration_in_seconds(bpm=self.context.get_bpm())
                sleep(sleep_time)
                self.end()

    def play_transposed(self, semitones):
        if self.type_ is NoteTypes.NORMAL:
            self.context.midi.send_message(self.get_transposed_midi_repr(semitones))

    def end(self):
        self.context.midi.send_message(self.get_end_note_midi_repr())

    def transpose(self, semitones):
        self.pitch += semitones

    def get_transposed_midi_repr(self, semitones):
        return [self._channel_prefix + self.channel, self.pitch + semitones, self.velocity]


class NoteContainer(object):
    def __init__(self, context, notes, gaps):
        self.context = context
        self.notes = notes
        self.gaps = gaps  # NoteDurationTypes
        self.type_ = NoteTypes.NORMAL
        self.channel = None
        self.pitch = 0

    def __repr__(self):
        return "NoteContainer - %s notes%s%s" % (len(self.notes),
                                                 ", %s gaps" % self.gaps[0].name,
                                                 ", %s duration" % (self.notes[0].duration.name
                                                                    if self.notes[0].duration is not None else ""))

    def __str__(self):
        return self.__repr__()

    def play(self, transposed=0):
        Thread(target=self._play, args=(transposed,)).start()

    def play_transposed(self, semitones):
        self.play(transposed=semitones)

    def _play(self, transposed_semitones):
        for i, note in enumerate(self.notes):
            if isinstance(note.pitch, int):
                orig_pitch = note.pitch
                note.pitch += int(self.pitch // 2)

            if transposed_semitones:
                note.play_transposed(transposed_semitones)
            else:
                note.play()

            if i < len(self.gaps):
                sleep(self.gaps[i].get_duration_in_seconds(self.context.get_bpm()))

            if isinstance(note.pitch, int):
                note.pitch = orig_pitch

    def set_channel(self, channel):
        self.channel = channel
        for note in self.notes:
            note.set_channel(channel)

    def set_velocity(self, velocity):
        for note in self.notes:
            note.set_velocity(velocity)

    def supply_scheduling_object(self, scheduling_object):
        for note in self.notes:
            note.supply_scheduling_object(scheduling_object)


class NoteSchedhulingTypes:
    JUST_LENGTH = "Just note length"
    JUST_TUPLET = "Just tuplet"


class NoteSchedulingObject:
    def __init__(self, seq):
        self.seq = str(seq.strip())
        self.type_ = None
        self.duration_object = None
        self.attack_object = None
        self.repeat_count = 0
        self.times = 1
        self.is_dotted = (lambda: self._is_dotted(self.seq))()
        self.number_of_dots = (lambda: self.seq.count(NoteSchedulingSequenceConstants.DOTTED))()
        self.is_times = (lambda: self.times > 1)

        if self._has_times(self.seq):
            self.times = self._get_times(self.seq)
        else:
            self.times = 1

        if self._has_attack(self.seq):
            self.attack_object = self._get_attack(self.seq)

        if self._has_repeat(self.seq):
            self.repeat_count = self._get_repeat_count(self.seq)

        if self._is_just_note_length(seq):
            self.type_ = NoteSchedhulingTypes.JUST_LENGTH
        elif self._is_just_tuplet(seq):
            self.type_ = NoteSchedhulingTypes.JUST_TUPLET

        pure_seq = self._get_pure_seq(seq)

        if pure_seq in NoteDurationTypes.MAP.keys():
            self.duration_object = copy(NoteDurationTypes.MAP[pure_seq])

            if self.is_dotted:
                self.duration_object.divider /= (3 / 2.) * self.number_of_dots
            self.duration_object.divider /= self.times
        else:
            self.duration_object = NoteDurationTypes.UNKNOWN

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

        seq = seq.replace(NoteSchedulingSequenceConstants.DOTTED, "")
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
        return NoteSchedulingSequenceConstants.DOTTED in seq

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
    def _get_times(seq):
        comma_idx = seq.index(NoteSchedulingSequenceConstants.TIMES)

        try:
            return int(seq[comma_idx + 1])
        except IndexError:
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

    def get_play_count(self):
        return self.repeat_count + 1

    @staticmethod
    def _get_repeat_count(seq):
        repeat_seq_start_index = seq.index(NoteSchedulingSequenceConstants.REPEAT)
        repeat_seq_end_index = seq.rindex(NoteSchedulingSequenceConstants.REPEAT)
        repeat_seq = seq[repeat_seq_start_index + 1:repeat_seq_end_index]
        return int(repeat_seq)

    @staticmethod
    def _remove_subsequence(seq, bounded_by):
        if bounded_by not in seq:
            return seq

        start_index = seq.index(bounded_by)
        end_index = seq.rindex(bounded_by)
        return seq[:start_index] + seq[end_index + 1:]

    def __repr__(self):
        return "%s%s%s%s" % (
            "%sx " % self.times if self.times - 1 else "",
            self.duration_object.name,
            "-%sx" % self.get_play_count() if self.get_play_count() - 1 else "",
            " %s%s" % (self.number_of_dots, "x dotted") if self.is_dotted else "")

    def __str__(self):
        return self.__repr__()


class TupletTypes:
    TRIPLET = "Triplet"
    QUINTUPLET = "Quintuplet"
    SEPTUPLET = "Septuplet"
    NONUPLET = "Nonuplet"

    MAP = {"t": TRIPLET, "q": QUINTUPLET, "s": SEPTUPLET, "n": NONUPLET}


class NoteSchedulingSequenceConstants:
    ATTACK = "a"
    REPEAT = "r"
    DOTTED = "."
    TIMES = ","

    BOUNDED = ATTACK, REPEAT


class NoteDurationTypesRecord:
    def __init__(self, name, divider=None):
        self.name = name
        self.divider = divider

    def get_duration_in_seconds(self, bpm):
        if self.divider is not None:
            return 60. / bpm / self.divider
        else:
            print("Trying to get_duration_in_seconds() but divider is None. Defaulting to Whole note duration.")
            return 60. / bpm


class NoteDurationTypes:
    WHOLE = NoteDurationTypesRecord("Whole", 1)
    HALF = NoteDurationTypesRecord("Half", 2)
    QUARTER = NoteDurationTypesRecord("Quarter", 4)
    EIGTHT = NoteDurationTypesRecord("Eigtht", 8)
    SIXTEENTH = NoteDurationTypesRecord("Sixteenth", 16)
    THIRTYSECOND = NoteDurationTypesRecord("Thirtysecond", 32)
    SIXTYFOURTH = NoteDurationTypesRecord("Sixtyfourth", 64)

    WHOLE_TRIPLET = NoteDurationTypesRecord("Whole triplet", WHOLE.divider * 3 / 2.)
    HALF_TRIPLET = NoteDurationTypesRecord("Half triplet", HALF.divider * 3 / 2.)
    QUARTER_TRIPLET = NoteDurationTypesRecord("Quarter triplet", QUARTER.divider * 3 / 2.)
    EIGTHT_TRIPLET = NoteDurationTypesRecord("Eigtht triplet", EIGTHT.divider * 3 / 2.)
    SIXTEENTH_TRIPLET = NoteDurationTypesRecord("Sixteenth triplet", SIXTEENTH.divider * 3 / 2.)
    THIRTYSECOND_TRIPLET = NoteDurationTypesRecord("Thirtysecond triplet", THIRTYSECOND.divider * 3 / 2.)
    SIXTYFOURTH_TRIPLET = NoteDurationTypesRecord("Sixtyfourth triplet", SIXTYFOURTH.divider * 3 / 2.)

    WHOLE_QUINTUPLET = NoteDurationTypesRecord("Whole quintuplet", WHOLE.divider * 5 / 2.)
    HALF_QUINTUPLET = NoteDurationTypesRecord("Half quintuplet", HALF.divider * 5 / 2.)
    QUARTER_QUINTUPLET = NoteDurationTypesRecord("Quarter quintuplet", QUARTER.divider * 5 / 2.)
    EIGTHT_QUINTUPLET = NoteDurationTypesRecord("Eigtht quintuplet", EIGTHT.divider * 5 / 2.)
    SIXTEENTH_QUINTUPLET = NoteDurationTypesRecord("Sixteenth quintuplet", SIXTEENTH.divider * 5 / 2.)
    THIRTYSECOND_QUINTUPLET = NoteDurationTypesRecord("Thirtysecond quintuplet", THIRTYSECOND.divider * 5 / 2.)
    SIXTYFOURTH_QUINTUPLET = NoteDurationTypesRecord("Sixtyfourth quintuplet", SIXTYFOURTH.divider * 5 / 2.)

    WHOLE_SEPTUPLET = NoteDurationTypesRecord("Whole septuplet", WHOLE.divider * 7 / 2.)
    HALF_SEPTUPLET = NoteDurationTypesRecord("Half septuplet", HALF.divider * 7 / 2.)
    QUARTER_SEPTUPLET = NoteDurationTypesRecord("Quarter septuplet", QUARTER.divider * 7 / 2.)
    EIGTHT_SEPTUPLET = NoteDurationTypesRecord("Eigtht septuplet", EIGTHT.divider * 7 / 2.)
    SIXTEENTH_SEPTUPLET = NoteDurationTypesRecord("Sixteenth septuplet", SIXTEENTH.divider * 7 / 2.)
    THIRTYSECOND_SEPTUPLET = NoteDurationTypesRecord("Thirtysecond septuplet", THIRTYSECOND.divider * 7 / 2.)
    SIXTYFOURTH_SEPTUPLET = NoteDurationTypesRecord("Sixtyfourth septuplet", SIXTYFOURTH.divider * 7 / 2.)

    WHOLE_NONUPLET = NoteDurationTypesRecord("Whole nonuplet", WHOLE.divider * 9 / 2.)
    HALF_NONUPLET = NoteDurationTypesRecord("Half nonuplet", HALF.divider * 9 / 2.)
    QUARTER_NONUPLET = NoteDurationTypesRecord("Quarter nonuplet", QUARTER.divider * 9 / 2.)
    EIGTHT_NONUPLET = NoteDurationTypesRecord("Eigtht nonuplet", EIGTHT.divider * 9 / 2.)
    SIXTEENTH_NONUPLET = NoteDurationTypesRecord("Sixteenth nonuplet", SIXTEENTH.divider * 9 / 2.)
    THIRTYSECOND_NONUPLET = NoteDurationTypesRecord("Thirtysecond nonuplet", THIRTYSECOND.divider * 9 / 2.)
    SIXTYFOURTH_NONUPLET = NoteDurationTypesRecord("Sixtyfourth nonuplet", SIXTYFOURTH.divider * 9 / 2.)

    UNKNOWN = NoteDurationTypesRecord(name="Unknown NoteDurationTypes object")

    MAP = {"1": WHOLE, "2": HALF, "4": QUARTER, "8": EIGTHT, "16": SIXTEENTH, "32": THIRTYSECOND, "64": SIXTYFOURTH,
           "1t": WHOLE_TRIPLET, "2t": HALF_TRIPLET, "4t": QUARTER_TRIPLET, "8t": EIGTHT_TRIPLET,
           "16t": SIXTEENTH_TRIPLET, "32t": THIRTYSECOND_TRIPLET, "64t": SIXTYFOURTH_TRIPLET,
           "1q": WHOLE_QUINTUPLET,
           "2q": HALF_QUINTUPLET,
           "4q": QUARTER_QUINTUPLET,
           "8q": EIGTHT_QUINTUPLET,
           "16q": SIXTEENTH_QUINTUPLET,
           "32q": THIRTYSECOND_QUINTUPLET,
           "64q": SIXTYFOURTH_QUINTUPLET,
           "1s": WHOLE_SEPTUPLET,
           "2s": HALF_SEPTUPLET,
           "4s": QUARTER_SEPTUPLET,
           "8s": EIGTHT_SEPTUPLET,
           "16s": SIXTEENTH_SEPTUPLET,
           "32s": THIRTYSECOND_SEPTUPLET,
           "64s": SIXTYFOURTH_SEPTUPLET,
           "1n": WHOLE_NONUPLET,
           "2n": HALF_NONUPLET,
           "4n": QUARTER_NONUPLET,
           "8n": EIGTHT_NONUPLET,
           "16n": SIXTEENTH_NONUPLET,
           "32n": THIRTYSECOND_NONUPLET,
           "64n": SIXTYFOURTH_NONUPLET}


class NoteDuration:
    def __init__(self, duration_str_sequence):
        self.duration = None

        if duration_str_sequence in NoteDurationTypes.MAP.keys():
            self.duration = copy(NoteDurationTypes.MAP[duration_str_sequence])
        else:
            self.duration = copy(NoteDurationTypes.UNKNOWN)

    def get(self):
        return self.duration


class NoteLengthsOld:
    def __init__(self, bpm):
        self.whole = 60. / bpm
        self.half = self.whole / 2.
        self.quarter = self.whole / 2.
        self.eigtht = self.whole / 8.
        self.sixteenth = self.whole / 16.
        self.thirtysecond = self.whole / 32.
        self.sixtyfourth = self.whole / 64.

        self.triplet = self.quarter / 3.
        self.quintuplet = self.quarter / 5.
        self.septuplet = self.quarter / 7.
        self.nonuplet = self.quarter / 9.

    def get_random(self):
        note_list = sorted(list(self.__dict__.keys()))
        chosen_note = random.choice(note_list)
        print("Random note: \"%s\"" % chosen_note)
        return self.__dict__[chosen_note]

    def get_all(self):
        all_notes = sorted(list(self.__dict__.keys()))
        return all_notes

    def get_by_name(self, name_):
        return self.__getattribute__(name_)


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
