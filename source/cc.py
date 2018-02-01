class CCKeys:
    def __init__(self):
        self.portamento = 5
        self.expression = 11
        self.voice = 40
        self.octave = 41
        self.detune = 42
        self.vco_eg_int = 43
        self.cutoff = 44
        self.vcf_eg_int = 45
        self.lfo_rate = 46
        self.lfo_pitch_int = 47
        self.lfo_cutoff_int = 48
        self.eg_attack = 49
        self.eg_decay_release = 50
        self.eg_sustain = 51
        self.delay_time = 52
        self.delay_feedback = 53

    def get_all(self):
        return sorted(list(self.__dict__.keys()))

    def get_cc_by_name(self, name_):
        return self.__getattribute__(name_)
