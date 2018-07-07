import random
from time import sleep
from threading import Thread


class NoteTypes:
    NORMAL = "Normal"
    NOTE_PAUSE = "Note Pause"
    GO_TO_START = "Go To Start"


class NoteObject(object):
    def __init__(self, context, pitch=None, channel=None, velocity=None, duration=None, type_=NoteTypes.NORMAL):
        self.context = context
        self.duration = duration
        self.channel = channel
        self.pitch = pitch
        self.velocity = velocity
        self.type_ = type_

    def __repr__(self):
        return "Channel: %s, Pitch: %s, Velocity: %s\n" % (self.channel, self.pitch, self.velocity)

    def __str__(self):
        return self.__repr__()

    def get_note_type(self):
        return self.type_

    def set_channel(self, channel):
        self.channel = int(channel)

    def set_velocity(self, velocity):
        self.velocity = int(velocity)

    def set_duration(self, duration):
        self.duration = duration

    def get_midi_repr(self):
        return [0x90 + self.channel, self.pitch, self.velocity]

    def get_end_note_midi_repr(self):
        return self.get_midi_repr()[:2] + [0]

    def play(self):
        if self.type_ is NoteTypes.NORMAL:
            self.context.midi.send_message(self.get_midi_repr())

    def play_transposed(self, semitones):
        if self.type_ is NoteTypes.NORMAL:
            self.context.midi.send_message(self.get_transposed_midi_repr(semitones))

    def end(self):
        self.context.midi.send_message(self.get_end_note_midi_repr())

    def play_and_schedule_end(self):
        self.play()
        Thread(target=self.schedule_end).start()

    def schedule_end(self):
        sleep(self.duration)
        self.context.midi.send_message(self.get_end_note_midi_repr())

    def transpose(self, semitones):
        if self.pitch is not None:
            self.pitch += semitones

    def get_transposed_midi_repr(self, semitones):
        return [0x90 + self.channel, self.pitch + semitones, self.velocity]


class NoteLengths:
    def __init__(self, bpm):
        self.whole = 60 / bpm
        self.half = self.whole / 2
        self.quarter = self.whole / 4
        self.eigtht = self.whole / 8
        self.sixteenth = self.whole / 16
        self.thirtysecond = self.whole / 32
        self.sixtyfourth = self.whole / 64

        self.triplet = self.quarter / 3
        self.quintuplet = self.quarter / 5
        self.septuplet = self.quarter / 7
        self.nonuplet = self.quarter / 9

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