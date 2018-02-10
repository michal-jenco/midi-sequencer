import random


class NoteLengths:
    def __init__(self, bpm):

        self.whole = 60/bpm
        self.half = self.whole/2
        self.quarter = self.whole/4
        self.eigtht = self.whole/8
        self.sixteenth = self.whole/16
        self.thirtysecond = self.whole/32
        self.sixtyfourth = self.whole/64

        self.triplet = self.quarter/3
        self.quintuplet = self.quarter/5
        self.septuplet = self.quarter/7
        self.nonuplet = self.quarter/9

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
