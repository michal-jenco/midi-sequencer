import datetime


def log(logfile=None, msg=""):
    result = "[%s]: \"%s\"%s" % (str(datetime.datetime.now()), msg, "\n")

    if logfile is not None:
        logfile.write(result)
        logfile.flush()

    print(result)
