from sequencer import Sequencer
import threading
import rtmidi

midi = rtmidi.MidiOut()

available_ports = midi.get_ports()
print(available_ports)

midi_port = 1

try:
    midi.open_port(midi_port)
except:
    midi.open_port(midi_port-1)

thread_keys = threading.Thread(target=lambda: Sequencer(midi).show(), args=())
thread_sample = threading.Thread(target=lambda: Sequencer(midi).show(), args=())
thread_3 = threading.Thread(target=lambda: Sequencer(midi).show(), args=())

thread_keys.start()
# thread_sample.start()
# thread_3.start()
