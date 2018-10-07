class B__i__n__a__r__y(object):
    class Constants(object):
        class NumberOfNotesInScale(object):
            twelve = 12

    @staticmethod
    def get_pcs(number):
        """From either binary string or integer"""

        if isinstance(number, str):
            if len(number) == B__i__n__a__r__y.Constants.NumberOfNotesInScale.twelve:
                return B__i__n__a__r__y.get_pcs_from_binary_string(number)
            else:
                return B__i__n__a__r__y.get_pcs_from_integer(int(number))

        elif isinstance(number, int):
            return B__i__n__a__r__y.get_pcs_from_integer(number)

    @staticmethod
    def get_binary_string_from_integer(integer):
        return str(bin(integer))[2:]

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
        # return [sum([cls + 12 * (i + 1) for i, cls in range(octaves)])]


if __name__ == '__main__':
    print(B__i__n__a__r__y.get_binary_string_from_integer(1234))
    print(B__i__n__a__r__y.get_pcs_from_integer(1234))
    print(B__i__n__a__r__y.get_pcs_from_binary_string("010101010101"))

    expanded = B__i__n__a__r__y.expand_pcs(
        B__i__n__a__r__y.get_pcs_from_binary_string("010101010101"), 2, True)
    print(expanded)

    for i in range(4096):
        string = "%s - %s - %s" % (i,
                                   B__i__n__a__r__y.get_binary_string_from_integer(i),
                                   B__i__n__a__r__y.get_pcs_from_integer(i))
        print(string)

