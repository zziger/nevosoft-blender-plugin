class OperatorBase:
    def message(self, msg):
        print("INFO:", msg)
        self.report({"INFO"}, msg)

    def warning(self, msg):
        print("WARNING:", msg)
        self.report({"WARNING"}, msg)

    def error(self, msg, logToConsole=True):
        if logToConsole:
            print("ERROR:", msg)
        self.report({"ERROR"}, msg)


class ErrorException(Exception):
    pass


def getBoneTag(bone):
    if bone['tag'] == None:
        return -1
    return bone['tag']

def findBoneByTag(bones, tag: int):
    return next(filter(lambda e: getBoneTag(e) == tag, bones), None)