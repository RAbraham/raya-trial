
from abc import ABC, abstractmethod

class Actor(ABC):
    def no_op(self):
        # Do Nothing. Used to ensure that the actor is ready before leaving the submit job
        pass