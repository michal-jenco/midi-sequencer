import time
import threading
import rtmidi
from rtmidi.midiutil import open_midiinput

from source.akai_midimix_message import AkaiMidimixMessage
from source.functions import range_to_range
from source.constants import Ranges


class MIDIInputListener(object):
    def __init__(self, sequencer, context, input_name, queue, interval):
        self.sequencer = sequencer
        self.context = context
        self.input_name = input_name
        self.interval = interval
        self.queue = queue

        self.midi = rtmidi.MidiIn()
        self.akai_message = AkaiMidimixMessage()

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

        self.main_loop_thread = threading.Thread(target=self.main_loop, args=())
        self.main_loop_thread.setDaemon(True)
        self.main_loop_thread.start()

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

        if msg_name == "Knob Row 1 Col 8":
            bpm_range_value = range_to_range(Ranges.MIDI_RANGE, Ranges.BPM_RANGE, value)
            self.context.bpm.set(bpm_range_value)
            print("Set BPM to %s" % bpm_range_value)

        elif msg_name == "RecArm 1 Pressed":
            self.context.playback_on = not self.context.playback_on

        elif msg_name == "RecArm 2 Pressed":
            self.sequencer.end_all_notes()

        elif msg_name == "RecArm 3 Pressed":
            self.sequencer.reset_idx()

        elif msg_name == "RecArm 4 Pressed":
            self.sequencer.init_entries()

        elif msg_name == "RecArm 5 Pressed":
            self.sequencer.press_all_enters()

        elif "Fader" in msg_name:
            try:
                i = int(msg_name.split()[-1]) - 1
                velocity_value = value

                if i % 2 == 0:
                    self.sequencer.velocities_strvars_min[i//2].set(velocity_value)
                else:
                    self.sequencer.velocities_strvars_max[i//2].set(velocity_value)

            except:
                pass
