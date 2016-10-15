
class RFERestartException(Exception):
    pass


class RFEConnectionError(Exception):
    pass


class RFEAlreadyConnected(RFEConnectionError):
    pass


class RFEAlreadyDisconnected(RFEConnectionError):
    pass
