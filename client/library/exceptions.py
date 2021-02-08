class ChatClientException(Exception):
    """The base exception class"""
    pass


class NoConnectionException(ChatClientException):
    """No client has been created yet"""
    pass
