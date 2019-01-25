class RequestResponseObject:

    def __init__(
            self,
            request=None,
            callback=None,
    ):

        self.request = request
        self.response = None
        self.callback = callback
