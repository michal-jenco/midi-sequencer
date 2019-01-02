from time import sleep
from threading import Thread
from copy import copy

from source.constants import MIDIChannels
from source.cc import CCFM
from source.note_duration_types import NoteDurationTypes
from source.note_types import NoteTypes


class NoteObject(object):
    def __init__(self, context, pitch=None, channel=None, velocity=None, attack=None, duration=None, transpose=0,
                 play_count=1, decay_function=None, type_=NoteTypes.NORMAL):
        self.context = context
        self.duration = duration
        self.attack = attack
        self.channel = channel
        self.pitch = pitch
        self.velocity = velocity
        self.transpose = transpose
        self.repetitions = play_count
        self.decay_function = decay_function
        self.type_ = type_
        self.last_played_midi_repr = None

        self._channel_prefix = 0x90

    def __repr__(self):
        return "[NoteObject - Channel: %s, Pitch: %s, Velocity: %s]" % (self.channel, self.pitch, self.velocity)

    def __str__(self):
        return self.__repr__()

    def supply_scheduling_object(self, obj):
        self.duration = obj.duration_object
        self.attack = obj.attack_object
        self.repetitions = obj.get_play_count()
        self.decay_function = obj.decay_function

    def get_type(self):
        return self.type_

    def set_channel(self, channel):
        self.channel = int(channel)

    def set_velocity(self, velocity):
        self.velocity = int(velocity)

    def set_duration(self, duration):
        self.duration = duration

    def set_transpose(self, transpose):
        self.transpose = transpose

    def get_midi_repr(self):
        if self.pitch is None:
            return None
        return [self._channel_prefix + self.channel, self.pitch + self.transpose, self.velocity]

    def get_end_note_midi_repr(self):
        if self.get_midi_repr() is None:
            return None
        return self.get_velocity_0_note(self.get_midi_repr())

    def play(self):
        if self.type_ is NoteTypes.NORMAL:
            Thread(target=self._play).start()

    def _play(self):
        original_velocity = self.velocity

        for i in range(self.repetitions):
            if self.decay_function is not None:
                self.velocity = original_velocity * self.decay_function(
                    i, *self.decay_function.parameters if self.decay_function.parameters else ())

            if self.attack is not None and not i:
                sleep(self.attack.get_seconds(bpm=self.context.get_bpm()))

            if self.channel == MIDIChannels.volca_fm and self.context.volca_fm_send_velocity:
                self.context.midi.send_message([0xb0 + self.channel, CCFM().velocity, self.velocity])

            note_midi_repr = self.get_midi_repr()
            self.last_played_midi_repr = note_midi_repr
            self.context.midi.send_message(self.get_velocity_0_note(note_midi_repr))
            self.context.midi.send_message(note_midi_repr)

            if self.duration is not None:
                sleep_time = self.duration.get_seconds(bpm=self.context.get_bpm())
                sleep(sleep_time)
                self.end()

        self.velocity = original_velocity

    def _play_transposed(self, semitones):
        if self.type_ is NoteTypes.NORMAL:
            note_midi_repr = self.get_transposed_midi_repr(semitones)
            self.context.midi.send_message(self.get_velocity_0_note(note_midi_repr))
            self.context.midi.send_message(note_midi_repr)
            self.last_played_midi_repr = note_midi_repr

        if self.duration is not None:
            sleep(self.duration.get_seconds(bpm=self.context.get_bpm()))
            self.context.midi.send_message(self.get_velocity_0_note(self.get_transposed_midi_repr(semitones)))

    def play_transposed(self, semitones):
        if self.type_ is NoteTypes.NORMAL:
            Thread(target=self._play_transposed, args=(semitones,)).start()

    def end(self):
        end_midi_repr = self.get_end_note_midi_repr()

        if end_midi_repr is None:
            return

        if self.last_played_midi_repr is not None:
            self.context.midi.send_message(self.get_velocity_0_note(self.last_played_midi_repr))
        else:
            self.context.midi.send_message(end_midi_repr)

    def transpose(self, semitones):
        self.pitch += semitones

    def get_transposed_midi_repr(self, semitones):
        return [self._channel_prefix + self.channel, self.pitch + semitones, self.velocity]

    @staticmethod
    def get_velocity_0_note(note):
        return note[:2] + [0]


class TupletTypes:
    TRIPLET = "Triplet"
    QUINTUPLET = "Quintuplet"
    SEPTUPLET = "Septuplet"
    NONUPLET = "Nonuplet"

    MAP = {"t": TRIPLET, "q": QUINTUPLET, "s": SEPTUPLET, "n": NONUPLET}


class NoteDuration:
    def __init__(self, duration_str_sequence):
        self.duration = None

        if duration_str_sequence in NoteDurationTypes.MAP.keys():
            self.duration = copy(NoteDurationTypes.MAP[duration_str_sequence])
        else:
            self.duration = copy(NoteDurationTypes.UNKNOWN)

    def get(self):
        return self.duration
