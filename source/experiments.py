from math import log2


def generate_binary_numbers(a=0, b=31, zerofill=None):
    if zerofill is None:
        zerofill = int(log2(b)) + 1
    return [str(bin(i))[2:].zfill(zerofill) for i in range(a, b + 1)]


if __name__ == '__main__':
    print("".join(generate_binary_numbers()))