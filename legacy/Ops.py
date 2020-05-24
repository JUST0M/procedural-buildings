from random import uniform, random
from Rule import Size

class Op():
    childOps = []
    childLabels = []

    def __init__(self):
        pass

    # evaluate arg values
    def evalArgs(self, *args):
        evaledArgs = [self.evalArg(arg) for arg in args]
        return evaledArgs

    def evalArg(self, arg):
        if type(arg) == list:
            return [self.evalArg(a) for a in arg]
        elif type(arg) == Size:
            return Size(self.evalArg(arg.size), arg.isRelative)
        else:
            try:
                return float(arg.subs([('rand',random())]))
            except:
                return arg

    def run(self, context):
        raise NotImplementedError

    def simplifyOpTree(self, seenOps):
        myHash = self.__hash__()
        if hasattr(self, 'childOps'):
            for i in range(len(self.childOps)):
                child, childHash = self.childOps[i].simplifyOpTree(seenOps)
                self.childOps[i] = child
                myHash += childHash

        if myHash in seenOps:
            return seenOps[myHash], myHash

    def __hash__(self):
        raise NotImplementedError

# Push the current context onto a memory stack
class OpPushScope(Op):
    def __init__(self):
        pass

    def run(self, context):
        context.pushScope()

# Modify this context to become the one at the top of the stack
class OpPopScope(Op):
    def __init__(self):
        pass

    def run(self, context):
        context.popScope()

# Split context in given direction into given size sections
class OpSplit(Op):
    def __init__(self, axis, sizes, childOps):
        self.axis = axis
        self.sizes = sizes
        self.childOps = childOps

    def run(self, context):
        childScopes = context.split(*self.evalArgs(self.axis, self.sizes))
        context.pushScope()
        for childOp, childScope in zip(self.childOps, childScopes):
            context.setScope(childScope)
            childOp.run(context)
        context.popScope()

    def toGrammar(self, ruleName):
        grammarLines = []
        return grammarLines

    # Given a list of already seen ops, return a hash of self and new seen ops.
    # self is such that all equivalent sub-ops are represented by the same object
    def simplifyOpTree(self, seenOps):
        myHash = self.__hash__()
        for i in range(len(self.childOps)):
            child, childHash = self.childOps[i].simplifyOpTree(seenOps)
            self.childOps[i] = child
            myHash += childHash

        if myHash in seenOps:
            return seenOps[myHash], myHash

    def __hash__(self):
        return self.axis + ','.join([str(c) for c in self.sizes])


# Split the scope into uniform scopes and repeat an operation on each new scope
class OpRepeat(Op):
    def __init__(self, axis, size, childOps):
        self.axis = axis
        self.size = size
        self.childOps = childOps

    def run(self, context):
        # There is really just one child op
        childOp = self.childOps[0]
        childScopes = context.repeat(*self.evalArgs(self.axis, self.size))

        context.pushScope()
        for childScope in childScopes:
            context.setScope(childScope)
            childOp.run(context)
        context.popScope()

# Split the scope into components (e.g. faces) and apply rules to each
class OpComp(Op):
    def __init__(self, faces, childOps):
        #self.axis = axis
        self.faces = faces
        self.childOps = childOps

    def run(self, context):
        childScopes = context.comp(self.faces)
        context.pushScope()
        for childOp, childScope in zip(self.childOps, childScopes):
            context.setScope(childScope)
            childOp.run(context)
        context.popScope()

# Colour current context
class OpColour(Op):
    nameToColour = {
        'red': [1, 0, 0],
        'green': [0, 1, 0],
        'blue': [0, 0, 1],
    }
    def __init__(self, col):
        if type(col) == str:
            self.colour = self.nameToColour[col]
        else:
            self.colour = col

    def run(self, context):
        context.colour(*self.evalArgs(self.colour))

# Given a list of rules, choose one at random according to their priorirties
class OpChooseRuleWithPriority(Op):
    def __init__(self, rules):
        self.childOps = []
        self.cumulativePriorities = []
        priority = 0
        for r in rules:
            priority += self.evalArg(r.priority)
            self.childOps.append(r.op)
            self.cumulativePriorities.append(priority)

    def run(self, context):
        # Pick a random number less than the max cumulative priority
        rand = uniform(0, self.cumulativePriorities[-1])
        i = 0
        while self.cumulativePriorities[i] < rand:
            i += 1

        self.childOps[i].run(context)

# Scale the current object
class OpScale(Op):
    def __init__(self, scaleVector):
        self.v = scaleVector

    def run(self, context):
        context.scale(*self.evalArgs(self.v))
        #context.scale(self.v)

# Set the size of the current scope
class OpResizeScope(Op):
    def __init__(self, sx, sy, sz):
        self.sx = sx
        self.sy = sy
        self.sz = sz

    def run(self, context):
        context.resizeScope(*self.evalArgs(self.sx, self.sy, self.sz))

# Rotate the current object
class OpRotate(Op):
    def __init__(self, axis, angle):
        self.axis = axis
        self.angle = angle

    def run(self, context):
        context.rotate(*self.evalArgs(self.axis, self.angle))

    def __hash__(self):
        return "R"

# Translate the current object
class OpTranslate(Op):
    def __init__(self, translationVector):
        self.v = translationVector

    def run(self, context):
        context.translate(*self.evalArgs(self.v))

# Complex operation which runs a sequence of ops in order
class OpSeq(Op):
    def __init__(self, childOps):
        self.childOps = childOps

    def run(self, context):
        for op in self.childOps:
            op.run(context)

    def __hash__(self):
        return "seq"

# Put a primitive in the current scope
class OpPrimitive(Op):
    def __init__(self, prim):
        self.prim = prim

    def run(self, context):
        context.primitive(self.prim)

    def __hash__(self):
        return self.prim

# Nil op does nothing
class OpNil(Op):
    def __init__(self):
        pass

    def run(self, context):
        pass

    def __hash__(self, context):
        return "nil"




