import itertools
import random
import math


from source.parser_my import Parser

"""
def parse_permutations(seq, output_length=None, start=0, random_order=False, count=None):
    individual_permutations = ["".join(x) for x in itertools.permutations(seq)]
    
    if random_order:
        random.shuffle(individual_permutations)
    else:
        pass

    if count is not None:
        individual_permutations = individual_permutations[:count]
    
    output_string = "".join(individual_permutations)

    if not output_length:
        output_length = len(output_string)

    return output_string[start:start+output_length]


test = "0r+067"


for i in range(0, 10):
    out = parse_permutations(test, random_order=True)
    print(out)
    """


def parse_octave_sequence(_, text):
    result = []

    sequences = list(text.split(","))

    for seq in sequences:
        seq_list = seq.split()
        times = Parser().parse_param("x", seq)

        if times is None:
            times = 1

        for j in range(0, times):
            for i in range(0, len(seq_list)):
                result.append(int(seq_list[i])) if seq_list[i][0] != "x" else 0
                print(result)

    return result


# print(parse_octave_sequence("", "0 1 -1 0 2 x12, 4 5 6 x3"))


import tkinter as tk
import rtmidi
import time
from source.delay import Delay
from source.context import Context

root = tk.Tk()
context = Context(root)

context.midi = rtmidi.MidiOut()
context.midi.open_port(0)

note = [0x90, 60, 127]
scale = [0, 2, 3, 5, 7, 9, 10, 12]
notes = []

for i in range(0, 8):
    notes.append([note[0], note[1]+scale[i], note[2]])

for n in notes:
    x = lambda: Delay(context).run_delay_with_note(n, random.random(), None)
    Delay(context).create_thread_for_function(x)
    time.sleep(random.random())
