
class TLSClientError(Exception):
    pass


class ConnectionError(TLSClientError):
    pass


class TimeoutError(TLSClientError):
    pass


class SSLError(TLSClientError):
    pass


class RequestError(TLSClientError):
    def __init__(self, message, status_code=None, response=None):
        self.status_code = status_code
        self.response = response
        super().__init__(message)
        