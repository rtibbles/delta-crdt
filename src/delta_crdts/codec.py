import msgpack
from .base import Map
from .base import Set
from .dot_map import DotMap
from .dot_set import DotSet


registered_types = (
    Map,
    Set,
    DotMap,
    DotSet,
)


def __default(obj):
    for registered_type in registered_types:
        if isinstance(obj, registered_type):
            return msgpack.ExtType(registered_type.msgpack_code, encode(obj.to_init()))
    raise TypeError("Unknown type: %r" % (obj,))


def ext_hook(code, data):
    for registered_type in registered_types:
        if code == registered_type.msgpack_code:
            return registered_type.factory(decode(data))
    return msgpack.ExtType(code, data)


def encode(value, **kwargs):
    return msgpack.packb(value, default=__default, use_bin_type=True, **kwargs)


def decode(value, **kwargs):
    return msgpack.unpackb(
        value, ext_hook=ext_hook, raw=False, use_list=False, **kwargs
    )
