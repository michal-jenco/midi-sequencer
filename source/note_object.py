import random
from time import sleep
from threading import Thread


class NoteTypes:
    NORMAL = "Normal"
    NOTE_PAUSE = "Note Pause"
    GO_TO_START = "Go To Start"


class NoteObject(object):
    def __init__(self, context, pitch=None, channel=None, velocity=None, duration=None, repetitions=0,
                 type_=NoteTypes.NORMAL):
        self.context = context
        self.duration = duration
        self.channel = channel
        self.pitch = pitch
        self.velocity = velocity
        self.repetitions = repetitions
        self.type_ = type_

        self._channel_prefix = 0x90

    def __repr__(self):
        return "Channel: %s, Pitch: %s, Velocity: %s\n" % (self.channel, self.pitch, self.velocity)

    def __str__(self):
        return self.__repr__()

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
            self.context.midi.send_message(self.get_midi_repr())

    def play_transposed(self, semitones):
        if self.type_ is NoteTypes.NORMAL:
            self.context.midi.send_message(self.get_transposed_midi_repr(semitones))

    def play_with_scheduling_object(self, obj):
        if isinstance(obj, NoteSchedulingObject):
            pass

        else:
            raise TypeError("Must supply a NoteSchedulingObject instance.")

    def end(self):
        self.context.midi.send_message(self.get_end_note_midi_repr())

    def play_and_schedule_end(self):
        self.play()
        Thread(target=self.schedule_end).start()

    def schedule_end(self):
        sleep(self.duration)
        self.end()

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
        self.note_duration = None

        if self.is_just_note_length(self.seq):
            self.type_ = NoteSchedhulingTypes.JUST_LENGTH
            self.note_duration = NoteDuration(self.seq)

        elif self.is_just_tuplet(self.seq):
            self.type_ = NoteSchedhulingTypes.JUST_TUPLET
            self.note_duration = NoteDuration(self.seq)

    @staticmethod
    def is_just_note_length(seq):
        try:
            int(seq)
            return True
        except:
            return False

    def is_just_tuplet(self, seq):
        return seq[-1] in TupletTypes.MAP.keys() and self.is_just_note_length(seq[:-1])

    def __repr__(self):
        return str(NoteDurationTypes.MAP[self.seq])

    def __str__(self):
        return self.__repr__()


class TupletTypes:
    TRIPLET = "Triplet"
    QUINTUPLET = "Quintuplet"
    SEPTUPLET = "Septuplet"
    NONUPLET = "Nonuplet"

    MAP = {"t": TRIPLET, "q": QUINTUPLET, "s": SEPTUPLET}


class NoteDurationTypes:
    WHOLE = "Whole"
    HALF = "Half"
    QUARTER = "Quarter"
    EIGTHT = "Eigtht"
    SIXTEENTH = "Sixteenth"
    THIRTYSECOND = "Thirtysecond"
    SIXTYFOURTH = "Sixtyfourth"

    WHOLE_TRIPLET = "WHOLE triplet"
    HALF_TRIPLET = "HALF triplet"
    QUARTER_TRIPLET = "QUARTER triplet"
    EIGTHT_TRIPLET = "EIGTHT triplet"
    SIXTEENTH_TRIPLET = "SIXTEENTH triplet"
    THIRTYSECOND_TRIPLET = "THIRTYSECOND triplet"
    SIXTYFOURTH_TRIPLET = "SIXTYFOURTH triplet"

    WHOLE_QUINTUPLET = "WHOLE quintuplet"
    HALF_QUINTUPLET = "HALF quintuplet"
    QUARTER_QUINTUPLET = "QUARTER quintuplet"
    EIGTHT_QUINTUPLET = "EIGTHT quintuplet"
    SIXTEENTH_QUINTUPLET = "SIXTEENTH quintuplet"
    THIRTYSECOND_QUINTUPLET = "THIRTYSECOND quintuplet"
    SIXTYFOURTH_QUINTUPLET = "SIXTYFOURTH quintuplet"

    WHOLE_SEPTUPLET = "WHOLE septuplet"
    HALF_SEPTUPLET = "HALF septuplet"
    QUARTER_SEPTUPLET = "QUARTER septuplet"
    EIGTHT_SEPTUPLET = "EIGTHT septuplet"
    SIXTEENTH_SEPTUPLET = "SIXTEENTH septuplet"
    THIRTYSECOND_SEPTUPLET = "THIRTYSECOND septuplet"
    SIXTYFOURTH_SEPTUPLET = "SIXTYFOURTH septuplet"

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
    def __init__(self, duration_sequence):
        if duration_sequence in NoteDurationTypes.MAP.keys():
            self.duration = NoteDurationTypes.MAP[duration_sequence]


class NoteLengthsOld:
    def __init__(self, bpm):
        self.whole = 60. / bpm
        self.half = self.whole / 2.
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