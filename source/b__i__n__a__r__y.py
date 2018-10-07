from source.scale_names import scale_names_dict


class B__i__n__a__r__y(object):
    class Constants(object):
        class NumberOfNotesInScale(object):
            twelve = 12

    @staticmethod
    def get_pcs(number):
        """From either binary string, string integer or integer."""

        if isinstance(number, str):
            if len(number) == B__i__n__a__r__y.Constants.NumberOfNotesInScale.twelve:
                return B__i__n__a__r__y.get_pcs_from_binary_string(number)
            else:
                return B__i__n__a__r__y.get_pcs_from_integer(int(number))

        elif isinstance(number, int):
            return B__i__n__a__r__y.get_pcs_from_integer(number)

    @staticmethod
    def get_scale_name(input):
        """From either binary string, integer string, integer or pitch class set."""
        key = None

        if isinstance(input, str):
            if len(input) == B__i__n__a__r__y.Constants.NumberOfNotesInScale.twelve:
                key = scale_names_dict[int(input, 2)]
            else:
                key = scale_names_dict[int(input)]
        elif isinstance(input, int):
            key = input
        elif isinstance(input, list):
            key = B__i__n__a__r__y.get_integer_from_pcs(input)

        return None if key not in scale_names_dict else scale_names_dict[key]

    @staticmethod
    def get_binary_string_from_integer(integer):
        return str(bin(integer))[2:]

    @staticmethod
    def get_integer_from_pcs(pcs):
        return sum(2 ** i for i in pcs)

    @staticmethod
    def get_binary_string_from_pcs(pcs):
        return B__i__n__a__r__y.get_binary_string_from_integer(B__i__n__a__r__y.get_integer_from_pcs(pcs))

    @staticmethod
    def get_pcs_from_integer(integer):
        return B__i__n__a__r__y.get_pcs_from_binary_string(
            B__i__n__a__r__y.get_binary_string_from_integer(integer))

    @staticmethod
    def get_pcs_from_binary_string(string):
        return [i for i, bit in enumerate(string[::-1]) if int(bit)]

    @staticmethod
    def expand_pcs(pcs, octaves, top_up=False):
        res = pcs[:]

        for i in range(octaves):
            res += [a + B__i__n__a__r__y.Constants.NumberOfNotesInScale.twelve * (i + 1) for a in pcs]
        res += [B__i__n__a__r__y.Constants.NumberOfNotesInScale.twelve * (octaves + 1)] if top_up else []

        return res
        # return [sum([cls + 12 * (_ + 1) for _, cls in range(octaves)])]


if __name__ == '__main__':
    print(B__i__n__a__r__y.get_binary_string_from_integer(1234))
    print(B__i__n__a__r__y.get_pcs_from_integer(1234))
    print(B__i__n__a__r__y.get_pcs_from_binary_string("010101010101"))

    expanded = B__i__n__a__r__y.expand_pcs(
        B__i__n__a__r__y.get_pcs_from_binary_string("010101010101"), 2, True)
    print(expanded)

    for _ in range(4096):
        string = "%s - %s - %s - %s" % (_,
                                        B__i__n__a__r__y.get_binary_string_from_integer(_),
                                        B__i__n__a__r__y.get_pcs_from_integer(_),
                                        B__i__n__a__r__y.get_scale_name(_))
        print(string)

    print(B__i__n__a__r__y.get_scale_name([0, 1, 3, 5, 7, 9, 11]))
    print(B__i__n__a__r__y.get_binary_string_from_pcs([0, 1, 3, 5, 7, 9, 11]))