import time
import threading
import rtmidi
from rtmidi.midiutil import open_midiinput

from source.akai_midimix_message import AkaiMidimixMessage


class MIDIInputListener(object):
    def __init__(self, input_name, queue, interval):
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
                str_controller = self.akai_message.get_name_by_index(type_, controller)

                print("MIDI Input Listener: %s - %s" % (str_controller, value))

                self.queue.put(msg)

            time.sleep(self.interval)
