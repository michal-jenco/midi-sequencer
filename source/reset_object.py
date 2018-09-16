from source.constants import StringConstants


class ResetObject(object):
    def __init__(self, entry_string):
        self.entry_string = entry_string
        self.reset_at_index, self.reset_to_index, self.reset_after = reset_parser(entry_string)

    def __repr__(self):
        return "(Reset AT: %s, Reset TO: %s)" % (self.reset_at_index, self.reset_to_index)

    def get_new_index(self, sequencer_index):
        if sequencer_index == self.reset_at_index:
            return self.reset_to_index
        return None


def reset_parser(entry_string):
    if StringConstants.reset_delimiter not in entry_string:
        return int(entry_string), 0, None

    items = entry_string.split(StringConstants.reset_delimiter)

    if len(items) == 2:
        return int(items[1]), int(items[0]), None

