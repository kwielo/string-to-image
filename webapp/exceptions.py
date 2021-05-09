class Error(Exception):
    pass


class QueryParameterError(Error):
    def __init__(self, expression, message):
        self.expression = expression
        self.message = message
