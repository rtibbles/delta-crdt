import msgpack
from .base import Map
from .base import Set
from .dot_map import DotMap
from .causal_context import CausalContext

__MAP_CODE = 64
__SET_CODE = 65
__DOTMAP_CODE = 66
__CC_CODE = 67

__MAP_TYPE = Map
__SET_TYPE = Set
__DOTMAP_TYPE = DotMap
__CC_TYPE = CausalContext


def __encode_map(obj):
    return msgpack.ExtType(__MAP_CODE, encode(list(obj.items())))


def __encode_set(obj):
    return msgpack.ExtType(__SET_CODE, encode(list(obj)))


def __encode_dotmap(obj):
    dotmap_dict = {"cc": obj.cc, "state": dict(obj.items())}
    return msgpack.ExtType(__DOTMAP_CODE, encode(dotmap_dict))


def __encode_cc(obj):
    cc_dict = {"cc": obj.cc, "dc": obj.dc}
    return msgpack.ExtType(__CC_CODE, encode(cc_dict))


def __default(obj):
    if isinstance(obj, __MAP_TYPE):
        return __encode_map(obj)
    if isinstance(obj, __SET_TYPE):
        return __encode_set(obj)
    if isinstance(obj, __DOTMAP_TYPE):
        return __encode_dotmap(obj)
    if isinstance(obj, __CC_TYPE):
        return __encode_cc(obj)
    raise TypeError("Unknown type: %r" % (obj,))


def __decode_map(data):
    return __MAP_TYPE(decode(data, use_list=False))


def __decode_set(data):
    return __SET_TYPE(decode(data, use_list=False))


def __decode_dotmap(data):
    return __DOTMAP_TYPE(**decode(data, use_list=False))


def __decode_cc(data):
    return __CC_TYPE(**decode(data, use_list=False))


def ext_hook(code, data):
    if code == __MAP_CODE:
        return __decode_map(data)
    elif code == __SET_CODE:
        return __decode_set(data)
    elif code == __DOTMAP_CODE:
        return __decode_dotmap(data)
    elif code == __CC_CODE:
        return __decode_cc(data)
    return msgpack.ExtType(code, data)


def encode(value, **kwargs):
    return msgpack.packb(value, default=__default, use_bin_type=True, **kwargs)


def decode(value, **kwargs):
    return msgpack.unpackb(value, ext_hook=ext_hook, raw=False, **kwargs)
