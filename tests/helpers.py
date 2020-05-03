from delta_crdts.codec import decode
from delta_crdts.codec import encode


def transmit(delta):
    return decode(encode(delta))
