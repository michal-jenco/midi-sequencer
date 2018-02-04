import random


class NoteLengths:
    def __init__(self, bpm):

        self.whole = bpm/60
        self.half = bpm/60/2
        self.quarter = bpm/60/4
        self.eigtht = bpm/60/8
        self.sixteenth = bpm/60/16
        self.thirtysecond = bpm/60/32
        self.sixtyfourth = bpm/60/64

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
