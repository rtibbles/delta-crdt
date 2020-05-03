import msgpack
from .base import Map

__MAP_CODE = 64
__SET_CODE = 65

__MAP_TYPE = Map
__SET_TYPE = set


def __encode_map(obj):
    return msgpack.ExtType(__MAP_CODE, encode(list(obj.items())))


def __encode_set(obj):
    return msgpack.ExtType(__SET_CODE, encode(list(obj)))


def __default(obj):
    if isinstance(obj, __MAP_TYPE):
        return __encode_map(obj)
    if isinstance(obj, __SET_TYPE):
        return __encode_set(obj)
    raise TypeError("Unknown type: %r" % (obj,))


def __decode_map(data):
    return __MAP_TYPE(decode(data, use_list=False))


def __decode_set(data):
    return __SET_TYPE(decode(data, use_list=False))


def ext_hook(code, data):
    if code == __MAP_CODE:
        return __decode_map(data)
    elif code == __SET_CODE:
        return __decode_set(data)
    return msgpack.ExtType(code, data)


def encode(value, **kwargs):
    return msgpack.packb(value, default=__default, use_bin_type=True, **kwargs)


def decode(value, **kwargs):
    return msgpack.unpackb(value, ext_hook=ext_hook, raw=False, **kwargs)
