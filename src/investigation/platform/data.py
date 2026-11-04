"""Load packaged fictional platform fixtures; no external banking access."""
import json
from importlib.resources import files


def load_data(name: str):
    return json.loads(files("investigation").joinpath("data", name).read_text())
