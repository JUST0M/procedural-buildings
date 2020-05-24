from random import uniform

class RuleJob:
    def __init__(self, ruleLabel, obj):
        self.ruleLabel = ruleLabel
        self.obj = obj

class Op():
    def __init__(self):
        pass

    def run(self, context, obj):
        raise NotImplementedError

# Push the current context onto a memory stack
class OpPushObj(Op):
    def __init__(self):
        pass

    def run(self, context, obj):
        context.pushObj(obj)
        return []

# Modify this context to become the one at the top of the stack
class OpPopObj(Op):
    def __init__(self):
        pass

    def run(self, context):
        context.popObj()
        return []

# Split context in half in x-direction
class OpSplit(Op):
    # For now just split in half and apply left and right to the new scopes
    def __init__(self, left, right):
        self.leftRule = left
        self.rightRule = right

    def run(self, context, obj):
        (leftObj, rightObj) = context.split(obj)
        return [RuleJob(self.leftRule, leftObj), RuleJob(self.rightRule, rightObj)]

# Colour current context
class OpColour(Op):
    def __init__(self, colour):
        self.colour = colour

    def run(self, context, obj):
        context.colour(obj, self.colour)
        return []

# Given a list of rules, choose one at random according to their priorirties
class OpChooseRuleWithPriority(Op):
    def __init__(self, rules):
        self.rules = rules

    def run(self, context, obj):
        # Pick a random number less than the max cumulative priority
        rand = uniform(0, self.rules[-1].cumulativePriority)
        i = 0
        while self.rules[i].cumulativePriority < rand:
            i += 1

        return self.rules[i].run(context, obj)




