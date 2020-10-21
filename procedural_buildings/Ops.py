from random import random
from .parsing.Rule import Size
from sympy import boolalg, numbers
from sympy.core.expr import Expr
from sympy.core.relational import Relational
from collections import defaultdict
from .RandRange import RandRange


class Args:

    def __init__(self, args, perChildArgs):
        self.args = args
        self.perChildArgs = perChildArgs
        if len(perChildArgs) > 0:
            self.allArgs = (*self.args, self.perChildArgs)
        else:
            self.allArgs = self.args

    # evaluate arg values
    def evaluate(self, env):
        evaledArgs = tuple(self.evalArg(arg, env) for arg in self.allArgs)
        return evaledArgs

    def evaluateSeparate(self, env):
        evaledArgs = tuple(self.evalArg(arg, env) for arg in self.args)
        evaledChildArgs = tuple(self.evalArg(arg, env) for arg in self.perChildArgs)
        return evaledArgs, evaledChildArgs

    def evalArg(self, arg, env):
        t = type(arg)
        if t == tuple:
            return tuple(self.evalArg(a, env) for a in arg)
        elif t == Size:
            return Size(self.evalArg(arg.size, env), arg.isRelative)
        elif t == int or t == str or t == float:
            return arg
        elif issubclass(t, RandRange):
            return arg.evaluate()
        elif issubclass(t, Expr) or issubclass(t,Relational):
            evaled = arg.subs(env)
            if len(evaled.free_symbols) > 0:
                return str(evaled)
            elif issubclass(type(evaled), boolalg.BooleanAtom):
                return bool(evaled)
            elif issubclass(type(evaled), numbers.Integer):
                return int(evaled)
            else:
                return float(evaled)
        else:
             return arg

    def combineWith(self, other):
        newArgs = self.combineArgs(self.args, other.args)
        if newArgs == None:
            return None
        newPerChildArgs = self.combineArgs(self.perChildArgs, other.perChildArgs)
        if newPerChildArgs == None:
            return None
        else:
            return Args(newArgs, perChildArgs=newPerChildArgs)

    def combineArgs(self, arg1, arg2):
        if arg1 == arg2:
            return arg1
        t1 = type(arg1); t2 = type(arg2)
        if t1 == list or t1 == tuple:
            if t2 == t1 and len(arg1) == len(arg2):
                newListArg = []
                for a1, a2 in zip(arg1, arg2):
                    newArg = self.combineArgs(a1, a2)
                    if newArg == None:
                        return None
                    else:
                        newListArg.append(newArg)
                return newListArg if t1 == list else tuple(newListArg)
            else:
                return None
        elif t2 == list:
            return None

        elif t1 == Size:
            if t2 == Size and arg1.isRelative == arg2.isRelative:
                newSizeVal = self.combineArgs(arg1.size, arg2.size)
                return Size(newSizeVal, arg1.isRelative)
            else:
                return None
        elif t2 == Size:
            return None
        elif t1 == str:
            if t2 == str and arg1 == arg2:
                return arg1
            else:
                return None
        elif t2 == str:
            return None
        else:
            if not issubclass(t1, RandRange):
                arg1 = RandRange(arg1, arg1)
            if not issubclass(t2, RandRange):
                arg2 = RandRange(arg2, arg2)
            return arg1.union(arg2)

    def __getitem__(self, key):
        return self.allArgs[key]

    def __str__(self):
        return self.allArgs.__str__()

    def formatForGrammar(self):
        if len(self.args) == 0:
            return ""
        else:
            return f"({', '.join(map(str, self.args))})"


class Op:

    def __init__(self, *args, **kwargs):
        perChildArgs = kwargs.get('perChildArgs', ())
        self.args = Args(args, perChildArgs)
        self.childOps = kwargs.get('childOps', None)
        self.ruleLabel = None

    def addParams(self, paramNames):
        self.paramNames = paramNames

    def __repr__(self):
        return f"{self.__class__.__name__}@{hex(id(self))}"

    def __str__(self):
        return(self.toString(0))

    def toString(self, indent):
        spaces = "  " * indent
        s = f"{spaces}{self.__class__.__name__}{self.args.allArgs}"

        if self.childOps and len(self.childOps) > 0:
            s += "\n"
            if indent > 50:
                s += "...\n"
            newIndent = indent + 1
            s += "\n".join([c.toString(newIndent) if type(c) != str else c for c in self.childOps])
        return s

    def toStringWithIDs(self):
        return self._toStringWithIDs(0)

    def _toStringWithIDs(self, indent):
        spaces = "  " * indent
        s = f"{spaces}{self.__class__.__name__}{self.args.allArgs}({hex(id(self))})"
        if self.childOps and len(self.childOps) > 0:
            s += "\n"
            newIndent = indent + 1
            s += "\n".join([c._toStringWithIDs(newIndent) if type(c) != str else c for c in self.childOps])
        return s

    def run(self, context, scope, env):
        raise NotImplementedError

    def simplify(self, seenOps, combArgs=False):
        # Two ops that can definitely be merged should have the same hash

        ident = self.argsToHash() if combArgs else [self.__class__.__name__, *self.args.allArgs]
        if self.childOps:
            for i in range(len(self.childOps)):
                child = self.childOps[i].simplify(seenOps, combArgs)
                self.childOps[i] = child
                ident.append(child.hash)
        myHash = hash(tuple(ident))

        if myHash in seenOps:
            comboOp = seenOps[myHash]
            if combArgs:
                comboOp.augmentArgs(self)
            return comboOp
        else:
            seenOps[myHash] = self
            self.hash = myHash
            return self

    def combineWith(self, other):
        return OpChooseRuleWithPriority(perChildArgs=((0.5,0.5), (True, True)), childOps=[self,other]).simplify({})

    def augmentArgs(self, other):
        comboArgs = self.args.combineWith(other.args)
        if comboArgs == None:
            raise RuntimeError(f"Failed to combine op:\n{self}\nwith op:\n{other}")
        else:
            self.args = comboArgs

    def argsToHash(self):
        return [self.__class__.__name__]

    # Return a fully-deterministic op that could be generated by this op
    def exampleTree(self, env):
        cs = [c.exampleTree(env) for c in self.childOps] if self.childOps else None
        newArgs, newPerChildArgs = self.args.evaluateSeparate(env)
        return type(self)(*newArgs, perChildArgs=newPerChildArgs, childOps=cs)

    # Return n fully-deterministic ops that could be generated by this op
    def examples(self, n):
        return [self.exampleTree({}) for i in range(n)]

    # First generate n fully-deterministic ops that could be generated by this op
    # Then combine these examples to try and calculate the original op (self)
    def regenOpFromExamples(self, n):
        if n <= 0:
            return None
        examples = self.examples(n)
        return self.combineMany(examples)

    @staticmethod
    def combineMany(ops):
        n = len(ops)
        return OpChooseRuleWithPriority(perChildArgs=((1/n,)*n, (True,)*n), childOps=ops).simplify({},True)

    def toGrammarText(self):
        MAX_RULES = 10000
        ruleNum = iter(range(MAX_RULES))
        ruleLabel, grammarText = self._toGrammarText(ruleNum)
        return grammarText

    def _toGrammarText(self, ruleNum):
        # If we have already seen this operation and included it in the grammar
        # then just return the rule name and an empty string
        # since we don't want the rule to appear in the grammar more than once
        if self.ruleLabel:
            return self.ruleLabel, ""
        label = "rule" + str(next(ruleNum))
        self.ruleLabel = label
        # If this op has no children then we just return a one line rule
        # We add child args to this if needed
        ruleText = f"{label} --> {self.opName}{self.args.formatForGrammar()}"
        childText = ""
        if self.childOps != None:
            childArgs = []
            if len(self.args.perChildArgs) == 0:
                for c in self.childOps:
                    childLabel, cText = c._toGrammarText(ruleNum)
                    childArgs.append(childLabel)
                    childText += cText
            else:
                for arg, c in zip(self.args.perChildArgs, self.childOps):
                    childLabel, cText = c._toGrammarText(ruleNum)
                    childArgs.append(f"{arg} : {childLabel}")
                    childText += cText
            ruleText += "{" + " | ".join(childArgs) + "}"

        return label, ruleText + "\n" + childText


# Split context in given direction into given size sections
class OpSplit(Op):

    opName = 'split'

    def run(self, context, scope, env):
        axis, sizes = self.args.evaluate(env)
        childScopes = scope.split(axis, sizes)
        for childOp, childScope in zip(self.childOps, childScopes):
            childOp.run(context, childScope, env)

    def simplify(self, seenOps, combArgs=False):
        newMe = Op.simplify(self, seenOps, combArgs)
        sizes = newMe.args[1]
        newChildOps = []
        newSizes = []
        i = 0
        for child in newMe.childOps:
            if type(child) == OpSplit and child.args[0] == newMe.args[0]:
                # Can flatten this child
                newChildOps.extend(child.childOps)
                sumChildSizes = sum([s.size for s in child.args[1] if s.isRelative])
                mult = sizes[i]
                newSizes.extend([Size(s.size*mult/sumChildSizes, True) if s.isRelative else s for s in child.sizes])
            else:
                newChildOps.append(child)
                newSizes.append(sizes[i])
            i += 1
        newNewMe = OpSplit(self.args[0], perChildArgs=tuple(newSizes), childOps=newChildOps)
        return Op.simplify(newNewMe, seenOps, combArgs)

    # Also include the axis and number of children in the hash
    # because we can't combine operators with these values differing
    def argsToHash(self):
        return [self.__class__.__name__, self.args[0], len(self.args[1])]

# Split the scope into uniform scopes and repeat an operation on each new scope
class OpRepeat(Op):

    opName = 'repeat'

    def run(self, context, scope, env):
        axis, size = self.args.evaluate(env)
        # There is really just one child op
        childOp = self.childOps[0]
        childScopes = scope.repeat(axis, size)

        for childScope in childScopes:
            childOp.run(context, childScope, env)

    # Also include the axis in the hash
    # because we can't combine operators with this value differing
    def argsToHash(self):
        return [self.__class__.__name__, self.args[0]]

# Split the scope into uniform scopes and repeat an operation on each new scope
class OpRepeatN(Op):

    opName = 'repeatN'

    def run(self, context, scope, env):
        axis, n = self.args.evaluate(env)
        # There is really just one child op
        childOp = self.childOps[0]
        childScopes = scope.repeatN(axis, n)

        for childScope in childScopes:
            childOp.run(context, childScope, env)

    # Also include the axis in the hash
    # because we can't combine operators with this value differing
    def argsToHash(self):
        return [self.__class__.__name__, self.args[0]]

# Split the scope into components (e.g. faces) and apply rules to each
class OpComp(Op):

    opName = 'comp'

    def run(self, context, scope, env):
        faces = self.args[0]
        childScopes = [scope.comp(face) for face in faces]
        for childOp, childScope in zip(self.childOps, childScopes):
            childOp.run(context, childScope, env)

# Colour current context
class OpColour(Op):

    opName = 'colour'

    def run(self, context, scope, env):
        col = self.args.evaluate(env)
        context.colour(col, scope)

# Given a list of rules, choose one at random according to their priorirties
class OpChooseRuleWithPriority(Op):

    def chooseChild(self, env):
        priorities, conditions = self.args.evaluate(env)[0]
        # remove children whose conditions fail
        # remember the index of the valid children in the original list though
        filteredPriorities = [(i,p) for i,p in enumerate(priorities) if conditions[i]]
        # Pick a random number less than the max cumulative priority
        rand = random() * sum(x[1] for x in filteredPriorities)
        i = 0
        cumulativePriority = filteredPriorities[0][1]
        while cumulativePriority < rand:
            i += 1
            cumulativePriority += filteredPriorities[i][1]
        return self.childOps[filteredPriorities[i][0]]

    def run(self, context, scope, env):
        # Choose a child based on priorities and conditions and run that child
        self.chooseChild(env).run(context, scope, env)

    def exampleTree(self, env):
        return self.chooseChild(env).exampleTree(env)

    def simplify(self, seenOps, combArgs=False):
        priorities, conditions = self.args[0]
        seenChildren = defaultdict(float)
        for i in range(len(self.childOps)):
            child = self.childOps[i].simplify(seenOps, combArgs)
            # flatten child choices
            if type(child) == OpChooseRuleWithPriority:
                for j in range(len(child.childOps)):
                    c = child.childOps[j]
                    seenChildren[c.hash] += child.args[0][i] * priorities[i]
            else:
                seenChildren[child.hash] += priorities[i]

        newChildOps = []
        priorities = []
        # TODO: Need to sort out conditions too
        childHashes = seenChildren.keys()
        for opHash, priority in seenChildren.items():
            newChildOps.append(seenOps[opHash])
            priorities.append(priority)
        # If we only have one child then we are always going to choose it
        # so just return that operation and get rid of this choose op
        if (len(newChildOps) == 1):
            return newChildOps[0]
        priorities = tuple(priorities)
        newOp = OpChooseRuleWithPriority(perChildArgs=(priorities, (True,)*len(priorities)), childOps=newChildOps)
        if combArgs:
            ident = ('OpChooseRuleWithPriority', *childHashes)
        else:
            ident = ('OpChooseRuleWithPriority', priorities, *childHashes)
        myHash = hash(ident)

        if myHash in seenOps:
            comboOp = seenOps[myHash]
            if combArgs:
                comboOp.augmentArgs(newOp)
            comboOp.hash = myHash
            return comboOp
        else:
            seenOps[myHash] = newOp
            newOp.hash = myHash
            return newOp

    def _toGrammarText(self, ruleNum):
        if self.ruleLabel:
            return self.ruleLabel, ""
        label = "rule" + str(next(ruleNum))
        self.ruleLabel = label
        childText = ""
        text = ""
        for c, p in zip(self.childOps, self.args[0][0]):
            childLabel, cText = c._toGrammarText(ruleNum)
            text += f"{label} --> {childLabel} : %.5f\n" % p
            childText += cText
        return label, text + childText

# Set the size of the current scope
class OpResizeScope(Op):

    opName = 'S'

    def run(self, context, scope, env):
        v = self.args.evaluate(env)
        self.childOps[0].run(context, scope.resize(v), env)

# Translate the current object
class OpTranslate(Op):

    opName = 'T'

    def run(self, context, scope, env):
        v = self.args.evaluate(env)
        self.childOps[0].run(context, scope.translate(v), env)


# Rotate the current object
class OpRotate(Op):

    opName = 'R'

    def run(self, context, scope, env):
        axis, angle = self.args.evaluate(env)
        self.childOps[0].run(context, scope.rotate(axis, angle), env)

# Put a primitive in the current scope
class OpPrimitive(Op):

    opName = 'I'

    def run(self, context, scope, env):
        prim = self.args[0]
        context.addPrim(prim, scope)

    def argsToHash(self):
        return [self.__class__.__name__, self.args[0]]

    def _toGrammarText(self, ruleNum):
        return f"I({self.args[0]})", ""

# Very simple parent op that just runs its child
class OpDo(Op):

    def run(self, context, scope, env):
        self.childOps[0].run(context, scope, env)

    def _toGrammarText(self, ruleNum):
        return self.childOps[0]._toGrammarText(ruleNum)

# Nil op does nothing
class OpNil(Op):

    opName = 'nil'

    # Run on a scope, just leave that scope blank and do nothing
    def run(self, context, scope, env):
        pass

    def _toGrammarText(self, ruleNum):
        return "nil", ""

# Sets the values of parameters in the environment
class OpSetParams(Op):

    def exampleTree(self, env):
        paramVals = self.args.evaluate(env)
        child = self.childOps[0]
        envNew = env.copy()
        envNew.update(zip(child.paramNames, paramVals))
        return OpSetParams(paramVals, childOps=[child.exampleTree(envNew)])

    def run(self, context, scope, env):
        # Evaluate the param values in the current environment
        paramVals = self.args.evaluate(env)
        # The child operation is the operation that uses the params
        # set by this operation
        child = self.childOps[0]
        # Update the environment with the param values
        envNew = env.copy()
        envNew.update(zip(child.paramNames, paramVals))
        child.run(context, scope, envNew)

