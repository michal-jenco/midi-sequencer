from math import log2


def generate_binary_numbers(a=0, b=31, zerofill=None):
    if zerofill is None:
        zerofill = int(log2(b)) + 1
    return [str(bin(i))[2:].zfill(zerofill) for i in range(a, b + 1)]


def experiment1(input):
    a = "0123456789abcdedcba987654321"
    return [item if item == "0" else a[i % len(a)] for i, item in enumerate(input)]


if __name__ == '__main__':
    print("".join(generate_binary_numbers()))
    print("".join(experiment1("".join(generate_binary_numbers()))))