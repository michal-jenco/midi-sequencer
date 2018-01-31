import tkinter as tk

from parser_my import Parser
from context import Context
from scales import Scales
from notes import *
from constants import *

root = tk.Tk()

scales = Scales()
context = Context(root)

context.root = c2
context.scale = scales.get_random()
context.mode = MODE_SIMPLE

parser_ = Parser()

seq = parser_.get_notes(context, "020301543 ro-2+1")

