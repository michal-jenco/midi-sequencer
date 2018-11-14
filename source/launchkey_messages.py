class LaunchkeyMessage(object):
    def __init__(self):
        pass

    def get_name_by_msg(self, msg):
        return str(msg)

    @staticmethod
    def get_value(msg):
        return msg[2]
