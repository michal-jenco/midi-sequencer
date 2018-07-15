import random

from source.functions import log


class Scales:
    def __init__(self, context):
        self._context = context
        self.major = [0, 2, 4, 5, 7, 9, 11, 12]
        self.minor = [0, 2, 3, 5, 7, 8, 10, 12]

        self.melodic_minor = [0, 2, 3, 5, 7, 9, 11, 12]
        self.harmonic_minor = [0, 2, 3, 5, 7, 8, 11, 12]

        self.octatonic = [0, 1, 3, 4, 6, 7, 9, 10, 12]

        self.pentatonic = [0, 3, 5, 7, 10, 12]
        self.wholetone = [0, 2, 4, 6, 8, 10, 12]

        self.thirds = [0, 3, 6, 9, 12]
        self.fourths = [0, 4, 8, 12]
        self.fifths = [0, 5, 10, 15, 20, 25, 30]

        self.ionian = [0, 2, 4, 5, 7, 9, 11, 12]
        self.dorian = [0, 2, 3, 5, 7, 9, 10, 12]
        self.phrygian = [0, 1, 3, 5, 7, 8, 10, 12]
        self.lydian = [0, 2, 4, 6, 7, 9, 11, 12]
        self.mixolydian = [0, 2, 4, 5, 7, 9, 10, 12]
        self.aeolian = [0, 2, 3, 5, 7, 8, 10, 12]
        self.locrian = [0, 1, 3, 5, 6, 8, 10, 12]

        self.lydian_sharp_9 = [0, 3, 4, 6, 7, 9, 11, 12]
        self.lydian_augmented = [0, 2, 4, 6, 8, 9, 11, 12]

        self.acoustic = [0, 2, 4, 6, 7, 9, 10, 12]
        self.ukrainian_dorian = [0, 2, 3, 6, 7, 9, 10, 12]
        self.phrygian_dominant = [0, 1, 4, 5, 7, 8, 10, 12]
        self.double_harm_major = [0, 1, 4, 5, 7, 8, 11, 12]
        self.hungarian_minor = [0, 2, 3, 6, 7, 8, 11, 12]
        self.neapolitan_minor = [0, 1, 3, 5, 7, 8, 11, 12]
        self.neapolitan_major = [0, 1, 3, 5, 7, 9, 11, 12]
        self.enigmatic = [0, 1, 4, 6, 8, 10, 11, 12]
        self.hirajoshi = [0, 2, 3, 7, 8, 12]
        self.yo = [0, 2, 5, 7, 9, 12]
        self.persian = [0, 1, 4, 5, 6, 8, 11, 12]
        self.mixolydian_b6 = [0, 2, 4, 5, 7, 8, 10, 12]

        self.augmented = [0, 3, 4, 7, 8, 11, 12]
        self.balinese = [0, 1, 3, 7, 8, 12]
        self.chinese = [0, 4, 6, 7, 11, 12]
        self.egyptian = [0, 2, 5, 6, 9, 12]
        self.spanish = [0, 1, 3, 4, 5, 6, 8, 10, 12]
        self.in_sen = [0, 1, 5, 7, 10, 12]
        self.oriental = [0, 1, 4, 5, 6, 9, 10, 12]
        self.super_locrian = [0, 1, 3, 4, 6, 8, 10, 12]

        # self.byzantine = self.double_harm_major
        # self.arabic = self.double_harm_major
        # self.gypsy_major = self.double_harm_major
        # self.gypsy_minor = self.hungarian_minor
        # self.geez = self.dorian
        # self.gypsy = self.hungarian_minor
        # self.romanian_minor = self.ukrainian_dorian

        for scale_name in self.get_all_names():
            scale = self.get_scale_by_name(scale_name)
            orig_len = len(scale)
            for octave in range(2):
                for tone in range(orig_len):
                    scale.append(scale[tone + 1] + (octave + 1) * 12)

            self.__setattr__(scale_name, scale)

    def get_random(self):
        scale_list = sorted(list(self.__dict__.keys()))
        chosen_scale = random.choice(scale_list)
        log(msg="Random scale: \"%s\"" % chosen_scale)
        return self.__dict__[chosen_scale]

    def get_all_names(self):
        all_scales = sorted(list(self.__dict__.keys()))
        all_scales.remove("_context")
        return all_scales

    def get_scale_by_name(self, name):
        orig_result = self.__getattribute__(name)[self._context.scale_mode:]
        result = [item - self.__getattribute__(name)[self._context.scale_mode] for item in orig_result]
        return result

    @staticmethod
    def get_display_scale_name(scale):
        return scale.replace("_", " ").capitalize()

    def get_note_by_index_wrap(self, idx, scale):
        return scale[idx % len(scale)]


class ModeNames:
    MAJOR = {0: "Major", 1: "Dorian", 2: "Phrygian", 3: "Lydian", 4: "Mixolydian", 5: "Aeolian", 6: "Locrian"}
    MINOR = {0: "Minor", 1: "Locrian", 2: "Major", 3: "Dorian", 4: "Phrygian", 5: "Lydian", 6: "Mixolydian"}
    MELODIC_MINOR = {0: "Melodic minor", 1: "Phrygian #6 (Dorian b2)", 2: "Lydian augmented", 3: "Lydian dominant",
                     4: "Mixolydian b6", 5: "Half-diminished", 6: "Altered dominant"}
    HARMONIC_MINOR = {0: "Harmonic minor", 1: "Locrian #6", 2: "Ionian #5", 3: "Ukrainian dorian",
                      4: "Phrygian dominant", 5: "Lydian #9", 6: "Altered diminished"}
    DOUBLE_HARM_MAJOR = {0: "Double harmonic major", 1: "Lydian #6 #9", 2: "Phrygian bb7 b4",
                         3: "Hungarian minor", 4: "Locrian ♮6 ♮3 (Mixolydian b5 b2)",
                         5: "Ionian #5 #2", 6: "Locrian bb3 bb7"}

    MAP = {"major": MAJOR, "ionian": MAJOR, "minor": MINOR, "aeolian": MINOR, "melodic_minor": MELODIC_MINOR,
           "harmonic_minor": HARMONIC_MINOR, "double_harm_major": DOUBLE_HARM_MAJOR}


def check_duplicates():
    scale_names = Scales().get_all_names()
    scale_names.remove("fifths")
    scale_lists = {name: Scales().get_scale_by_name(name)[:Scales().get_scale_by_name(name).index(12)]
                   for name in scale_names}

    ok_duplicates = [("aeolian", "minor"), ("minor", "aeolian"),
                     ("ionian", "major"), ("major", "ionian")]
    duplicates = []

    for outer_name, outer_list in scale_lists.items():
        for inner_name, inner_list in scale_lists.items():
            if outer_list == inner_list and inner_name != outer_name:
                if (outer_name, inner_name) not in ok_duplicates:
                    duplicates.append((outer_name, inner_name))

    if duplicates:
        for one, two in duplicates:
            if (one, two) not in ok_duplicates:
                print("%s is the same as %s" % (one, two))
        return 1
    else:
        print("There are no duplicates __:)__.")
        return 0


if __name__ == '__main__':
    check_duplicates()
