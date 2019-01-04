from source.constants import StringConstants as Constants
from source.functions import range_to_range, rotate
import math


class ParamNames(object):
    class sin(object):
        speed = "speed"
        amplitude = "amp"
        phase = "phase"
        offset = "offset"

    @staticmethod
    def get(func_name):
        return getattr(ParamNames, func_name)

    @staticmethod
    def get_all(func_name):
        return [value for value in getattr(ParamNames, func_name).__dict__.values()]


class GeneratorParser(object):
    _needed_call_kwargs_dict = {"sin": ParamNames.get_all("sin")}
    _needed_range_kwargs_dict = {"sin": ["amp", "offset"]}

    @staticmethod
    def parse(string):
        attributes = string.split(Constants.literal_memory_sequence_separator)
        func = attributes[0]

        params = {item.split(Constants.generator_param_delimiter)[0]:
                  item.split(Constants.generator_param_delimiter)[1] for item in attributes[1:]}

        if "oct" in params:
            params["octaves"] = params["oct"]
        if "o" in params:
            params["octaves"] = params["o"]
        if "n" in params:
            params["notes"] = params["n"]

        params = GeneratorParser.fill_missing_params(func, params)
        params = GeneratorParser._make_kwargs_float(params)

        if Constants.generator_spacer_delimiter in params["spacer"]:
            params["spacer"] = params["spacer"].split(Constants.generator_spacer_delimiter)
        else:
            params["spacer"] = [params["spacer"]]

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
           ParamNames.sin.offset: 0.,
           "octaves": ""}

    @staticmethod
    def get(func_name):
        return getattr(DefaultParams, func_name)


class G_e__n_e__r_a__t_o__r_________Range(object):
    _dict = {"sin": lambda amp=1, offset=0: (-1 * amp + offset, amp + offset)}

    @staticmethod
    def get(func_name_string, **kwargs):
        kwargs = GeneratorParser.get_needed_kwargs_call(func_name_string, kwargs)

        return G_e__n_e__r_a__t_o__r_________Range._dict[func_name_string](
            **GeneratorParser.get_needed_kwargs_range(func_name_string, kwargs))


class G_e__n_e__r_a__t_o__r_________Funcs(object):
    sin = lambda x, speed, amp, phase, offset: math.sin((x + phase) / speed) * amp + offset

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
        self.notes = list(self.params["notes"])
        self.spacer = self.params["spacer"]
        self.octaves = self.params["octaves"]

        self._manage_octaves()

    def _manage_octaves(self):
        if self.octaves:
            if "-" in self.octaves:
                self.notes = [("%s-" % note) for note in self.notes] + self.notes
            if "+" in self.octaves:
                self.notes += [("%s+" % note) for note in self.notes]

    def __repr__(self):
        return (("%s:\n" % self.__class__.__name__)
                + "\n".join([("\t%s: %s" % (key, str(value))) for key, value in self.__dict__.items()]))

    def get_entrybox_repr(self):
        range_from = G_e__n_e__r_a__t_o__r_________Range.get(self.params["func"], **self.params)
        range_to = 0, len(self.notes)

        result = [self.notes[int(range_to_range(range_from, range_to, val))] + self.spacer[i % len(self.spacer)]
                  for i, val in enumerate(self.func(**self.params))]

        if "uniq" in self.params:
            result = self._squash_sequences(result)

        return "".join(rotate(result, int(self.params["offset"])))

    @staticmethod
    def _squash_sequences(lst):
        # replace xxx with x,,
        result = []
        last = ""

        for item in lst:
            if item == last:
                result.append(",")
            else:
                result.append(item)
            last = item

        return result


# test_string = "sin;len=16;speed=.2;amp=10;phase=;offset=-1;notes=0,2,,3+;spacer=,*,,*,,g302g,;oct=+1-1;uniq="
#
# gen = _____G_e__n_e__r_a__t_o__r_________(test_string)
#
# print(gen.get_entrybox_repr())
# print(GeneratorParser.parse(test_string))
