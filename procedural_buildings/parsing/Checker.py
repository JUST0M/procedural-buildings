from .Rule import *
from ..Ops import OpChooseRuleWithPriority, Op

class Checker:
    def __init__(self):
        self.opFromLabel = {}
        pass

    def check(self, ruleFromLabel):
        self.ruleFromLabel = ruleFromLabel
        # TODO: Probably only need to check start rule since we will check all reachable
        for label in ruleFromLabel:
            self.processLabel(label)
        return self.opFromLabel

    def createPriorityRule(self, rules):
        childOps = [r.op for r in rules]
        priorities = tuple(1 if r.priority==None else r.priority for r in rules)
        conditions = tuple(r.condition for r in rules)
        newOp = OpChooseRuleWithPriority(perChildArgs=(priorities, conditions), childOps=childOps)
        if hasattr(childOps[0], 'paramNames'):
            newOp.addParams(childOps[0].paramNames)
        return newOp

    def processLabel(self, label):
        if label not in self.ruleFromLabel:
            raise RuntimeError(f'Rule with label {label} does not exist')

        rules = self.ruleFromLabel[label]
        if label not in self.opFromLabel:
            if len(rules) == 1:
                op = rules[0].op
            else:
                op = self.createPriorityRule(rules)
            self.opFromLabel[label] = op
            self.processOp(op)

        return self.opFromLabel[label]

    # given an op, check it's children
    # for any children that are labels, process them
    # for any children that are ops, recursively process them
    def processOp(self, op):
        if op.childOps != None:
            for i in range(len(op.childOps)):
                if type(op.childOps[i]) == str:
                    op.childOps[i] = self.processLabel(op.childOps[i])
                elif type(op.childOps[i]).__bases__[0].__name__ == 'Op':
                    self.processOp(op.childOps[i])
                else:
                    raise RuntimeError(f'Op has a child of invalid type {type(op.childOps[i])}.')
