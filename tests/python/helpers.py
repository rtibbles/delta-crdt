from delta_crdt.codec import decode
from delta_crdt.codec import encode


def transmit(delta):
    return decode(encode(delta))
