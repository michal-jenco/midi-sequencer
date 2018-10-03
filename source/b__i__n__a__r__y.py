class B__i__n__a__r__y(object):
    class Constants(object):
        class NumberOfNotesInScale(object):
            twelve = 12

    @staticmethod
    def get_binary_string_from_integer(integer):
        return str(bin(integer))[2:]

    @staticmethod
    def get_pitch_class_set_from_integer(integer):
        return B__i__n__a__r__y.get_pitch_class_set_from_binary_string(
            B__i__n__a__r__y.get_binary_string_from_integer(integer))

    @staticmethod
    def get_pitch_class_set_from_binary_string(string):
        return [i for i, bit in enumerate(string[::-1]) if int(bit)]

    @staticmethod
    def expand_pitch_class_set(pcs, octaves, top_up=False):
        res = pcs[:]

        for i in range(octaves):
            res += [a + B__i__n__a__r__y.Constants.NumberOfNotesInScale.twelve * (i + 1) for a in pcs]
        res += [B__i__n__a__r__y.Constants.NumberOfNotesInScale.twelve * (octaves + 1)] if top_up else []

        return res
        # return [sum([cls + 12 * (i + 1) for i, cls in range(octaves)])]


if __name__ == '__main__':
    print(B__i__n__a__r__y.get_binary_string_from_integer(1234))
    print(B__i__n__a__r__y.get_pitch_class_set_from_integer(1234))
    print(B__i__n__a__r__y.get_pitch_class_set_from_binary_string("010101010101"))

    expanded = B__i__n__a__r__y.expand_pitch_class_set(
        B__i__n__a__r__y.get_pitch_class_set_from_binary_string("010101010101"), 2, True)
    print(expanded)

    for i in range(4096):
        string = "%s - %s - %s" % (i,
                                   B__i__n__a__r__y.get_binary_string_from_integer(i),
                                   B__i__n__a__r__y.get_pitch_class_set_from_integer(i))
        print(string)

