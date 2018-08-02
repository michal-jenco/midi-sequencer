import time
import threading
import rtmidi
from rtmidi.midiutil import open_midiinput, open_midioutput

from source.akai_messages import AkaiMidimixMessage, AkaiApcMessage
from source.akai_midimix_state import AkaiMidimixStates, AkaiMidimixState
from source.functions import range_to_range
from source.constants import Ranges, MiscConstants, StringConstants


class MIDIInputListener(object):
    def __init__(self, sequencer, context, input_names, interval):
        self.sequencer = sequencer
        self.context = context
        self.input_names = input_names
        self.interval = interval
        self.channel_count = 8

        self.device_input_port_map, self.device_output_port_map = {}, {}
        self.open_device_map_midi_in, self.open_device_map_port_in = {}, {}
        self.open_device_map_midi_out, self.open_device_map_port_out = {}, {}

        self.midi_in = rtmidi.MidiIn()
        self.midi_out = rtmidi.MidiOut()
        self.akai_midimix_message = AkaiMidimixMessage()
        self.akai_apc_message = AkaiApcMessage()
        self.akai_midimix_state = AkaiMidimixState(sequencer=sequencer)

        self.midimix_fader_synced = [False] * self.channel_count
        self.midimix_know_row_1_synced = [False] * self.channel_count
        self.midimix_know_row_2_synced = [False] * self.channel_count
        self.midimix_know_row_3_synced = [False] * self.channel_count

        self.available_input_ports = self.midi_in.get_ports()
        self.available_output_ports = self.midi_out.get_ports()
        print("Available INPUT ports: %s" % self.available_input_ports)
        print("Available OUTPUT ports: %s" % self.available_output_ports)

        for i, dev in enumerate(self.available_input_ports):
            for name in self.input_names:
                if name in dev:
                    self.device_input_port_map[name] = i
                    print("Found (INPUT) %s on port %s" % (name, self.device_input_port_map[name]))

        for i, dev in enumerate(self.available_output_ports):
            for name in self.input_names:
                if name in dev:
                    self.device_output_port_map[name] = i
                    print("Found (OUTPUT) %s on port %s" % (name, self.device_output_port_map[name]))

        for name in self.input_names:
            try:
                print("I am going to open %s (INPUT) on port %s." % (name, self.device_input_port_map[name]))
                self.open_device_map_midi_in[name], self.open_device_map_port_in[name] = open_midiinput(self.device_input_port_map[name])
            except:
                print("%s is not connected for INPUT." % name)
            else:
                print("Successfully connected to %s (INPUT) on port %s" % (name, self.device_input_port_map[name]))

        for name in self.input_names:
            try:
                print("I am going to open %s (OUTPUT) on port %s." % (name, self.device_output_port_map[name]))
                self.open_device_map_midi_out[name], self.open_device_map_port_out[name] = open_midioutput(self.device_output_port_map[name])
            except:
                print("%s is not connected for OUTPUT." % name)
            else:
                print("Successfully connected to %s (OUTPUT) on port %s" % (name, self.device_output_port_map[name]))

        # for i in range(128):
        #     for j in range(82):
        #         msg = [0x90, 0x0 + j, {0: 0x1, 1: 0x2, 2: 0x3, 3: 0x4, 4: 0x5, 5: 0x6}[(i % 3) * 2]]
        #         print("Sending msg: %s" % msg)
        #         try:
        #             self.open_device_map_midi_out[StringConstants.AKAI_MPC_NAME].send_message(msg)
        #         except:
        #             pass
        #         finally:
        #             time.sleep(.02)

        self.callback_dict_midimix = {"RecArm 1 Pressed": self.recarm_1_callback,
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
        return self.callback_dict_midimix

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
        state = self.akai_midimix_state.get()

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
                self.akai_midimix_state.previous()

        elif direction.lower() == "right":
            if self.context.scale_mode_changing_on:
                self.context.change_mode(offset=1)
            else:
                self.akai_midimix_state.next()

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
            for name in self.open_device_map_midi_in.keys():
                msg = self.open_device_map_midi_in[name].get_message()

                if msg:
                    msg, press_duration = msg
                    type_, controller, value = msg
                    str_controller = {StringConstants.AKAI_MIDIMIX_NAME: self.akai_midimix_message,
                                      StringConstants.AKAI_MPC_NAME: self.akai_apc_message}[name].get_name_by_msg(msg)

                    threading.Thread(target=lambda: print("MIDI Input Listener: %s: %s" % (str_controller, value))).start()

                    self._callback(msg)

            time.sleep(self.interval)

    def _callback(self, msg):
        msg_name = self.akai_midimix_message.get_name_by_msg(msg)
        value = self.akai_midimix_message.get_value(msg)

        if msg_name in self.callback_dict_midimix:
            self.callback_dict_midimix[msg_name]()

        elif msg_name == "Knob Row 1 Col 8":
            bpm_range_value = range_to_range(Ranges.MIDI_CC, Ranges.BPM, value)
            self.context.bpm.set(bpm_range_value)
            threading.Thread(target=lambda: print("Set BPM to %s" % bpm_range_value)).start()

        elif "Knob Row" in msg_name:
            knob_row = int(msg_name.split()[2])
            i = int(msg_name.split()[-1]) - 1

            if i == 7:
                return

            self.dict_sync_strvars = {1: (self.midimix_know_row_1_synced, self.sequencer.strvars_prob_skip_note),
                                      2: (self.midimix_know_row_2_synced, self.sequencer.strvars_prob_poly_abs),
                                      3: (self.midimix_know_row_3_synced, self.sequencer.strvars_prob_poly_rel)}

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

                if not self.midimix_fader_synced[i]:
                    if abs(int(velocities[i // 2].get()) - value) < MiscConstants.KNOB_SYNC_DISTANCE:
                        self.midimix_fader_synced[i] = True
                        velocities[i // 2].set(value)
                else:
                    velocities[i // 2].set(value)

            except:
                pass

        elif "Bank" in msg_name and "Pressed" in msg_name:
            self.bank_callback(direction=msg_name.split()[1])
