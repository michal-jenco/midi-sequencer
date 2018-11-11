from threading import Thread
from time import sleep

from source.note_types import NoteTypes


class NoteContainer(object):
    def __init__(self, context, notes, gaps):
        self.context = context
        self.notes = notes
        self.gaps = gaps  # NoteDurationTypes
        self.type_ = NoteTypes.NORMAL
        self.channel = None
        self.pitch = 0
        self.octave = 0

    def __repr__(self):
        return "NoteContainer - %s notes (pitches: %s)%s%s"\
               % (len(self.notes),
                  [note.pitch for note in self.notes],
                  ", %s gaps" % self.gaps[0].name,
                  ", %s duration" % (self.notes[0].duration.name
                                     if self.notes[0].duration is not None else ""))

    def __str__(self):
        return self.__repr__()

    def play(self, transposed=0):
        Thread(target=self._play, args=(transposed,)).start()

    def end(self):
        for note in self.notes:
            note.end()

    def play_transposed(self, semitones):
        self.play(transposed=semitones)

    def set_transpose(self, transpose):
        for i, note in enumerate(self.notes):
            note.set_transpose(transpose[i])

    def _play(self, transposed_semitones):
        for i, note in enumerate(self.notes):
            if isinstance(note.pitch, int):
                note.pitch += self.pitch // 2

            if transposed_semitones:
                note.play_transposed(transposed_semitones)
            else:
                note.play()

            if i < len(self.gaps):
                sleep(self.gaps[i].get_seconds(self.context.get_bpm()))

            if isinstance(note.pitch, int):
                note.pitch -= self.pitch // 2

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