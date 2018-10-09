import threading
import time
import random

from source.constants import DelayFunctions, DelayConstants


class Delay:
    def __init__(self, context):
        self.context = context

        self.notes = []
        self.global_delay_time = 1.

        self.df = DelayFunctions()
        self.dc = DelayConstants()

    def run_delay_with_note(self, note, delay_time, func, decay_param):
        self.context.midi.send_message(note)
        time.sleep(delay_time)

        note = func(note, decay_param)

        if note[2] > 0:
            self.run_delay_with_note(note, delay_time, func, decay_param)

        else:
            return

    @staticmethod
    def create_thread_for_function(func):
        thr = threading.Thread(target=func, args=())
        thr.start()
