import random

from source.functions import log, get_inverse_dict
from source.constants import MiscConstants
from source.b__i__n__a__r__y import B__i__n__a__r__y


class Scales:
    def dict(self):
        a = sorted(self.get_all_names())
        b = [self.__dict__[name] for name in a]
        return {key: value for key, value in zip(a, b)}

    def dict_minimal(self, dic=None):
        result = {}
        full_dict = self.dict() if dic is None else dic

        for name, lst in full_dict.items():
            index = full_dict[name].index(12) if 12 in full_dict[name] else MiscConstants.NO_OCTAVE_SCALE_INDEX
            result[name] = full_dict[name][:index]
        return result

    def get_corresponding_mode_name(self, scale_name):
        # print("Scale name: %s" % scale_name)
        # print("Scale name after conversion: %s" % scale_name)
        scale_name = ModeNames.convert_scale_name_from_scales__dict___to_dict_scale_name(scale_name)

        if scale_name not in ModeNames:
            return None

        if self.context.scale_mode == 0:
            return scale_name.capitalize()

        dict_which_contains_mode_name = ModeNames.get_dict_which_contains_mode_name(scale_name)

        if dict_which_contains_mode_name is not None:
            inverse_dict_which_contains_mode_name = get_inverse_dict(dict_which_contains_mode_name)
            mode_name_key = inverse_dict_which_contains_mode_name[scale_name.capitalize()]
            final_key = (mode_name_key + self.context.scale_mode) % len(dict_which_contains_mode_name.keys())

            if final_key in dict_which_contains_mode_name:
                mode_name = dict_which_contains_mode_name[final_key]
            else:
                mode_name = None
        else:
            mode_name = None

        return mode_name

    def __init__(self, context):
        self.context = context
        self.major = [0, 2, 4, 5, 7, 9, 11, 12]
        self.minor = [0, 2, 3, 5, 7, 8, 10, 12]

        self.melodic_minor = [0, 2, 3, 5, 7, 9, 11, 12]
        self.harmonic_minor = [0, 2, 3, 5, 7, 8, 11, 12]

        self.pentatonic = [0, 3, 5, 7, 10, 12]
        self.octatonic = [0, 1, 3, 4, 6, 7, 9, 10, 12]
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

        self.lydian_dominant = [0, 2, 4, 6, 7, 9, 10, 12]
        self.lydian_augmented = [0, 2, 4, 6, 8, 9, 11, 12]
        self.lydian_sharp_9 = [0, 3, 4, 6, 7, 9, 11, 12]

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

        self._expand_scales()

    def _expand_scales(self):
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
        all_scales.remove("context")
        return all_scales

    def get_scale_by_name(self, name):
        if self.context is None:
            return self.__getattribute__(name)

        try:
            int(name)
        except:
            try:
                self.__getattribute__(name)
            except AttributeError:
                return B__i__n__a__r__y.get_pcs(name)

            orig_result = self.__getattribute__(name)[self.context.scale_mode:]
            result = [item - self.__getattribute__(name)[self.context.scale_mode] for item in orig_result]
            return result
        else:
            orig = B__i__n__a__r__y.expand_pcs(B__i__n__a__r__y.get_pcs(name), 2, True)
            orig_truncated = orig[self.context.scale_mode:]
            return [item - orig[self.context.scale_mode] for item in orig_truncated]

    @staticmethod
    def get_display_scale_name(scale):
        return scale.replace("_", " ").capitalize()

    @staticmethod
    def get_note_by_index_wrap(idx, scale):
        return scale[idx % len(scale)]


class MetaModeNames(type):
    @staticmethod
    def __contains__(mode_name):
        return mode_name in ModeNames.get_all_mode_names()


class ModeNames(metaclass=MetaModeNames):
    MAJOR = {0: "Major", 1: "Dorian", 2: "Phrygian", 3: "Lydian", 4: "Mixolydian", 5: "Aeolian", 6: "Locrian"}
    MINOR = {0: "Minor", 1: "Locrian", 2: "Major", 3: "Dorian", 4: "Phrygian", 5: "Lydian", 6: "Mixolydian"}
    MELODIC_MINOR = {0: "Melodic minor", 1: "Phrygian #6 (Dorian b2)", 2: "Lydian augmented",
                     3: "Lydian dominant",
                     4: "Mixolydian b6", 5: "Half-diminished", 6: "Super locrian"}
    HARMONIC_MINOR = {0: "Harmonic minor", 1: "Locrian #6", 2: "Ionian #5", 3: "Ukrainian dorian",
                      4: "Phrygian dominant", 5: "Lydian #9", 6: "Altered diminished"}
    DOUBLE_HARM_MAJOR = {0: "Double harmonic major", 1: "Lydian #6 #9", 2: "Phrygian bb7 b4",
                         3: "Hungarian minor", 4: "Locrian ♮6 ♮3 (Mixolydian b5 b2, Oriental)",
                         5: "Ionian #5 #2", 6: "Locrian bb3 bb7"}
    PENTATONIC = {0: "Pentatonic", 1: "", 2: "", 3: "", 4: "Yo"}

    _MAJOR_INVERSE = get_inverse_dict(MAJOR)
    _MINOR_INVERSE = get_inverse_dict(MINOR)
    _MELODIC_MINOR_INVERSE = get_inverse_dict(MELODIC_MINOR)
    _HARMONIC_MINOR_INVERSE = get_inverse_dict(HARMONIC_MINOR)
    _DOUBLE_HARMONIC_MAJOR_INVERSE = get_inverse_dict(DOUBLE_HARM_MAJOR)
    _PENTATONIC_INVERSE = get_inverse_dict(PENTATONIC)

    MAP = {"major": MAJOR, "ionian": MAJOR, "minor": MINOR, "aeolian": MINOR, "melodic_minor": MELODIC_MINOR,
           "harmonic_minor": HARMONIC_MINOR, "double_harm_major": DOUBLE_HARM_MAJOR, "pentatonic": PENTATONIC}

    @staticmethod
    def convert_scale_name_from_scales__dict___to_dict_scale_name(scale_name):
        if "_harm_" in scale_name:
            scale_name = scale_name.replace("_harm_", "_harmonic_")
        if "sharp_" in scale_name:
            scale_name = scale_name.replace("sharp_", "#")

        return scale_name.replace("_", " ").lower()

    @staticmethod
    def get_all_mode_names():
        return set(item.lower() for sublist in
                   [list(value.values()) for value in ModeNames.MAP.values()]
                   for item in sublist)

    @staticmethod
    def get_all_dicts():
        return [ModeNames.MAJOR, ModeNames.MINOR, ModeNames.MELODIC_MINOR, ModeNames.HARMONIC_MINOR,
                ModeNames.DOUBLE_HARM_MAJOR, ModeNames.PENTATONIC]

    @staticmethod
    def get_all_inverse_dicts():
        return [getattr(ModeNames, item) for item in ModeNames.__dict__ if "_INVERSE" in item]

    @staticmethod
    def get_dict_which_contains_mode_name(mode_name):
        if mode_name not in ModeNames:
            return None

        all_dicts = ModeNames.get_all_dicts()
        for dic in all_dicts:
            if mode_name in {value.lower() for value in dic.values()}:
                return dic

        return None


def check_duplicates():
    scale_names = Scales(None).get_all_names()
    scale_names.remove("fifths")
    scale_lists = {name: Scales(None).get_scale_by_name(name)[:Scales(None).get_scale_by_name(name).index(12)]
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
        print("There are no duplicates __:)__.\n")
        return 0


if __name__ == '__main__':
    check_duplicates()

    print("All mode names: %s\n" % ModeNames.get_all_mode_names())
    print("All inverse dicts: %s\n" % ModeNames.get_all_inverse_dicts())

# self.byzantine = self.double_harm_major
# self.arabic = self.double_harm_major
# self.gypsy_major = self.double_harm_major
# self.gypsy_minor = self.hungarian_minor
# self.gypsy = self.hungarian_minor
# self.geez = self.dorian
# self.romanian_minor = self.ukrainian_dorian