from pathlib import Path
import tensorflow as tf
import raya

class TF1Actor(raya.Actor):
    def __init__(self, folder):
        weights = Path(folder) / "weights.txt"
        print(weights.read_text())
        print("================= In TF1 init ====================================")

    def act(self, name):
        print("================= In TF1 act ====================================")
        return f"TF:{tf.__version__}: {name}"

