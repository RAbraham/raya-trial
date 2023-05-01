import raya
import tensorflow as tf

class TF2Actor(raya.Actor):
    def __init__(self):
        print("================= In TF2 init ====================================")

    def do(self, name):

        print("================= In TF2 act ====================================")
        return f"TF:{tf.__version__}: {name}"

