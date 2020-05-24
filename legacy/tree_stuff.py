from collections import defaultdict
from Ops import OpSplit, OpPrimitive
class SplitTreeNode:

    def __init__(self, splitAxis, splitSizes, children):
        self.splitAxis = splitAxis
        self.splitSizes = splitSizes
        self.children = children
        self.parent = None
        self.val = self.splitAxis # TODO: CHANGE ME!
        self.processed = False
        for c in self.children:
            c.parent = self

    def calcOp(self, foundOps):
        opHash = self.splitAxis + ',' + ','.join([str(s) for s in self.splitSizes])
        opArgs = []
        for childNode in self.children:
            childOp, childHash = childNode.calcOp(foundOps)
            opHash += ',(' + childHash + ')'
            opArgs.append(childOp)
        if opHash in foundOps:
            return foundOps[opHash], opHash
        else:
            op = OpSplit(self.splitAxis, self.splitSizes, opArgs)
            foundOps[opHash] = op
            return op, opHash

    def __repr__(self):
        return str(self.val)

class SplitTreeLeaf:

    def __init__(self, primType):
        self.val = primType
        self.parent = None
        self.children = None

    def calcOp(self, foundOps):
        return OpPrimitive(self.val), self.val


    def __repr__(self):
        return str(self.val)


#class Cube(SplitTreeLeaf):
#
#class Slope(SplitTreeLeaf):
#
#class Hip(SplitTreeLeaf):



# given a dict
# where 2d list where each sublist contains pointers to nodes with identical subtrees (but maybe different values)

C1 = SplitTreeLeaf('C')
H1,H2,H3,H4 = [SplitTreeLeaf('H') for i in range(4)]
leaves = [C1,H1,H2,H3,H4]
tree = SplitTreeNode('z',[2,1],[
            C1,
            SplitTreeNode('x',[1,1],[
                SplitTreeNode('y',[1,1],[H1,H2]),
                SplitTreeNode('y',[1,1],[H3,H4])
            ])
        ])

frontier = [leaves]
height = 3
depth = 0


d = {}
op, h = tree.calcOp(d)

