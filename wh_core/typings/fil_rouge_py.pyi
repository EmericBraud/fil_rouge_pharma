"""
Fil Rouge - Warehouse optimizer
"""
from __future__ import annotations
__all__: list[str] = ['Coord', 'Rack', 'Slot', 'f']
class Coord:
    x: int
    y: int
    def __init__(self) -> None:
        ...
class Rack:
    def __init__(self) -> None:
        ...
class Slot:
    xy: Coord
    def __init__(self) -> None:
        ...
def f(x: int) -> int:
    """
    Test
    """
