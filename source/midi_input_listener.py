import time
import threading
import rtmidi
from rtmidi.midiutil import open_midiinput

from source.akai_midimix_message import AkaiMidimixMessage
from source.akai_midimix_state import AkaiMidimixStates, AkaiMidimixState
from source.functions import range_to_range
from source.constants import Ranges, Misc


class MIDIInputListener(object):
    def __init__(self, sequencer, context, input_name, interval):
        self.sequencer = sequencer
        self.context = context
        self.input_name = input_name
        self.interval = interval
        self.channel_count = 8

        self.midi = rtmidi.MidiIn()
        self.akai_message = AkaiMidimixMessage()
        self.state = AkaiMidimixState()

        self.fader_synced = [False] * self.channel_count
        self.know_row_1_synced = [False] * self.channel_count
        self.know_row_2_synced = [False] * self.channel_count
        self.know_row_3_synced = [False] * self.channel_count

        self.available_ports = self.midi.get_ports()

        for i, dev in enumerate(self.available_ports):
            if self.input_name in dev:
                self.port = i
                print("Found %s on port %s" % (self.input_name, i))
                break

        try:
            print("I am going to open %s on port %s." % (input_name, self.port))
            self.midi, self.port = open_midiinput(self.port)
        except:
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
                  "RecArm 6 Pressed": lambda: self.mute_callback(mode="mute"),
                  "RecArm 7 Pressed": lambda: self.mute_callback(mode="unmute"),
                  "RecArm 8 Pressed": lambda: self.mute_callback(mode="invert"),
                  "Solo Pressed": self.solo_callback}
        return result

    def get_state_and_device(self):
        state = self.state.get()

        if state is AkaiMidimixStates.MAIN:
            device = self.sequencer
        elif state is AkaiMidimixStates.SAMPLE_FRAME:
            device = self.sequencer.sample_frame

        return state, device

    def mute_callback(self, mode):
        _, device = self.get_state_and_device()

        if mode == "mute":
            device.mute_all()

        elif mode == "unmute":
            device.unmute_all()

        elif mode == "invert":
            device.invert_mute()

    def bank_callback(self, direction):
        if direction.lower() == "left":
            self.state.previous()

        elif direction.lower() == "right":
            self.state.next()

    def bpm_callback(self, value):
        bpm_range_value = range_to_range(Ranges.MIDI_RANGE, Ranges.BPM_RANGE, value)
        self.context.bpm.set(bpm_range_value)
        print("Set BPM to %s" % bpm_range_value)

    def playback_on_callback(self):
        self.context.playback_on = not self.context.playback_on

    def solo_callback(self):
        _, device = self.get_state_and_device()
        device.intvar_solo.set(not device.intvar_solo.get())

    def main_loop(self):
        while True:
            msg = self.midi.get_message()

            if msg:
                # throw away some weird number
                msg, _ = msg
                type_, controller, value = msg
                str_controller = self.akai_message.get_name_by_msg(msg)

                print("MIDI Input Listener: %s: %s" % (str_controller, value))
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

            value = int(range_to_range(Ranges.MIDI_RANGE, Ranges.PERC_RANGE, value))

            if not sync[i]:
                if abs(int(strvars[i].get()) - value) < Misc.KNOB_SYNC_DISTANCE:
                    sync[i] = True

            strvars[i].set(value)

        elif "Mute" in msg_name and "Pressed" in msg_name:
            state, device = self.get_state_and_device()

            if state is AkaiMidimixStates.MAIN:
                intvars = device.intvars_enable_channels
            elif state is AkaiMidimixStates.SAMPLE_FRAME:
                intvars = device.intvars_mutes

            i = int(msg_name.split()[1]) - 1

            if device.intvar_solo.get():
                for j, item in enumerate(intvars):
                    if i != j:
                        intvars[j].set(False)
                    else:
                        intvars[j].set(True)
            else:
                intvars[i].set(not intvars[i].get())

        elif "Fader" in msg_name:
            try:
                i = int(msg_name.split()[-1]) - 1

                if i % 2 == 0:
                    velocities = self.sequencer.velocities_strvars_min
                else:
                    velocities = self.sequencer.velocities_strvars_max

                if not self.fader_synced[i]:
                    if abs(int(velocities[i // 2].get()) - value) < Misc.KNOB_SYNC_DISTANCE:
                        self.fader_synced[i] = True
                        velocities[i // 2].set(value)
                else:
                    velocities[i // 2].set(value)

            except:
                pass

        elif "Bank" in msg_name and "Pressed" in msg_name:
            self.bank_callback(direction=msg_name.split()[1])
