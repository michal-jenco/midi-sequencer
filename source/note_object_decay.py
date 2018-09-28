import math

from source.constants import Ranges, StringConstants
from source.functions import range_to_range


class DecayFunctionDictMetaclass(type):
    @staticmethod
    def __getitem__(key):
        return getattr(DecayFunctionDict, key.lower())

    @staticmethod
    def __setitem__(key, value):
        setattr(DecayFunctionDict, key.lower(), value)


class DecayFunctionDict(metaclass=DecayFunctionDictMetaclass):
    @staticmethod
    def _logical_sin(i, smooth=1, min=0., max=1., *args):
        return range_to_range(Ranges.LOGICAL, (min, max), (math.sin(i / smooth) + 1) / 2.)

    @staticmethod
    def _logical_cos(i, smooth=1, min=0., max=1., *args):
        return range_to_range(Ranges.LOGICAL, (min, max), (math.cos(i / smooth) + 1) / 2.)

    sin = _logical_sin
    cos = _logical_cos


class DecayFunctionParameter:
    def __init__(self, name, value):
        self.name = name
        self.value = value

    def __repr__(self):
        msg = "%s \"%s\": value \"%s\"." % (self.__class__.__name__, self.name, self.value)
        return msg

    def __str__(self):
        return self.__repr__()


class DecayFunction:
    def __init__(self, entry_box_string):
        self.original_entry_box_string = entry_box_string
        self.func, self.parameters, self.name = self._parse_original_entry_box_string()

    def __repr__(self):
        msg = "DecayFunction \"%s\". Parameters: %s." % (self.func.__name__ if self.func is not None else None,
                                                         self.parameters)
        return msg

    def __call__(self, *args):
        return self.func(*args)

    def _parse_original_entry_box_string(self):
        items = (self.original_entry_box_string.split(StringConstants.container_separator)
                 if StringConstants.container_separator in self.original_entry_box_string
                 else [self.original_entry_box_string])

        if not self.original_entry_box_string:
            return None, None, None

        if len(items) == 1:
            func = DecayFunctionDict[items[0]]
            return func, None, func.__name__

        elif len(items) > 1:
            func = DecayFunctionDict[items[0]]
            return func, [float(item) for item in items[1:]], func.__name__