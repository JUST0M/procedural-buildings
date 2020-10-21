from random import randint, random
from .parsing.Rule import Size
from .Ops import OpSplit, OpPrimitive, OpNil
from math import ceil

# Generate a random operation graph with the given parameters
def genRandOpGraph(maxDepth, maxBranch, numPrims):
    if numPrims > maxBranch**maxDepth:
        return RuntimeError("Can't fit this many prims in tree with these params")
    return randSplit(0, maxDepth, maxBranch, numPrims)

# Create a random split operation with the given parameters
def randSplit(depth, maxDepth, maxBranch, numPrims):
    if numPrims == 0:
        return OpNil()
    if depth == maxDepth:
        return OpPrimitive('rect')
    if numPrims == 1:
        if random() < 0.5:
            return OpPrimitive('rect')
    dDiff = maxDepth - depth
    minBranch = ceil(numPrims / (maxBranch**(dDiff-1)))
    numChildren = randint(minBranch, maxBranch)

    childPrims = calcPrimsInChildren(numChildren, maxBranch**(dDiff-1), numPrims, numChildren)

    sizes =tuple(Size(randint(20,100), True) for i in range(numChildren))
    childOps = [randSplit(depth+1, maxDepth, maxBranch, n) for n in childPrims]
    return OpSplit(randint(0,2), perChildArgs=sizes, childOps=childOps)

# The following function splits some number of operations 'randomly' between a set of operations
# The problem is essentially:
    # Given N children and M primitives,
    # Assign some number of primitives to each child such that the total number of
    # assigned primitives is M and each child has no more than P primitives assigned.
# To generate a truly random assignment is complicated
# see https://stackoverflow.com/questions/8064629/random-numbers-that-add-to-100-matlab/8068956#8068956
# for a discussion.
# So we use a non-uniform verison that just generates the number of primitives assigned to each child on
# the fly.

def calcPrimsInChildren(numChildren, maxPerChild, numPrims, totChildren):
    if numChildren == 1:
        return [numPrims]
    myMin = max(numPrims - maxPerChild*(numChildren-1),0)
    myMax = min(numPrims, maxPerChild)
    inThisChild = randint(myMin, myMax)
    return [inThisChild, *calcPrimsInChildren(numChildren-1, maxPerChild, numPrims-inThisChild, totChildren)]


