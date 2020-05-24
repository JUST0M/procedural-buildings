# ================================
# module: operations
#
# description:
#     Provides definitions for opeartions that can be used in a CGA Shape grammar
#
# ================================


__all__ = [
        'RuleJob',
        'OpSplit',
        'OpPushScope',
        'OpPopScope',
        'OpColour',
        'OpChooseRuleWithPriority',
        ]

from .geometry import *
from random import uniform

class RuleJob:
    def __init__(self, ruleLabel, scope):
        self.ruleLabel = ruleLabel
        self.scope = scope

class Op:
    def __init__(self):
        raise NotImplementedError

    def run(self, model, scope):
        raise NotImplementedError

class OpSplit(Op):

    # For now just split in half and apply left and right to the new scopes
    def __init__(self, left, right):
        self.leftRule = left
        self.rightRule = right

    def run(self, model, scope):
        # Create a new scope for each part of the split
        # For now just split in half
        s = scope
        leftScope = Scope(s.pos, s.coordSys, Size(s.size.x / 2, s.size.y, s.size.z))

        rightScope = Scope(Position(s.pos.x + s.size.x / 2, s.pos.y, s.pos.z), s.coordSys, Size(s.size.x / 2, s.size.y, s.size.z))

        # Return the param/scope pairs as rules that need running

        return [RuleJob(self.leftRule, leftScope), RuleJob(self.rightRule, rightScope)]

class OpPushScope(Op):
    def __init__(self):
        ()

    def run(self, model, scope):
        scope.push
        return []

class OpPopScope(Op):
    def __init__(self):
        ()

    def run(self, model, scope):
        scope.pop
        return []

class OpColour(Op):
    def __init__(self, colour):
        self.colour = colour

    def run(self, model, scope):
        print(f"Colouring scope:\n{scope}\nwith colour {self.colour}")
        model.recolour(scope, self.colour)
        return []

# Given a list of rules, will choose one at random according to their priorirties
class OpChooseRuleWithPriority(Op):
    def __init__(self, rules):
        self.rules = rules

    def run(self, model, scope):
        # Pick a random number less than the max cumulative priority
        rand = uniform(0, self.rules[-1].cumulativePriority)
        i = 0
        while self.rules[i].cumulativePriority < rand:
            i += 1

        return self.rules[i].run(model, scope)
