class AkaiMidimixMessage(object):
    def __init__(self):
        self.code_dict = dict()

        for i in 128, 144, 176:
            self.code_dict[i] = dict()
        
        self.code_dict[176][16] = "Knob Row 1 Col 1"
        self.code_dict[176][20] = "Knob Row 1 Col 2"
        self.code_dict[176][24] = "Knob Row 1 Col 3"
        self.code_dict[176][28] = "Knob Row 1 Col 4"
        self.code_dict[176][46] = "Knob Row 1 Col 5"
        self.code_dict[176][50] = "Knob Row 1 Col 6"
        self.code_dict[176][54] = "Knob Row 1 Col 7"
        self.code_dict[176][58] = "Knob Row 1 Col 8"

        self.code_dict[176][16 + 1] = "Knob Row 2 Col 1"
        self.code_dict[176][20 + 1] = "Knob Row 2 Col 2"
        self.code_dict[176][24 + 1] = "Knob Row 2 Col 3"
        self.code_dict[176][28 + 1] = "Knob Row 2 Col 4"
        self.code_dict[176][46 + 1] = "Knob Row 2 Col 5"
        self.code_dict[176][50 + 1] = "Knob Row 2 Col 6"
        self.code_dict[176][54 + 1] = "Knob Row 2 Col 7"
        self.code_dict[176][58 + 1] = "Knob Row 2 Col 8"

        self.code_dict[176][16 + 2] = "Knob Row 3 Col 1"
        self.code_dict[176][20 + 2] = "Knob Row 3 Col 2"
        self.code_dict[176][24 + 2] = "Knob Row 3 Col 3"
        self.code_dict[176][28 + 2] = "Knob Row 3 Col 4"
        self.code_dict[176][46 + 2] = "Knob Row 3 Col 5"
        self.code_dict[176][50 + 2] = "Knob Row 3 Col 6"
        self.code_dict[176][54 + 2] = "Knob Row 3 Col 7"
        self.code_dict[176][58 + 2] = "Knob Row 3 Col 8"

        self.code_dict[176][19] = "Fader 1"
        self.code_dict[176][23] = "Fader 2"
        self.code_dict[176][27] = "Fader 3"
        self.code_dict[176][31] = "Fader 4"
        self.code_dict[176][49] = "Fader 5"
        self.code_dict[176][53] = "Fader 6"
        self.code_dict[176][57] = "Fader 7"
        self.code_dict[176][61] = "Fader 8"
        self.code_dict[176][62] = "Fader Main"

        self.code_dict[144][1] = "Mute 1 Pressed"
        self.code_dict[128][1] = "Mute 1 Released"
        self.code_dict[144][4] = "Mute 2 Pressed"
        self.code_dict[128][4] = "Mute 2 Released"
        self.code_dict[144][7] = "Mute 3 Pressed"
        self.code_dict[128][7] = "Mute 3 Released"
        self.code_dict[144][10] = "Mute 4 Pressed"
        self.code_dict[128][10] = "Mute 4 Released"
        self.code_dict[144][13] = "Mute 5 Pressed"
        self.code_dict[128][13] = "Mute 5 Released"
        self.code_dict[144][16] = "Mute 6 Pressed"
        self.code_dict[128][16] = "Mute 6 Released"
        self.code_dict[144][19] = "Mute 7 Pressed"
        self.code_dict[128][19] = "Mute 7 Released"
        self.code_dict[144][22] = "Mute 8 Pressed"
        self.code_dict[128][22] = "Mute 8 Released"

        self.code_dict[144][3] = "RecArm 1 Pressed"
        self.code_dict[128][3] = "RecArm 1 Released"
        self.code_dict[144][6] = "RecArm 2 Pressed"
        self.code_dict[128][6] = "RecArm 2 Released"
        self.code_dict[144][9] = "RecArm 3 Pressed"
        self.code_dict[128][9] = "RecArm 3 Released"
        self.code_dict[144][12] = "RecArm 4 Pressed"
        self.code_dict[128][12] = "RecArm 4 Released"
        self.code_dict[144][15] = "RecArm 5 Pressed"
        self.code_dict[128][15] = "RecArm 5 Released"
        self.code_dict[144][18] = "RecArm 6 Pressed"
        self.code_dict[128][18] = "RecArm 6 Released"
        self.code_dict[144][21] = "RecArm 7 Pressed"
        self.code_dict[128][21] = "RecArm 7 Released"
        self.code_dict[144][24] = "RecArm 8 Pressed"
        self.code_dict[128][24] = "RecArm 8 Released"

        self.code_dict[144][27] = "Solo Pressed"
        self.code_dict[128][27] = "Solo Released"

        self.code_dict[144][25] = "Bank Left Pressed"
        self.code_dict[128][25] = "Bank Left Released"
        self.code_dict[144][26] = "Bank Right Pressed"
        self.code_dict[128][26] = "Bank Right Released"

    def get_name_by_index(self, type_, i):
        try:
            return self.code_dict[type_][i]
        except:
            return "No such code in AKAI MIDI_MIX messages :("
