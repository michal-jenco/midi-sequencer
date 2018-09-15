from source.constants import StringConstants as Constants
from source.functions import range_to_range, rotate
import math


class ParamNames(object):
    class sin(object):
        speed = "speed"
        amplitude = "amp"
        phase = "phase"
        offset = "offset"

    tanh = sin

    @staticmethod
    def get(func_name):
        return getattr(ParamNames, func_name)

    @staticmethod
    def get_all(func_name):
        return [value for value in getattr(ParamNames, func_name).__dict__.values()]


class GeneratorParser(object):
    _needed_call_kwargs_dict = {"sin": ParamNames.get_all("sin"),
                                "tanh": ParamNames.get_all("tanh")}
    _needed_range_kwargs_dict = {"sin": ["amp", "offset"],
                                 "tanh": ["amp"]}

    @staticmethod
    def parse(string):
        attributes = string.split(Constants.literal_memory_sequence_separator)
        func = attributes[0]

        params = {item.split(Constants.generator_param_delimiter)[0]:
                  item.split(Constants.generator_param_delimiter)[1] for item in attributes[1:]}

        params = GeneratorParser.fill_missing_params(func, params)
        params = GeneratorParser._make_kwargs_float(params)
        return params

    @staticmethod
    def _make_kwargs_float(dict_):
        for key, value in dict_.items():
            if key in ("notes", "spacer"):
                continue

            try:
                float(value)
            except:
                pass
            else:
                dict_[key] = float(value)
        return dict_

    @staticmethod
    def get_needed_kwargs_call(func_name, dict_):
        new_dict = {}

        for needed in GeneratorParser._needed_call_kwargs_dict[func_name]:
            try:
                new_dict[needed] = dict_[needed]
            except:
                pass

        return new_dict

    @staticmethod
    def get_needed_kwargs_range(func_name, dict_):
        new_dict = {}

        for needed in GeneratorParser._needed_range_kwargs_dict[func_name]:
            try:
                new_dict[needed] = dict_[needed]
            except:
                pass

        return new_dict

    @staticmethod
    def fill_missing_params(func_name, dict_):
        defaults = DefaultParams.get(func_name)
        dict_["func"] = func_name

        if "spacer" not in dict_:
            dict_["spacer"] = ""

        for param in defaults:
            if param not in dict_ or not dict_[param]:
                dict_[param] = defaults[param]

        return dict_


class DefaultParams(object):
    sin = {ParamNames.sin.speed: 1.,
           ParamNames.sin.amplitude: 1.,
           ParamNames.sin.phase: 0.,
           ParamNames.sin.offset: 0.}

    tanh = sin

    @staticmethod
    def get(func_name):
        return getattr(DefaultParams, func_name)


class G_e__n_e__r_a__t_o__r_________Range(object):
    _dict = {"sin": lambda amp=1, offset=0: (-1 * amp + offset, amp + offset),
             "tanh": lambda amp=1: (-Constants.max_tanh * amp, Constants.max_tanh * amp)}

    @staticmethod
    def get(func_name_string, **kwargs):
        kwargs = GeneratorParser.get_needed_kwargs_call(func_name_string, kwargs)

        return G_e__n_e__r_a__t_o__r_________Range._dict[func_name_string](
            **GeneratorParser.get_needed_kwargs_range(func_name_string, kwargs))


class G_e__n_e__r_a__t_o__r_________Funcs(object):
    sin = lambda x, speed, amp, phase, offset: math.sin((x + phase) / speed) * amp + offset
    tanh = lambda x, speed, amp, phase, offset: abs(math.tanh((x + phase) / speed) * amp + offset) % Constants.max_tanh

    @staticmethod
    def get(string):
        return getattr(G_e__n_e__r_a__t_o__r_________Funcs, string)


class G_e__n_e__r_a__t_o__r_________Func(object):
    def __init__(self, func_name):
        self.func_name = func_name

    def __call__(self, **kwargs):
        length = int(kwargs["len"])
        func_params = GeneratorParser.get_needed_kwargs_call(self.func_name, kwargs)
        return [G_e__n_e__r_a__t_o__r_________Funcs.get(self.func_name)(i, **func_params) for i in range(length)]

    def __repr__(self):
        return (("%s:\n" % self.__class__.__name__)
                + "\n".join([("\t%s: %s" % (key, str(value))) for key, value in self.__dict__.items()]))


class _____G_e__n_e__r_a__t_o__r_________(object):
    def __init__(self, func_entry_box_string):
        self.params = GeneratorParser.parse(func_entry_box_string)
        self.func = G_e__n_e__r_a__t_o__r_________Func(self.params["func"])
        self.length = int(self.params["len"])
        self.notes = self.params["notes"]
        self.spacer = self.params["spacer"]

    def __repr__(self):
        return (("%s:\n" % self.__class__.__name__)
                + "\n".join([("\t%s: %s" % (key, str(value))) for key, value in self.__dict__.items()]))

    def get_entrybox_repr(self):
        result = []

        range_from = G_e__n_e__r_a__t_o__r_________Range.get(self.params["func"], **self.params)
        range_to = (0, len(self.notes) - 1)

        print("notes: %s" % self.notes)
        print("range_from: %s" % (range_from,))
        print("range_to: %s" % (range_to,))

        for val in self.func(**self.params):
            print("int(range_to_range(range_from, range_to, val)): %s" % int(range_to_range(range_from, range_to, val)))
            if self.notes:
                result.append(self.notes[int(range_to_range(range_from, range_to, val))])
                result.append(self.spacer)

        return "".join(rotate(result, int(self.params["offset"])))

#
# test_string = "sin;len=16;speed=.2;amp=10;phase=;offset=-1;notes=0,2,,3;oct=+1-1"
#
# gen = _____G_e__n_e__r_a__t_o__r_________(func_entry_box_string=test_string)
#
# print(gen.get_entrybox_repr())
# print(GeneratorParser.parse(test_string))
#
