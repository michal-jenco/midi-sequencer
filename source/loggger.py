import datetime
import os


class Loggger(object):
    def __init__(self, directory):
        self.frequency = 50
        self.cnt = 0
        self.directory = directory
        self.filename = str(datetime.datetime.now()).rsplit(".")[0].split(" ")[0] + ".midi"
        self.open_file = open(os.path.join(self.directory, self.filename), "a")

    def __del__(self):
        self.open_file.flush()
        self.open_file.close()

    def log(self, msg):
        # print("logging: {}".format(msg))
        self.open_file.write("[{}]:\t{}\n".format(str(datetime.datetime.now()), msg))
        self.cnt += 1

        if not self.cnt % self.frequency:
            self.open_file.flush()
