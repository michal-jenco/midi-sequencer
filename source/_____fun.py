import os
from collections import OrderedDict

from source.functions import print_dict

all_files = os.listdir(os.getcwd())
py_file_contents = [open(f, "r").readlines() for f in all_files if f.endswith(".py")]
combined_lines = [line.strip() for file in py_file_contents for line in file if line != "\n" and line]

sorted_lines = sorted(combined_lines, key=lambda x: len(x), reverse=True)

count_dict = OrderedDict()

for line in sorted_lines:
    if line not in count_dict:
        count_dict[line] = 0
    count_dict[line] += 1

sorted_list = sorted(count_dict.items(), key=lambda o: o[1])
sorted_dict = OrderedDict(sorted_list)

print(os.linesep.join(sorted_lines))
print_dict(count_dict)
print_dict(sorted_dict)