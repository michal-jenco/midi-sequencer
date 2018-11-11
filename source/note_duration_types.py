class NoteDurationTypesRecord:
    def __init__(self, name, divider=None):
        self.name = name
        self.divider = divider

    def get_seconds(self, bpm):
        if self.divider is not None:
            return 60. / bpm / self.divider
        else:
            print("Trying to get_duration_in_seconds() but divider is None. Defaulting to Whole note duration.")
            return 60. / bpm


class NoteDurationTypes:
    WHOLE = NoteDurationTypesRecord("Whole", 1)
    HALF = NoteDurationTypesRecord("Half", 2)
    QUARTER = NoteDurationTypesRecord("Quarter", 4)
    EIGTHT = NoteDurationTypesRecord("Eigtht", 8)
    SIXTEENTH = NoteDurationTypesRecord("Sixteenth", 16)
    THIRTYSECOND = NoteDurationTypesRecord("Thirtysecond", 32)
    SIXTYFOURTH = NoteDurationTypesRecord("Sixtyfourth", 64)

    WHOLE_TRIPLET = NoteDurationTypesRecord("Whole triplet", WHOLE.divider * 3 / 2.)
    HALF_TRIPLET = NoteDurationTypesRecord("Half triplet", HALF.divider * 3 / 2.)
    QUARTER_TRIPLET = NoteDurationTypesRecord("Quarter triplet", QUARTER.divider * 3 / 2.)
    EIGTHT_TRIPLET = NoteDurationTypesRecord("Eigtht triplet", EIGTHT.divider * 3 / 2.)
    SIXTEENTH_TRIPLET = NoteDurationTypesRecord("Sixteenth triplet", SIXTEENTH.divider * 3 / 2.)
    THIRTYSECOND_TRIPLET = NoteDurationTypesRecord("Thirtysecond triplet", THIRTYSECOND.divider * 3 / 2.)
    SIXTYFOURTH_TRIPLET = NoteDurationTypesRecord("Sixtyfourth triplet", SIXTYFOURTH.divider * 3 / 2.)

    WHOLE_QUINTUPLET = NoteDurationTypesRecord("Whole quintuplet", WHOLE.divider * 5 / 2.)
    HALF_QUINTUPLET = NoteDurationTypesRecord("Half quintuplet", HALF.divider * 5 / 2.)
    QUARTER_QUINTUPLET = NoteDurationTypesRecord("Quarter quintuplet", QUARTER.divider * 5 / 2.)
    EIGTHT_QUINTUPLET = NoteDurationTypesRecord("Eigtht quintuplet", EIGTHT.divider * 5 / 2.)
    SIXTEENTH_QUINTUPLET = NoteDurationTypesRecord("Sixteenth quintuplet", SIXTEENTH.divider * 5 / 2.)
    THIRTYSECOND_QUINTUPLET = NoteDurationTypesRecord("Thirtysecond quintuplet", THIRTYSECOND.divider * 5 / 2.)
    SIXTYFOURTH_QUINTUPLET = NoteDurationTypesRecord("Sixtyfourth quintuplet", SIXTYFOURTH.divider * 5 / 2.)

    WHOLE_SEPTUPLET = NoteDurationTypesRecord("Whole septuplet", WHOLE.divider * 7 / 2.)
    HALF_SEPTUPLET = NoteDurationTypesRecord("Half septuplet", HALF.divider * 7 / 2.)
    QUARTER_SEPTUPLET = NoteDurationTypesRecord("Quarter septuplet", QUARTER.divider * 7 / 2.)
    EIGTHT_SEPTUPLET = NoteDurationTypesRecord("Eigtht septuplet", EIGTHT.divider * 7 / 2.)
    SIXTEENTH_SEPTUPLET = NoteDurationTypesRecord("Sixteenth septuplet", SIXTEENTH.divider * 7 / 2.)
    THIRTYSECOND_SEPTUPLET = NoteDurationTypesRecord("Thirtysecond septuplet", THIRTYSECOND.divider * 7 / 2.)
    SIXTYFOURTH_SEPTUPLET = NoteDurationTypesRecord("Sixtyfourth septuplet", SIXTYFOURTH.divider * 7 / 2.)

    WHOLE_NONUPLET = NoteDurationTypesRecord("Whole nonuplet", WHOLE.divider * 9 / 2.)
    HALF_NONUPLET = NoteDurationTypesRecord("Half nonuplet", HALF.divider * 9 / 2.)
    QUARTER_NONUPLET = NoteDurationTypesRecord("Quarter nonuplet", QUARTER.divider * 9 / 2.)
    EIGTHT_NONUPLET = NoteDurationTypesRecord("Eigtht nonuplet", EIGTHT.divider * 9 / 2.)
    SIXTEENTH_NONUPLET = NoteDurationTypesRecord("Sixteenth nonuplet", SIXTEENTH.divider * 9 / 2.)
    THIRTYSECOND_NONUPLET = NoteDurationTypesRecord("Thirtysecond nonuplet", THIRTYSECOND.divider * 9 / 2.)
    SIXTYFOURTH_NONUPLET = NoteDurationTypesRecord("Sixtyfourth nonuplet", SIXTYFOURTH.divider * 9 / 2.)

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
           "64s": SIXTYFOURTH_SEPTUPLET,
           "1n": WHOLE_NONUPLET,
           "2n": HALF_NONUPLET,
           "4n": QUARTER_NONUPLET,
           "8n": EIGTHT_NONUPLET,
           "16n": SIXTEENTH_NONUPLET,
           "32n": THIRTYSECOND_NONUPLET,
           "64n": SIXTYFOURTH_NONUPLET}
