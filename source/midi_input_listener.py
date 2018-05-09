import time
import threading
import rtmidi
from rtmidi.midiutil import open_midiinput

from source.akai_midimix_message import AkaiMidimixMessage
from source.functions import range_to_range
from source.constants import Ranges


class MIDIInputListener(object):
    def __init__(self, sequencer, context, input_name, interval):
        self.sequencer = sequencer
        self.context = context
        self.input_name = input_name
        self.interval = interval

        self.midi = rtmidi.MidiIn()
        self.akai_message = AkaiMidimixMessage()

        self.fader_synced = [False]*8
        self.know_row_1_synced = [False]*8
        self.know_row_2_synced = [False]*8
        self.know_row_3_synced = [False]*8

        self.available_ports = self.midi.get_ports()

        for i, dev in enumerate(self.available_ports):
            if self.input_name in dev:
                self.port = i
                print("Found %s on port %s" % (self.input_name, i))
                break

        print("I am going to open %s on port %s." % (input_name, self.port))

        try:
            self.midi, self.port = open_midiinput(self.port)
        except (EOFError, KeyboardInterrupt):
            print("Akai MIDI Mix is not connected.")
            return

        self.callback_dict = self.get_callback_dict()

        self.main_loop_thread = threading.Thread(target=self.main_loop, args=())
        self.main_loop_thread.setDaemon(True)
        self.main_loop_thread.start()

    def get_callback_dict(self):
        result = {"RecArm 1 Pressed": self.playback_on_callback,
                  "RecArm 2 Pressed": self.sequencer.end_all_notes,
                  "RecArm 3 Pressed": self.sequencer.reset_idx,
                  "RecArm 4 Pressed": self.sequencer.init_entries,
                  "RecArm 5 Pressed": self.sequencer.press_all_enters,
                  "RecArm 6 Pressed": self.sequencer.mute_all,
                  "RecArm 7 Pressed": self.sequencer.unmute_all,
                  "RecArm 8 Pressed": self.sequencer.invert_mute,
                  "Solo Pressed": self.solo_callback,
                  "Knob Row 1 Col 8": self.bpm_callback}
        return result

    def bpm_callback(self, value):
        bpm_range_value = range_to_range(Ranges.MIDI_RANGE, Ranges.BPM_RANGE, value)
        self.context.bpm.set(bpm_range_value)
        print("Set BPM to %s" % bpm_range_value)

    def playback_on_callback(self):
        self.context.playback_on = not self.context.playback_on

    def solo_callback(self):
        self.sequencer.intvar_solo.set(not self.sequencer.intvar_solo.get())

    def main_loop(self):
        while True:
            msg = self.midi.get_message()

            if msg:
                msg, _ = msg
                type_, controller, value = msg
                str_controller = self.akai_message.get_name_by_msg(msg)

                print("MIDI Input Listener: %s - %s" % (str_controller, value))
                self._callback(msg)

            time.sleep(self.interval)

    def _callback(self, msg):
        msg_name = self.akai_message.get_name_by_msg(msg)
        value = self.akai_message.get_value(msg)

        if msg_name in self.callback_dict:
            self.callback_dict[msg_name]()

        elif msg_name == "Knob Row 1 Col 8":
            bpm_range_value = range_to_range(Ranges.MIDI_RANGE, Ranges.BPM_RANGE, value)
            self.context.bpm.set(bpm_range_value)
            print("Set BPM to %s" % bpm_range_value)

        elif "Knob Row" in msg_name:
            knob_row = int(msg_name.split()[2])
            i = int(msg_name.split()[-1]) - 1

            if i == 7:
                return

            if knob_row == 1:
                sync = self.know_row_1_synced
                strvars = self.sequencer.strvars_prob_skip_note
            elif knob_row == 2:
                sync = self.know_row_2_synced
                strvars = self.sequencer.strvars_prob_poly_abs
            else:
                sync = self.know_row_3_synced
                strvars = self.sequencer.strvars_prob_poly_rel

            if not sync[i]:
                if abs(int(strvars[i].get()) - value) < 5:
                    sync[i] = True
            else:
                strvars[i].set(value)

        elif "Mute" in msg_name and "Pressed" in msg_name:
            i = int(msg_name.split()[1]) - 1

            if self.sequencer.intvar_solo.get():
                for j, item in enumerate(self.sequencer.intvars_enable_channels):
                    if i != j:
                        print("Setting %s to False" % j)
                        self.sequencer.intvars_enable_channels[j].set(False)
                    else:
                        print("Setting %s to True" % j)
                        self.sequencer.intvars_enable_channels[j].set(True)

            else:
                self.sequencer.intvars_enable_channels[i].set(not self.sequencer.intvars_enable_channels[i].get())

        elif "Fader" in msg_name:
            try:
                i = int(msg_name.split()[-1]) - 1

                if i % 2 == 0:
                    velocities = self.sequencer.velocities_strvars_min
                else:
                    velocities = self.sequencer.velocities_strvars_max

                if not self.fader_synced[i]:
                    if abs(int(velocities[i // 2].get()) - value) < 5:
                        self.fader_synced[i] = True
                else:
                    velocities[i // 2].set(value)

            except:
                pass
