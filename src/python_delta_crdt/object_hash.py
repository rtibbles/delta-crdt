import json


def get_object_key(obj):
    try:
        return hash(obj)
    except TypeError:
        try:
            return hash(json.dumps(obj, sort_keys=True))
        except TypeError:
            raise TypeError("Unhashable type")
