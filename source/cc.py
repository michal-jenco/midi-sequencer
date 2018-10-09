class CC(object):
    def __init__(self):
        pass

    def get_all(self):
        return sorted(list(self.__dict__.keys()))

    def get(self, name_):
        return self.__getattribute__(name_)


class CCKeys(CC):
    def __init__(self):
        super(CC, self).__init__()

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


class CCFM(CC):
    def __init__(self):
        super(CC, self).__init__()

        self.transpose = 40
        self.velocity = 41
        self.mod_attack = 42
        self.mod_decay = 43
        self.carrier_attack = 44
        self.carrier_decay = 45
        self.lfo_rate = 46
        self.lfo_pitch_depth = 47
        self.algorithm = 48
        self.arp_type = 49
        self.arp_division = 50


class CCSample(CC):
    def __init__(self):
        super(CC, self).__init__()

        self.level = 7
        self.pan = 10
        self.start_point = 40
        self.sample_length = 41
        self.high_cut = 42
        self.speed = 43
        self.pitch_int = 44
        self.pitch_attack = 45
        self.pitch_decay = 46
        self.amp_attack = 47
        self.amp_delay = 48


class CCKick(CC):
    def __init__(self):
        super(CC, self).__init__()

        self.pulse_color = 40
        self.pulse_level = 41
        self.amp_attack = 42
        self.amp_decay = 43
        self.drive = 44
        self.tone = 45
        self.resonator_pitch = 46
        self.resonator_bend = 47
        self.resonator_time = 48
        self.accent = 49


class CCMonologue(CC):
    def __init__(self):
        super(CC, self).__init__()

        self.eg_attack, self.eg_decay, self.eg_int = 16, 17, 25
        self.eg_type, self.eg_target = 61, 62
        self.lfo_rate, self.lfo_depth = 24, 26
        self.lfo_target, self.lfo_wave, self.lfo_mode = 56, 58, 59
        self.drive = 28
        self.pitch = 35
        self.shape_1, self.shape_2 = 36, 37
        self.level_1, self.level_2 = 39, 40
        self.cutoff, self.resonance = 43, 44
        self.octave_2 = 49
        self.wave_1, self.wave_2 = 50, 51
        self.sync_ring = 60
