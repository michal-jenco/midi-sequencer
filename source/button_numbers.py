class ButtonNumbers(object):
    """"""

    class Novation(object):
        """"""

        PITCH = 0
        MODULATION = 1

        MIDI_CHANNEL_UP = 102
        MIDI_CHANNEL_DOWN = 103

        SLIDER_1 = 41
        SLIDER_2 = 42
        SLIDER_3 = 43
        SLIDER_4 = 44
        SLIDER_5 = 45
        SLIDER_6 = 46
        SLIDER_7 = 47
        SLIDER_8 = 48
        SLIDER_9 = 7

        BUTTON_1 = 51
        BUTTON_2 = 52
        BUTTON_3 = 53
        BUTTON_4 = 54
        BUTTON_5 = 55
        BUTTON_6 = 56
        BUTTON_7 = 57
        BUTTON_8 = 58
        BUTTON_9 = 59

        IN_CONTROL_RIGHT = NotImplemented
        LEFT = NotImplemented
        RIGHT = NotImplemented

        KNOB_1 = 21
        KNOB_2 = 22
        KNOB_3 = 23
        KNOB_4 = 24
        KNOB_5 = 25
        KNOB_6 = 26
        KNOB_7 = 27
        KNOB_8 = 28

        PAD_11 = NotImplemented
        PAD_12 = NotImplemented
        PAD_13 = NotImplemented
        PAD_14 = NotImplemented
        PAD_15 = NotImplemented
        PAD_16 = NotImplemented
        PAD_17 = NotImplemented
        PAD_18 = NotImplemented
        PAD_21 = NotImplemented
        PAD_22 = NotImplemented
        PAD_23 = NotImplemented
        PAD_24 = NotImplemented
        PAD_25 = NotImplemented
        PAD_26 = NotImplemented
        PAD_27 = NotImplemented
        PAD_28 = NotImplemented

        PAD_RIGHT_1 = 104
        PAD_RIGHT_2 = 105

        SCENE_UP = 112
        SCENE_DOWN = 113

        STOP = 114
        PLAY = 115
        REPEAT = 116
        RECORD = 117

        _CODE_PAD_PRESS = 153
        _CODE_PAD_RELEASE = 137

        _CODES_PAD = _CODE_PAD_PRESS, _CODE_PAD_RELEASE
        _CODES_BASIC = 176, 224

        @staticmethod
        def msg_is_button(msg, button):
            if msg[0] in ButtonNumbers.Novation._CODES_BASIC:
                return msg[1] == button
