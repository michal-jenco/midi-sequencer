import time
import threading
import rtmidi
from rtmidi.midiutil import open_midiinput, open_midioutput
from tkinter import INSERT

from source.akai_messages import AkaiMidimixMessage, AkaiApcMessage
from source.akai_state import AkaiMidimixStateNames, AkaiMidimixState, AkaiApcState, AkaiApcStateNames
from source.akai_buttons import AkaiApcButtons
from source.functions import range_to_range, get_all_indices, insert_into_entry
from source.constants import Ranges, MiscConstants, StringConstants, SleepTimes, NumberOf


class MIDIInputListener(object):
    def __init__(self, sequencer, context, input_names, interval=SleepTimes.MIDI_INPUT_MAINLOOP):
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
        self.akai_message_midimix = AkaiMidimixMessage()
        self.akai_message_apc = AkaiApcMessage()
        self.akai_state_midimix = AkaiMidimixState(sequencer=sequencer)
        self.akai_state_apc = AkaiApcState(sequencer=sequencer)

        self.button_color_controller_apc, self.button_color_controller_midimix = None, None

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
                self.button_color_controller_apc = AkaiApcButtons.Controller(
                    midi=self.open_device_map_midi_out[name])

        self._callback_dict_midimix = {"RecArm 1 Pressed": self.recarm_1_callback_midimix,
                                       "RecArm 2 Pressed": self.recarm_2_callback_midimix,
                                       "RecArm 3 Pressed": self.recarm_3_callback_midimix,
                                       "RecArm 4 Pressed": self.recarm_4_callback_midimix,
                                       "RecArm 5 Pressed": self.recarm_5_callback_midimix,
                                       "RecArm 6 Pressed": self.recarm_6_callback_midimix,
                                       "RecArm 7 Pressed": self.recarm_7_callback_midimix,
                                       "RecArm 8 Pressed": self.recarm_8_callback_midimix,
                                       "Solo Pressed": self.solo_callback_midimix}

        self._callback_dict_apc = {"Up Pressed": self.up_callback_apc,
                                   "Down Pressed": self.down_callback_apc,
                                   "Left Pressed": self.left_callback_apc,
                                   "Right Pressed": self.right_callback_apc,
                                   "Volume Pressed": self.volume_callback_apc,
                                   "Pan Pressed": self.pan_callback_apc,
                                   "Send Pressed": self.send_callback_apc,
                                   "Device Pressed": self.device_callback_apc,
                                   "Shift Pressed": self.shift_pressed_callback_apc,
                                   "Shift Released": self.shift_released_callback_apc,
                                   "Clip Stop Pressed": self.clip_stop_callback_apc,
                                   "Solo Pressed": self.solo_callback_apc,
                                   "Rec Arm Pressed": self.rec_arm_callback_apc,
                                   "Mute Pressed": self.mute_callback_apc,
                                   "Select Pressed": self.select_callback_apc,
                                   "Free 1 Pressed": self.free_1_callback_apc,
                                   "Free 2 Pressed": self.free_2_callback_apc,
                                   "Stop All Clips Pressed": self.stop_all_clips_callback_apc,
                                   "Fader": lambda fader_number, value: self.fader_callback_apc(fader_number, value),
                                   "Button Pressed": lambda button_number: self.button_callback_apc(button_number)}

        self._callback_dict_entries_free = {
            self.sequencer.entry_off_arrays: self.sequencer.set_off_array,
            self.sequencer.entry_poly: self.sequencer.set_poly_absolute,
            self.sequencer.entry_mode_sequence: self.sequencer.set_mode_sequence,
            self.sequencer.entry_skip_note_sequential: self.sequencer.set_skip_note_sequential,
            self.sequencer.entry_skip_note_parallel: self.sequencer.set_skip_note_parallel,
            self.sequencer.entry_octave_sequences: self.sequencer.set_octave_sequences,
            self.sequencer.entry_transpose_sequences: self.sequencer.set_transpose_sequences,
            self.sequencer.entry_midi_channels: self.sequencer.set_midi_channels,
            self.sequencer.entry_note_scheduling: self.sequencer.set_note_scheduling_sequence}

        self.main_loop_thread = threading.Thread(target=self.main_loop, args=())
        self.main_loop_thread.setDaemon(True)
        self.main_loop_thread.start()

    def get_callback_dict(self):
        return self._callback_dict_midimix

    def recarm_1_callback_midimix(self):
        self.playback_on_callback_midimix()

    def recarm_2_callback_midimix(self):
        self.sequencer.end_all_notes()

    def recarm_3_callback_midimix(self):
        self.sequencer.reset_idx()

    def recarm_4_callback_midimix(self):
        self.context.scale_mode_changing_on = not self.context.scale_mode_changing_on
        self.sequencer.frame_status.update_scale_mode()

    def recarm_5_callback_midimix(self):
        self.sequencer.press_all_enters()

    def recarm_6_callback_midimix(self):
        self.mute_callback_midimix("mute")

    def recarm_7_callback_midimix(self):
        self.mute_callback_midimix("unmute")

    def recarm_8_callback_midimix(self):
        self.mute_callback_midimix("invert")

    def get_state_and_device(self):
        state = self.akai_state_midimix.get()

        if state is AkaiMidimixStateNames.MAIN:
            device = self.sequencer
        elif state is AkaiMidimixStateNames.SAMPLE_FRAME:
            device = self.sequencer.sample_frame

        return state, device

    def mute_callback_midimix(self, mode):
        _, device = self.get_state_and_device()

        if mode == "mute":
            device.mute_all()

        elif mode == "unmute":
            device.unmute_all()

        elif mode == "invert":
            device.invert_mute()

    def bank_callback_midimix(self, direction):
        if direction.lower() == "left":
            if self.context.scale_mode_changing_on:
                self.context.change_mode(offset=-1)
            else:
                self.akai_state_midimix.previous()

        elif direction.lower() == "right":
            if self.context.scale_mode_changing_on:
                self.context.change_mode(offset=1)
            else:
                self.akai_state_midimix.next()

    def bpm_callback_midimix(self, value):
        bpm_range_value = range_to_range(Ranges.MIDI_CC, Ranges.BPM, value)
        self.context.bpm.set(bpm_range_value)
        print("Set BPM to %s" % bpm_range_value)

    def playback_on_callback_midimix(self):
        self.context.playback_on = not self.context.playback_on

    def solo_callback_midimix(self):
        _, device = self.get_state_and_device()
        device.intvar_solo.set(not device.intvar_solo.get())

    def button_callback_apc(self, button_number):
        row, col = self._get_row_col_from_button_number(button_number)
        self.button_color_controller_apc.turn_off_row(row)
        self.button_color_controller_apc.set_color(button_number, AkaiApcButtons.Colors.Grid.green)
        reversed_entry_list = list(reversed(self.sequencer.akai_apc_entry_names))

        entry_to_focus = reversed_entry_list[row]

        if row == 5:
            self.context.change_mode(set_to=col)
            # insert_into_entry(self.sequencer.entry_mode_sequence, str(col))
            # self.sequencer.set_mode_sequence(None)
            return

        if (entry_to_focus is not self.sequencer.entry_root_sequences
                or self.akai_state_apc.current_state is AkaiApcStateNames.SHIFT):

            entry_to_focus.focus_set()
            self._set_correct_column(entry_to_focus, col)
            self._set_selection_range(col, entry_to_focus)

            self.button_color_controller_apc.set_color(button_number, AkaiApcButtons.Colors.Grid.green)

        else:
            if reversed_entry_list[row] is self.sequencer.entry_root_sequences:
                root_dict = {0: "e", 1: "f", 2: "g", 3: "a", 4: "b", 5: "c"}

                original_entry_content = self.sequencer.entry_root_sequences.get().split(StringConstants.multiple_entry_separator)

                if col in root_dict.keys():
                    root_str = root_dict[col]
                    original_entry_content[0] = " %s " % root_str
                    insert_into_entry(self.sequencer.entry_root_sequences,
                                      ("%s" % StringConstants.multiple_entry_separator).join(original_entry_content))

                else:
                    direction_dict = {6: -1, 7: 1}
                    notes_list = ["e", "f", "fs", "g", "gs", "a", "as", "b", "c", "cs", "d", "ds"]

                    current_root = original_entry_content[0].strip().lower()

                    if current_root in notes_list:
                        new_root = notes_list[(notes_list.index(current_root) + direction_dict[col]) % len(notes_list)]
                        original_entry_content[0] = " %s " % new_root
                        insert_into_entry(self.sequencer.entry_root_sequences,
                                          ("%s" % StringConstants.multiple_entry_separator).join(original_entry_content))

                self.sequencer.set_root_sequences(None)

    @staticmethod
    def _set_selection_range(col, entry_to_focus):
        indices = get_all_indices(entry_to_focus.get())

        if not indices:
            return

        if col == 0:
            start = 0
        else:
            start = indices[col - 1] + 1

        if col == (NumberOf.SEQUENCES - 1):
            start = indices[-1] + 1
            end = len(entry_to_focus.get())
        else:
            end = indices[col]

        print("Start: %s, End: %s" % (start, end))
        entry_to_focus.selection_range(start, end)

    @staticmethod
    def _get_row_col_from_button_number(button_number):
        row, col = button_number // 8, button_number % 8
        return row, col

    def fader_callback_apc(self, i, value):
        pass

    def _up_down_callback_base(self, direction):
        focused_widget = self.sequencer.get_focused_widget()

        if focused_widget not in self.sequencer.entry_names:
            self.sequencer.entry_memory_sequences.focus_set()

        _, track_column = self._get_col_to_display(focused_widget)

        if StringConstants.multiple_entry_separator not in focused_widget.get():
            track_column = self.akai_state_apc.previous_column

        next_entry = self.sequencer.entry_names[
            (self.sequencer.entry_names.index(focused_widget) + direction) % len(self.sequencer.entry_names)]

        next_entry.focus_set()
        self._set_selection_range(track_column, next_entry)

        if StringConstants.multiple_entry_separator in next_entry.get():
            self._set_correct_column(next_entry, track_column)
        else:
            self.akai_state_apc.previous_column = track_column

    def up_callback_apc(self):
        self._up_down_callback_base(-1)

    def down_callback_apc(self):
        self._up_down_callback_base(1)

    def _left_right_callback_base(self, direction):
        focused_widget = self.sequencer.get_focused_widget()

        if focused_widget in self.sequencer.entry_names:
            indices = get_all_indices(focused_widget.get())

            if not indices:
                return

            actual_column, col_button = self._get_col_to_display(focused_widget)

            if (col_button == (NumberOf.SEQUENCES - 2) and direction == 1) or (col_button == 0 and direction == -1):
                focused_widget.icursor(len(focused_widget.get()))
                self._set_selection_range(NumberOf.SEQUENCES - 1, focused_widget)
                return

            if col_button == (NumberOf.SEQUENCES - 1) and direction == 1:
                focused_widget.icursor(indices[0] - 1)
                self._set_selection_range(0, focused_widget)
                return

            indices_index = (col_button + direction) % len(indices)
            focused_widget.icursor(indices[indices_index])
            self._set_selection_range(col_button + direction, focused_widget)

        else:
            pass

    def left_callback_apc(self):
        self._left_right_callback_base(-1)

    def right_callback_apc(self):
        self._left_right_callback_base(1)

    def volume_callback_apc(self):
        pass

    def pan_callback_apc(self):
        pass

    def send_callback_apc(self):
        pass

    def device_callback_apc(self):
        pass

    def shift_pressed_callback_apc(self):
        self.akai_state_apc.turn_on_shift()
        focused_widget = self.sequencer.get_focused_widget()

        if focused_widget in self.sequencer.akai_apc_entry_names:
            row = list(reversed(self.sequencer.akai_apc_entry_names)).index(focused_widget)

            _, col_button = self._get_col_to_display(focused_widget)
            button_number = row * 8 + col_button

            self.button_color_controller_apc.set_color(button_number, AkaiApcButtons.Colors.Grid.green)
        else:
            self.button_color_controller_apc.set_all_grid_to_color(AkaiApcButtons.Colors.Grid.yellow_blink)

    def shift_released_callback_apc(self):
        self.akai_state_apc.turn_off_shift()

    @staticmethod
    def _get_col_to_display(focused_widget):
        """Returns actual cursor column and column the cursor is in entry box based on multiple entry separator"""

        cursor_column_in_widget = focused_widget.index(INSERT)
        indices = get_all_indices(focused_widget.get())

        for i in reversed(indices):
            if i < cursor_column_in_widget:
                return i, indices.index(i) + 1

        try:
            return indices[0] - 2, 0
        except:
            return 0, 0

    def clip_stop_callback_apc(self):
        pass

    def solo_callback_apc(self):
        pass

    def rec_arm_callback_apc(self):
        pass

    def mute_callback_apc(self):
        pass

    def select_callback_apc(self):
        pass

    def free_callback_base(self, direction):
        focused_widget = self.sequencer.get_focused_widget()

        if focused_widget in self._callback_dict_entries_free.keys():
            widget_content = focused_widget.get()
            content_list = widget_content.split(StringConstants.multiple_entry_separator)
            _, track_column = self._get_col_to_display(focused_widget)

            if StringConstants.multiple_entry_separator not in widget_content:
                current_cell_list = [str(widget_content).strip()]
            else:
                current_cell_list = content_list[track_column].split()

            if not current_cell_list:
                return

            times_sequences = []
            for i, item in enumerate(current_cell_list):
                if StringConstants.times in item:
                    times_idx = item.index(StringConstants.times)
                    times_sequences.append(item[times_idx:])
                    item = item[:times_idx]
                else:
                    times_sequences.append(None)

                integer_item_repr, idx_of_end = "", None

                for idx, char in enumerate(item):
                    if char in ("+", "-"):
                        continue
                    try:
                        int(char)
                    except:
                        idx_of_end = idx
                        break
                    else:
                        integer_item_repr += char

                if focused_widget is self.sequencer.entry_note_scheduling:
                    rest = None if idx_of_end is None else item[idx_of_end:]
                    item = int(integer_item_repr)

                    value = item // 2 if direction == 1 else item * 2

                    if value > 64:
                        value = 64
                    elif value < 1:
                        value = 1

                    current_cell_list[i] = str(value) + (rest if rest is not None else "")

                # elif focused_widget is self._callback_dict_entries_free.keys():


                else:
                    item = int(item)
                    current_cell_list[i] = item + direction

            result = " ".join((str(value) + (times_sequences[i] if times_sequences[i] is not None else "")) for i, value in enumerate(current_cell_list))
            current_cell_list = " %s " % result

            content_list[track_column] = current_cell_list
            insert_into_entry(focused_widget, "|".join(content_list))
            self._set_correct_column(focused_widget, track_column)

            self._callback_dict_entries_free[focused_widget](None)

    @staticmethod
    def _set_correct_column(focused_widget, track_column):
        indices = get_all_indices(focused_widget.get())

        if not indices:
            return

        if track_column == (NumberOf.SEQUENCES - 1):
            focused_widget.icursor(len(focused_widget.get()))
        else:
            focused_widget.icursor(indices[track_column] - 1)

    def free_1_callback_apc(self):
        """Plus"""

        self.free_callback_base(1)

    def free_2_callback_apc(self):
        """Minus"""

        self.free_callback_base(-1)

    def stop_all_clips_callback_apc(self):
        self.sequencer.press_all_enters()

    def main_loop(self):
        while True:
            for name in self.open_device_map_midi_in.keys():
                msg = self.open_device_map_midi_in[name].get_message()

                if msg:
                    msg, press_duration = msg
                    type_, controller, value = msg
                    str_controller = {StringConstants.AKAI_MIDIMIX_NAME: self.akai_message_midimix,
                                      StringConstants.AKAI_APC_NAME: self.akai_message_apc}[name].get_name_by_msg(msg)

                    threading.Thread(target=lambda: print("MIDI Input Listener: %s: %s" % (str_controller, value))).start()

                    {StringConstants.AKAI_MIDIMIX_NAME: self._callback_midimix,
                     StringConstants.AKAI_APC_NAME: self._callback_apc}[name](msg)

            time.sleep(self.interval)

    def _callback_apc(self, msg):
        msg_name = self.akai_message_apc.get_name_by_msg(msg)
        value = self.akai_message_apc.get_value(msg)

        if msg_name in self._callback_dict_apc:
            self._callback_dict_apc[msg_name]()

        elif "Button" in msg_name and "Pressed" in msg_name:
            button_number = int(msg_name.split()[1])
            self._callback_dict_apc["Button Pressed"](button_number)

        elif "Fader" in msg_name:
            fader_number = int(msg_name.split()[-1])
            self._callback_dict_apc["Fader"](fader_number, value)

    def _callback_midimix(self, msg):
        msg_name = self.akai_message_midimix.get_name_by_msg(msg)
        value = self.akai_message_midimix.get_value(msg)

        if msg_name in self._callback_dict_midimix:
            self._callback_dict_midimix[msg_name]()

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

            if state is AkaiMidimixStateNames.MAIN:
                intvars = device.intvars_enable_channels
            elif state is AkaiMidimixStateNames.SAMPLE_FRAME:
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
            self.bank_callback_midimix(direction=msg_name.split()[1])
