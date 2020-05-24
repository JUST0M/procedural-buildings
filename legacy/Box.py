import numpy as np

class Box:
    def __init__(self, minCoords, maxCoords):
        self.min = minCoords
        self.max = maxCoords
        self.planes = [*((i,self.min[i]) for i in range(3)),
                       *((i,self.max[i]) for i in range(3))]
        self.size = [c2 - c1 for c1,c2 in zip(self.min, self.max)]

    def volume(self):
        diffX = self.max[0] - self.min[0]
        diffY = self.max[1] - self.min[1]
        diffZ = self.max[2] - self.min[2]
        return diffX * diffY * diffZ

    # Return a new scope such that the new scope comes
    # before other but within self in the given direction.
    # Dimensions other than the provided axis will remain the same
    # as self's dimensions
    def before(self, other, axis):
        if self.min[axis] == other.min[axis]:
            return None
        elif axis == 0:
            return Box(self.min, (other.min[0], self.max[1], self.max[2]))
        elif axis == 1:
            return Box(self.min, (self.max[0], other.min[1], self.max[2]))
        elif axis == 2:
            return Box(self.min, (self.max[0], self.max[1], other.min[2]))

    # Like before but after
    def after(self, other, axis):
        if self.max[axis] == other.max[axis]:
            return None
        elif axis == 0:
            return Box((other.max[0], self.min[1], self.min[2]), self.max)
        elif axis == 1:
            return Box((self.min[0], other.max[1], self.min[2]), self.max)
        elif axis == 2:
            return Box((self.min[0], self.min[1], other.max[2]), self.max)

    def takeSizeFrom(self, other, axis):
        if axis == 0:
            return Box((other.min[0], self.min[1], self.min[2]),
                         (other.max[0], self.max[1], self.max[2]))
        elif axis == 1:
            return Box((self.min[0], other.min[1], self.min[2]),
                         (self.max[0], other.max[1], self.max[2]))
        elif axis == 2:
            return Box((self.min[0], self.min[1], other.min[2]),
                         (self.max[0], self.max[1], other.max[2]))

    def contains(self, other):
        for ax in (0,1,2):
            if self.min[ax] > other.min[ax] or self.max[ax] < other.max[ax]:
                return False
        return True

    def matToUnitSquare(self):
        sx = self.max[0] - self.min[0]
        sy = self.max[1] - self.min[1]
        sz = self.max[2] - self.min[2]
        return np.array([[1/sx, 0, 0, -self.min[0]/sx - 0.5],
                         [0, 1/sy, 0, -self.min[1]/sy - 0.5],
                         [0, 0, 1/sz, -self.min[2]/sz - 0.5],
                         [0, 0, 0, 1]])

    def boundWith(self, other):
        newMin = tuple(min(pair) for pair in zip(self.min, other.min))
        newMax = tuple(max(pair) for pair in zip(self.max, other.max))
        return Box(newMin, newMax)

    def cutWith(self, plane):
        planeAxis, planeCoord = plane
        beforeMin = self.min
        beforeMax = tuple(planeCoord if i==planeAxis else self.max[i] for i in range(3))
        afterMin = tuple(planeCoord if i==planeAxis else self.min[i] for i in range(3))
        afterMax = self.max
        return Box(beforeMin, beforeMax), Box(afterMin, afterMax)

    def relationTo(self, plane):
        planeAxis, planeCoord = plane
        if self.min[planeAxis] < planeCoord:
            if self.max[planeAxis] <= planeCoord:
                return 'before'
            else:
                return 'intersect'
        else:
            return 'after'

    def __str__(self):
        return f"min: {self.min}, max: {self.max}"

    def __repr__(self):
        return f"min: {self.min}, max: {self.max}"

