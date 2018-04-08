import datetime


def log(logfile=None, msg=""):
    result = "[%s]: \"%s\"%s" % (str(datetime.datetime.now()), msg, "\n")

    if logfile is not None:
        logfile.write(result)
        logfile.flush()

    print(result)


def get_date_string(type):
    result = ""

    if type == "filename":
        result = str(datetime.datetime.now()).split(".")[0].replace(":", "-").replace(" ", "-")

    return result
