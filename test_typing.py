import math
import typing

# https://docs.python.org/3/library/typing.html
# https://mypy.readthedocs.io/en/stable/index.html

def floor(x: float, d: int) -> int:
    base = 10 ** d
    return math.floor(x / base) * base

floor(123.0, 2)