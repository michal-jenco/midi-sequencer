import threading
import rtmidi
import time

midi = rtmidi.MidiOut()

available_ports = midi.get_ports()
print(available_ports)

midi_port = 1

try:
    midi.open_port(midi_port)
except Exception:
    midi.open_port(midi_port-1)

bpm = 60

notes = [[0x90, 54+x*2, 110] for x in range(0, 4)]
note_lengths = [32, 32, 16, 16]

print(note_lengths)
print(notes)

sleep_count = 0
note_count = 0
while True:

    note_idx = note_count % notes.__len__()

    print("%s, %s, %s, %s" % (sleep_count, sleep_count % note_lengths[note_idx], note_idx, note_lengths[note_idx]-1))

    if sleep_count % note_lengths[note_idx] == note_lengths[note_idx]-1:
        msg = notes[note_idx]
        midi.send_message(msg)
        note_count += 1

    time.sleep(bpm/60/64)
    sleep_count += 1


