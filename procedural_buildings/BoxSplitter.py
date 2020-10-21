from .parsing.Rule import Size
from .Ops import OpSplit, OpNil, OpPrimitive
from itertools import cycle
import numpy as np

# Represents a bounding box for a primitive object
class Box:
    def __init__(self, bounds, prim):
        self.boundVals = [[low, high] for low, high in bounds]
        # Convert values to Bound objects
        self.bounds = tuple((Bound(low, True, self), Bound(high, False, self)) for (low, high) in self.boundVals)
        self.prim = OpPrimitive(prim)
        # container points to the smallest Container containing this Box
        self.container = None

    def matToUnitSquare(self):
        sx, sy, sz = [b-a for a,b in self.boundVals]
        return np.array([[1/sx, 0, 0, -self.boundVals[0][0]/sx - 0.5],
                         [0, 1/sy, 0, -self.boundVals[1][0]/sy - 0.5],
                         [0, 0, 1/sz, -self.boundVals[2][0]/sz - 0.5],
                         [0, 0, 0, 1]])

# Represents a bound for a box
class Bound:
    # Record whether or not this is a low or high bound
    # Also store a pointer back to the box this is a bound for
    def __init__(self, val, low, box):
        self.val = val
        self.low = low
        self.box = box

    def __str__(self):
        return str(self.val)

    def __repr__(self):
        return str(self)


# Represents a container for boxes
class Container:
    # Initially only set an axis
    # The bounds of the container must be set later by setBounds
    def __init__(self, axis):
        self.axis = axis
        self.children = []
        self.unmatched = 0
        self.prevAxis = (axis - 1) % 3
        self.nextAxis = (axis + 1) % 3
        self.numPrims = 0
        self.child = None
        self.isPrim = False
        self.bounds = None

    # Reset the current child so it effectively empty
    def resetChild(self):
        self.child = Container(self.nextAxis)
        # copy
        childBounds = [b[:] for b in self.bounds]
        axis = self.axis
        # swap min and max on prev axis so we know they will be updated first time
        # we expandToFit
        childBounds[axis][0] = self.bounds[axis][1]
        childBounds[axis][1] = self.bounds[axis][0]
        self.child.setBounds(childBounds)

    # Set the bounds of this container
    def setBounds(self, bounds):
        self.bounds = bounds

    # Increment the number of unmatched boxes we've added to the current child
    def incUnmatched(self):
        self.unmatched += 1

    # Add box to the current child
    # If that child can now be split off and a new child started then do so
    def addToChild(self, box):
        self.unmatched -= 1
        if self.child == None:
            self.resetChild()
        # Increase the size of child to also fit box
        self.child.expandToFit(box)
        # self.child is now the smallest container containing box
        box.container = self.child
        # If we no longer have unmatched boxes then we can split
        # and start a new child
        improvedContainer = False
        if self.unmatched == 0:
            # If self.child exactly fits box then we can just replace
            # with a PrimContainer
            if self.child.numPrims == 1 and self.child.perfectlyContains(box):
                box.container = PrimContainer(box.prim, self.child.bounds)
                self.children.append(box.container)
            else:
                self.children.append(self.child)
            improvedContainer = not (self.child.numPrims == self.numPrims and
                                     self.child.bounds == self.bounds)
            self.resetChild()
        return improvedContainer

    # Expand this container's bounds to include box along prev container axis
    def expandToFit(self, box):
        self.numPrims += 1
        axis = self.prevAxis
        if box.boundVals[axis][0] < self.bounds[axis][0]:
            self.bounds[axis][0] = box.boundVals[axis][0]
        if box.boundVals[axis][1] > self.bounds[axis][1]:
            self.bounds[axis][1] = box.boundVals[axis][1]

    # Like expandToFit but adjust all axes
    def addBox(self, box):
        self.numPrims += 1
        if self.bounds == None:
            self.bounds = [b[:] for b in box.boundVals]
        else:
            for ax in range(3):
                if box.boundVals[ax][0] < self.bounds[ax][0]:
                    self.bounds[ax][0] = box.boundVals[ax][0]
                if box.boundVals[ax][1] > self.bounds[ax][1]:
                    self.bounds[ax][1] = box.boundVals[ax][1]

    # Convert this container into a split operation
    def toOp(self):
        sizes = []
        childOps = []
        # There may be empty space at the beginning of this container that
        # needs to represented with a nil operation
        prev = self.bounds[self.axis][0]
        for i in range(len(self.children)):
            child = self.children[i]

            # Check if there is empty space between this and the previous child
            # If so, fill it with a nil operation
            nilSize = child.bounds[self.axis][0] - prev
            if nilSize > 0:
                childOps.append(OpNil())
                sizes.append(Size(nilSize, True))

            # Convert this child to an operation
            childOps.append(child.toOp())
            childSize = child.bounds[self.axis][1] - child.bounds[self.axis][0]
            sizes.append(Size(childSize, True))
            prev = child.bounds[self.axis][1]

        # We also need to check for empty space after the last child
        nilSize = self.bounds[self.axis][1] - prev
        if nilSize > 0:
            childOps.append(OpNil())
            sizes.append(Size(nilSize, True))

        # If there is only one child just return that instead
        if len(childOps) == 1:
            return childOps[0]
        else:
            return OpSplit(self.axis,
                           perChildArgs=tuple(sizes),
                           childOps=childOps)

    # Check if this container exactly contains box
    def perfectlyContains(self, box):
        return self.bounds == box.boundVals

# A contianer that perfectly contains a primitive operation
class PrimContainer:
    def __init__(self, prim, bounds):
        self.prim = prim
        self.isPrim = True
        self.bounds = bounds

    # Convert this container into an operation
    # We can simply return the primitive operation that this container
    # perfectly contains
    def toOp(self):
        return self.prim

# Given a set of primitive-containing boxes and an initial container
# that exactly bounds all the boxes, return a split operation that
# places all the primitive boxes in their correct location when run
# on a scope equal to the initial container
def boxesToOp(boxes, initialContainer):
    initialContainer.numPrims = len(boxes)
    for box in boxes:
        box.container = initialContainer

    bounds = [sorted(
               (bound for b in boxes for bound in (b.bounds[ax][0], b.bounds[ax][1])),
               key=lambda b: (b.val, b.low)
              ) for ax in (0,1,2)]

    axis = cycle((0,1,2))
    allPrimitiveContainers = False
    consecutiveFailCount = 0

    # We have finished when all boxes' containers are primitive containers
    while not allPrimitiveContainers and consecutiveFailCount < 6:
        allPrimitiveContainers = True
        ax = next(axis)
        didAnySplit = False
        for bound in bounds[ax]:
            box = bound.box
            container = box.container
            if not container.isPrim:
                allPrimitiveContainers = False
                if bound.low:
                    # Increment the unmatched counter for this box's container
                    container.incUnmatched()
                else:
                    # Add this box to its containers current child
                    # This will also update the box's container pointer
                    # and do a split if the container's unmatched counter is zero
                    improvedContainer = container.addToChild(box)
                    if improvedContainer:
                        didAnySplit = True
        if didAnySplit:
            consecutiveFailCount = 0
        else:
            consecutiveFailCount += 1

    if consecutiveFailCount == 6 and not allPrimitiveContainers:
        print([b.bounds for b in boxes])
        print([b.container for b in boxes])
        print([b.container.bounds for b in boxes])
        raise RuntimeError("Failed to split boxes")



    return initialContainer.toOp()


#boxes = [Box(x, f"prim{i}") for i, x in enumerate([[[0.0, 100.0], [0.0, 25.874126], [51.111111, 100.0]], [[0.0, 27.058824], [70.27972, 100.0], [0.0, 100.0]]])]

#initialContainer = Container(0)
#for box in boxes:
#    initialContainer.addBox(box)
#initialContainer.setBounds([[0,23],[0,6],[0,12]])

#print(boxesToOp(boxes, initialContainer))






