import raya
from pylru import lrudecorator
import time

class CachingModelActor(raya.Actor):
    def __init__(self):
        print("================= In Caching Model init ====================================")

    @lrudecorator(100)
    def act(self, name):
        time.sleep(5)
        print("================= In Caching Do ====================================")
        return f"Hi {name}"

