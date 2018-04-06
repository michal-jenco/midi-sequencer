import datetime


def log(msg=""):
    result = "[%s]: \"%s\"" % (str(datetime.datetime.now()), msg)
    print(result)
