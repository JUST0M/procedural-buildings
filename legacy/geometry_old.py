# ================================
# module: geometry
#
# description:
#     Provides common classes used in geometry
#     May be scrapped when Blender comes into play
#
# ================================


__all__ = [
        'Position',
        'CoordinateSystem',
        'Size',
        'Scope',
        ]

from collections import deque

class XYZ:
    def __init__(self, x, y, z):
        self.x, self.y, self.z = x, y, z

class Position(XYZ):
    ()

class CoordinateSystem(XYZ):
    ()

class Size(XYZ):
    ()

class Scope:
    stack = deque()

    def __init__(self, pos, coordSys, size):
        self.pos = pos
        self.coordSys = coordSys
        self.size = size

    def __str__(self):
        return(
            f"Position:\t\t(x: {self.pos.x}, y: {self.pos.y}, z: {self.pos.z})\n"
            f"Coordinate System:\t(x: {self.coordSys.x}, y: {self.coordSys.y}, z: {self.coordSys.z})\n"
            f"Size:\t\t\t(x: {self.size.x}, y: {self.size.y}, z: {self.size.z})"
        )

    def push(self):
        self.stack.append((self.pos, self.coordSys, self.size))

    def pop(self):
        self.pos, self.coordSys, self.size = self.stack.pop()

    # Other funcs to probs add:
    """
    translate
    rotate
    extrude/resize

    probs need these functions to be able to mutate current Scope as well as return new scope
    """