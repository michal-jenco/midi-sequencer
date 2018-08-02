class PitchBendNamesMetaclass(type):
    @staticmethod
    def __getitem__(key):
        return PitchBendNames.MAP[key] if key in PitchBendNames.MAP.keys() else "Unknown tone division"


class PitchBendNames(metaclass=PitchBendNamesMetaclass):
    MAP = {1: "Whole tone", 2: "Semitone", 3: "Third tone", 4: "Quarter tone",
           5: "Fifth tone", 6: "Sixth tone", 7: "Seventh tone", 8: "Eigtht tone"}


class PitchBendRanges(object):
    minimum, maximum = 0, 16383
    zero = maximum // 2
    monologue_semitone = maximum // 4


class PitchBend(object):
    def __init__(self, control_seq, channel, midi):
        self.type = None
        self.times = None
        self.midi = midi
        self.channel = channel
        self.direction = -1 if control_seq[0] == "-" else 1

        control_seq = control_seq.replace("+", "").replace("-", "")

        if len(control_seq) == 1:
            self.times, self.type = 1, int(control_seq)
        elif len(control_seq) == 2:
            self.times, self.type = [int(a) for a in control_seq]

        self.name = "%s %s %s. Channel: %s." % (
            "Plus" if self.direction == 1 else "Minus",
            self.times,
            PitchBendNames[self.type] + ("s" if self.times > 1 else ""),
            self.channel)

        if self.type == 0:
            self.integer_bend = PitchBendRanges.zero
        else:
            self.integer_bend = (PitchBendRanges.zero
                                 + self.direction * int((self.times / (self.type / 2.)) * PitchBendRanges.monologue_semitone))

    def __call__(self):
        # print("Sending PitchBend: %s" % self.name)
        msb = (self.integer_bend >> 7) & 0xff
        lsb = self.integer_bend & 0xff

        # print("Integer bend: %s" % self.integer_bend)
        # print("Reconsutzcted: %s" % ((msb * 2 ** 7) | lsb))

        msg = [0b11100000 + self.channel, lsb, msb]
        self.midi.send_message(msg)

        return self.name