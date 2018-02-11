import random
import time


def a(mult=1):
    return random.random()*mult


def sleep_and_increase_time(sleep_time, time_var):
    time.sleep(sleep_time)
    time_var += sleep_time
