import itertools
import random


def parse_permutations(seq, output_length=None, start=0, random_order=False, count=None):
    individual_permutations = ["".join(x) for x in itertools.permutations(seq)]
    
    if random_order:
        random.shuffle(individual_permutations)
    else:
        pass

    if count is not None:
        individual_permutations = individual_permutations[:count]
    
    output_string = "".join(individual_permutations)

    if not output_length:
        output_length = len(output_string)

    return output_string[start:start+output_length]


test = "0r+067"


for i in range(0, 10):
    out = parse_permutations(test, random_order=True)
    print(out)

