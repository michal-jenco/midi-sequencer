import time
import threading
import rtmidi
from rtmidi.midiutil import open_midiinput

from source.akai_midimix_message import AkaiMidimixMessage
from source.akai_midimix_state import AkaiMidimixStates, AkaiMidimixState
from source.functions import range_to_range
from source.constants import Ranges, MiscConstants


class MIDIInputListener(object):
    def __init__(self, sequencer, context, input_name, interval):
        self.sequencer = sequencer
        self.context = context
        self.input_name = input_name
        self.interval = interval
        self.channel_count = 8

        self.midi = rtmidi.MidiIn()
        self.akai_message = AkaiMidimixMessage()
        self.state = AkaiMidimixState(sequencer=sequencer)

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

        self.callback_dict = {"RecArm 1 Pressed": self.recarm_1_callback,
                              "RecArm 2 Pressed": self.recarm_2_callback,
                              "RecArm 3 Pressed": self.recarm_3_callback,
                              "RecArm 4 Pressed": self.recarm_4_callback,
                              "RecArm 5 Pressed": self.recarm_5_callback,
                              "RecArm 6 Pressed": self.recarm_6_callback,
                              "RecArm 7 Pressed": self.recarm_7_callback,
                              "RecArm 8 Pressed": self.recarm_8_callback,
                              "Solo Pressed": self.solo_callback}

        self.main_loop_thread = threading.Thread(target=self.main_loop, args=())
        self.main_loop_thread.setDaemon(True)
        self.main_loop_thread.start()

    def get_callback_dict(self):
        return self.callback_dict

    def recarm_1_callback(self):
        self.playback_on_callback()

    def recarm_2_callback(self):
        self.sequencer.end_all_notes()

    def recarm_3_callback(self):
        self.sequencer.reset_idx()

    def recarm_4_callback(self):
        self.context.scale_mode_changing_on = not self.context.scale_mode_changing_on
        self.sequencer.frame_status.update_scale_mode()

    def recarm_5_callback(self):
        self.sequencer.press_all_enters()

    def recarm_6_callback(self):
        self.mute_callback("mute")

    def recarm_7_callback(self):
        self.mute_callback("unmute")

    def recarm_8_callback(self):
        self.mute_callback("invert")

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
            if self.context.scale_mode_changing_on:
                self.context.change_mode(offset=-1)
            else:
                self.state.previous()

        elif direction.lower() == "right":
            if self.context.scale_mode_changing_on:
                self.context.change_mode(offset=1)
            else:
                self.state.next()

    def bpm_callback(self, value):
        bpm_range_value = range_to_range(Ranges.MIDI_CC, Ranges.BPM, value)
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

                threading.Thread(target=lambda: print("MIDI Input Listener: %s: %s" % (str_controller, value))).start()

                self._callback(msg)

            time.sleep(self.interval)

    def _callback(self, msg):
        msg_name = self.akai_message.get_name_by_msg(msg)
        value = self.akai_message.get_value(msg)

        if msg_name in self.callback_dict:
            self.callback_dict[msg_name]()

        elif msg_name == "Knob Row 1 Col 8":
            bpm_range_value = range_to_range(Ranges.MIDI_CC, Ranges.BPM, value)
            self.context.bpm.set(bpm_range_value)
            threading.Thread(target=lambda: print("Set BPM to %s" % bpm_range_value)).start()

        elif "Knob Row" in msg_name:
            knob_row = int(msg_name.split()[2])
            i = int(msg_name.split()[-1]) - 1

            if i == 7:
                return

            self.dict_sync_strvars = {1: (self.know_row_1_synced, self.sequencer.strvars_prob_skip_note),
                                      2: (self.know_row_2_synced, self.sequencer.strvars_prob_poly_abs),
                                      3: (self.know_row_3_synced, self.sequencer.strvars_prob_poly_rel)}

            sync, strvars = self.dict_sync_strvars[knob_row]
            value = int(range_to_range(Ranges.MIDI_CC, Ranges.PERCENT, value))

            if not sync[i]:
                if abs(int(strvars[i].get()) - value) < MiscConstants.KNOB_SYNC_DISTANCE:
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
                    intvars[j].set(i == j)
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
                    if abs(int(velocities[i // 2].get()) - value) < MiscConstants.KNOB_SYNC_DISTANCE:
                        self.fader_synced[i] = True
                        velocities[i // 2].set(value)
                else:
                    velocities[i // 2].set(value)

            except:
                pass

        elif "Bank" in msg_name and "Pressed" in msg_name:
            self.bank_callback(direction=msg_name.split()[1])
