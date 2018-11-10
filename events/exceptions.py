class Error(Exception):
    """Base class for exceptions in this module."""
    pass


class NodeBlockingException(Error):
    """Exception raised when a node is blocking.

    Attributes:
        expression -- input expression in which the error occurred
        message -- explanation of the error
    """

    def __init__(self, expression, message):
        self.expression = expression
        self.message = message


class NoTransactionFound(Exception):
    pass
