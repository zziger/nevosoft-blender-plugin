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
