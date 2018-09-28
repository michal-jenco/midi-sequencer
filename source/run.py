import threading
import rtmidi
import time

from source.constants import StringConstants
from source.sequencer import Sequencer

midi = rtmidi.MidiOut()
available_ports = midi.get_ports()

print("Available MIDI devices:")
for dev in available_ports:
    print("\t%s" % dev)

for i, dev in enumerate(available_ports):
    if StringConstants().BESPECO_MIDI_NAME in dev:
        bespeco_port = i
        print("Bespeco port: %s" % bespeco_port)
        break

try:
    midi.open_port(bespeco_port)
except:
    midi.open_port(0)

thread_1 = threading.Thread(target=lambda: Sequencer(midi).show())
thread_1.start()
# thread_2 = threading.Thread(target=lambda: Sequencer(midi).show())
# thread_2.start()
