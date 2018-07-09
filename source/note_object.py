import random
from time import sleep
from threading import Thread


class NoteTypes:
    NORMAL = "Normal"
    NOTE_PAUSE = "Note Pause"
    GO_TO_START = "Go To Start"


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
        return "Channel: %s, Pitch: %s, Velocity: %s\n" % (self.channel, self.pitch, self.velocity)

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
                sleep(self.duration.get_duration_in_seconds(bpm=self.context.get_bpm()))
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

        if self._has_attack(self.seq):
            self.attack_object = self._get_attack(self.seq)
            seq = self._remove_subsequence(seq, NoteSchedulingSequenceConstants.ATTACK)

        if self._has_repeat(self.seq):
            self.repeat_count = self._get_repeat_count(self.seq)
            seq = self._remove_subsequence(seq, NoteSchedulingSequenceConstants.REPEAT)

        if self._is_just_note_length(seq):
            self.type_ = NoteSchedhulingTypes.JUST_LENGTH
        elif self._is_just_tuplet(seq):
            self.type_ = NoteSchedhulingTypes.JUST_TUPLET

        if seq in NoteDurationTypes.MAP.keys():
            self.duration_object = NoteDurationTypes.MAP[seq]
        else:
            self.duration_object = NoteDurationTypes.UNKNOWN

    @staticmethod
    def _is_just_note_length(seq):
        try:
            int(seq)
            return True
        except:
            return False

    def _is_just_tuplet(self, seq):
        return seq[-1] in TupletTypes.MAP.keys() and self._is_just_note_length(seq[:-1])

    @staticmethod
    def _has_attack(seq):
        return NoteSchedulingSequenceConstants.ATTACK in seq

    @staticmethod
    def _has_repeat(seq):
        return NoteSchedulingSequenceConstants.REPEAT in seq

    @staticmethod
    def _get_attack(seq):
        attack_seq_start_index = seq.index(NoteSchedulingSequenceConstants.ATTACK)
        attack_seq_end_index = seq.rindex(NoteSchedulingSequenceConstants.ATTACK)
        attack_seq = seq[attack_seq_start_index + 1:attack_seq_end_index]
        return NoteDurationTypes.MAP[attack_seq]

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
        start_index = seq.index(bounded_by)
        end_index = seq.rindex(bounded_by)
        return seq[:start_index] + seq[end_index + 1:]

    def __repr__(self):
        return "%s - %sx" % (self.duration_object.name, self.get_play_count())

    def __str__(self):
        return self.__repr__()


class TupletTypes:
    TRIPLET = "Triplet"
    QUINTUPLET = "Quintuplet"
    SEPTUPLET = "Septuplet"
    NONUPLET = "Nonuplet"

    MAP = {"t": TRIPLET, "q": QUINTUPLET, "s": SEPTUPLET}


class NoteSchedulingSequenceConstants:
    ATTACK = "a"
    REPEAT = "r"


class NoteDurationTypesRecord:
    def __init__(self, name, multiplier=None):
        self.name = name
        self.multiplier = multiplier

    def get_duration_in_seconds(self, bpm):
        if self.multiplier is not None:
            return 60. / bpm / self.multiplier
        else:
            print("Trying to get_duration_in_seconds() but multiplier is None. Defaulting to Whole note duration.")
            return 60. / bpm


class NoteDurationTypes:
    WHOLE = NoteDurationTypesRecord(name="Whole", multiplier=1)
    HALF = NoteDurationTypesRecord(name="Half", multiplier=2)
    QUARTER = NoteDurationTypesRecord(name="Quarter", multiplier=4)
    EIGTHT = NoteDurationTypesRecord(name="Eigtht", multiplier=8)
    SIXTEENTH = NoteDurationTypesRecord(name="Sixteenth", multiplier=16)
    THIRTYSECOND = NoteDurationTypesRecord(name="Thirtysecond", multiplier=32)
    SIXTYFOURTH = NoteDurationTypesRecord(name="Sixtyfourth", multiplier=64)

    WHOLE_TRIPLET = NoteDurationTypesRecord(name="Whole triplet", multiplier=WHOLE.multiplier * 3 / 4.)
    HALF_TRIPLET = NoteDurationTypesRecord(name="Half triplet", multiplier=HALF.multiplier * 3 / 4.)
    QUARTER_TRIPLET = NoteDurationTypesRecord(name="Quarter triplet", multiplier=QUARTER.multiplier * 3 / 4.)
    EIGTHT_TRIPLET = NoteDurationTypesRecord(name="Eigtht triplet", multiplier=EIGTHT.multiplier * 3 / 4.)
    SIXTEENTH_TRIPLET = NoteDurationTypesRecord(name="Sixteenth triplet", multiplier=SIXTEENTH.multiplier * 3 / 4.)
    THIRTYSECOND_TRIPLET = NoteDurationTypesRecord(name="Thirtysecond triplet", multiplier=THIRTYSECOND.multiplier * 3 / 4.)
    SIXTYFOURTH_TRIPLET = NoteDurationTypesRecord(name="Sixtyfourth triplet", multiplier=SIXTYFOURTH.multiplier * 3 / 4.)

    WHOLE_QUINTUPLET = NoteDurationTypesRecord(name="Whole quintuplet", multiplier=WHOLE.multiplier * 5 / 4.)
    HALF_QUINTUPLET = NoteDurationTypesRecord(name="Half quintuplet", multiplier=HALF.multiplier * 5 / 4.)
    QUARTER_QUINTUPLET = NoteDurationTypesRecord(name="Quarter quintuplet", multiplier=QUARTER.multiplier * 5 / 4.)
    EIGTHT_QUINTUPLET = NoteDurationTypesRecord(name="Eigtht quintuplet", multiplier=EIGTHT.multiplier * 5 / 4.)
    SIXTEENTH_QUINTUPLET = NoteDurationTypesRecord(name="Sixteenth quintuplet", multiplier=SIXTEENTH.multiplier * 5 / 4.)
    THIRTYSECOND_QUINTUPLET = NoteDurationTypesRecord(name="Thirtysecond quintuplet", multiplier=THIRTYSECOND.multiplier * 5 / 4.)
    SIXTYFOURTH_QUINTUPLET = NoteDurationTypesRecord(name="Sixtyfourth quintuplet", multiplier=SIXTYFOURTH.multiplier * 5 / 4.)

    WHOLE_SEPTUPLET = NoteDurationTypesRecord(name="Whole septuplet", multiplier=WHOLE.multiplier * 7 / 4.)
    HALF_SEPTUPLET = NoteDurationTypesRecord(name="Half septuplet", multiplier=HALF.multiplier * 7 / 4.)
    QUARTER_SEPTUPLET = NoteDurationTypesRecord(name="Quarter septuplet", multiplier=QUARTER.multiplier * 7 / 4.)
    EIGTHT_SEPTUPLET = NoteDurationTypesRecord(name="Eigtht septuplet", multiplier=EIGTHT.multiplier * 7 / 4.)
    SIXTEENTH_SEPTUPLET = NoteDurationTypesRecord(name="Sixteenth septuplet", multiplier=SIXTEENTH.multiplier * 7 / 4.)
    THIRTYSECOND_SEPTUPLET = NoteDurationTypesRecord(name="Thirtysecond septuplet", multiplier=THIRTYSECOND.multiplier * 7 / 4.)
    SIXTYFOURTH_SEPTUPLET = NoteDurationTypesRecord(name="Sixtyfourth septuplet", multiplier=SIXTYFOURTH.multiplier * 7 / 4.)

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
           "64s": SIXTYFOURTH_SEPTUPLET}


class NoteDuration:
    def __init__(self, duration_str_sequence):
        self.duration = None

        if duration_str_sequence in NoteDurationTypes.MAP.keys():
            self.duration = NoteDurationTypes.MAP[duration_str_sequence]

        else:
            self.duration = NoteDurationTypes.UNKNOWN

    def get(self):
        return self.duration


class NoteLengthsOld:
    def __init__(self, bpm):
        self.whole = 60. / bpm
        self.half = self.whole / 4.
        self.quarter = self.whole / 4.
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
    return [NoteObject(context=context,
                       channel=ch,
                       pitch=pitch if isinstance(pitch, int) else None,
                       velocity=vel,
                       type_=NoteTypes.NORMAL if isinstance(pitch, int) else pitch)
            for ch, pitch, vel in midi_notes]