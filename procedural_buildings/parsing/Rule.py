# Rule class used by the grammar parser to represent a rule
class Rule:
    def __init__(self, left, right):
        self.label = left.label
        self.op = right.op
        self.priority = right.priority
        self.condition = left.condition
        if left.paramNames != None:
            self.op.addParams(left.paramNames)

# Right side of a rule
class Right:
    def __init__(self, op, priority=None):
        self.op = op
        self.priority = priority

# Left side of a rule
class Left:
    def __init__(self, label, paramNames=None, condition=True):
        self.label = label
        self.paramNames = paramNames
        self.condition = condition


# A size class used to represent absolute and relative sizes in a grammar/op graph
class Size:
    # A size has some value and is either a relative or absolute size
    def __init__(self, size, isRelative):
        self.size = size
        self.isRelative = isRelative

    def valToString(self):
        if type(self.size) == int:
            return str(self.size)
        else:
            try:
                return "%.5f" % self.size
            except:
                return str(self.size)

    def __str__(self):
        if self.isRelative:
            return f"~({self.valToString()})"
        else:
            return f"{self.valToString()}"
    def __repr__(self):
        if self.isRelative:
            return f"RelSize({self.size})"
        else:
            return f"Size({self.size})"

    def __hash__(self):
        return hash((self.size, self.isRelative))

