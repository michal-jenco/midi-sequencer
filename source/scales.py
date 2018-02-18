import random


class Scales:
    def __init__(self):
        self.major = [0, 2, 4, 5, 7, 9, 11, 12]
        self.minor = [0, 2, 3, 5, 7, 9, 10, 12]

        self.melodic_minor = [0, 2, 3, 5, 7, 9, 11, 12]
        self.harmonic_minor = [0, 2, 3, 5, 7, 8, 11, 12]

        self.gypsy = [0, 2, 3, 6, 7, 8, 11, 12]
        self.octatonic = [0, 1, 3, 4, 6, 7, 9, 10, 12]

        self.chromatic = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]

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

        self.x2_harmonic_major = [0, 1, 4, 5, 7, 8, 11, 12]

        self.hungarian_minor = [0, 2, 3, 6, 7, 8, 11, 12]

        self.neapolitan_minor = [0, 1, 3, 5, 7, 8, 11, 12]
        self.neapolitan_major = [0, 1, 3, 5, 7, 9, 11, 12]

        self.enigmatic = [0, 1, 4, 6, 8, 10, 11, 12]

        self.hirajoshi = [0, 2, 3, 7, 8, 12]
        self.yo = [0, 2, 5, 7, 9, 12]

        self.persian = [0, 1, 4, 5, 6, 8, 11, 12]

        # self.byzantine = self.x2_harmonic_major
        # self.arabic = self.x2_harmonic_major
        # self.gypsy_major = self.x2_harmonic_major
        # self.gypsy_minor = self.hungarian_minor

        for scale in self.get_all():
            scale = self.get_scale_by_name(scale)
            for octave in range(0, 2):
                for tone in range(1, len(scale)):
                    scale.append(scale[tone] + (octave+1)*12)

    def get_random(self):
        scale_list = sorted(list(self.__dict__.keys()))
        chosen_scale = random.choice(scale_list)

        print("Random scale: \"%s\"" % chosen_scale)

        return self.__dict__[chosen_scale]

    def get_all(self):
        all_scales = sorted(list(self.__dict__.keys()))

        return all_scales

    def get_scale_by_name(self, name_):
        return self.__getattribute__(name_)

    def get_display_scale_name(self, scale):
        return scale.replace("_", " ").capitalize()

    @staticmethod
    def get_note_by_index_wrap(idx, scale):
        scale_length = len(scale)
        octave = idx > scale_length
        return scale[idx % scale_length] #+ (12 if octave else 0)
