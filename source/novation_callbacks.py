class NovationCallbacks(object):
    def __init__(self, sequencer, context):
        self.sequencer = sequencer
        self.context = context

    def slider_1(self, value):
        self.context.novation_velocity_min = value

    def slider_2(self, value):
        self.context.novation_velocity_max = value

    def slider_3(self, value):
        pass

    def slider_4(self, value):
        pass

    def slider_5(self, value):
        pass

    def slider_6(self, value):
        pass

    def slider_7(self, value):
        pass

    def slider_8(self, value):
        pass

    def slider_9(self, value):
        pass

    def knob_1(self, value):
        pass

    def knob_2(self, value):
        pass

    def knob_3(self, value):
        pass

    def knob_4(self, value):
        pass

    def knob_5(self, value):
        pass

    def knob_6(self, value):
        pass

    def knob_7(self, value):
        pass

    def knob_8(self, value):
        pass
