class AkaiApcButtons(object):
    class Colors(object):
        class Grid(object):
            off = 0x0
            green = 0x1
            green_blink = 0x2
            red = 0x3
            red_blink = 0x4
            yellow = 0x5
            yellow_blink = 0x6

        class RowCol(object):
            off = 0x0
            on = 0x1
            blink = 0x2

    class Controller(object):
        def __init__(self, midi):
            self.midi = midi

        def set_color(self, button_number, color):
            self.midi.send_message([0x90, button_number, color])

        def set_all_grid_to_color(self, color):
            for i in range(64):
                self.midi.send_message([0x90, i, color])

        def turn_off_grid(self):
            self.set_all_grid_to_color(AkaiApcButtons.Colors.Grid.off)

