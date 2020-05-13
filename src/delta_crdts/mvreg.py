from .base import CausalCRDT
from .base import Set
from .base import mutator
from .dot_set import DotSet
from .codec import encode


class MVReg(CausalCRDT):
    @classmethod
    def initial(cls):
        return DotSet()

    @classmethod
    def join(cls, s1, s2):
        return DotSet.join(s1, s2)

    @classmethod
    def value(cls, state):
        return Set(state.values())

    @mutator
    def write(self, value):
        encoded_id = encode(self.id).encode("base64")
        return DotSet.join(self.state.remove_all(), self.state.add(encoded_id, value))
