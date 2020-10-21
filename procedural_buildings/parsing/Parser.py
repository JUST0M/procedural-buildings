from sly import Parser as SlyParser
from .Rule import Rule, Right, Left, Size
from .Lexer import Lexer
from ..Ops import *
from sympy import symbols, Eq, Ne
from numpy import pi
from ..RandRange import RandRange, RandIntRange


class Parser(SlyParser):

    tokens = Lexer.tokens

    precedence = (
        ('nonassoc', NEQ, EQ, LT, GT, LTE, GTE),
        ('left', PLUS, MINUS),
        ('left', TIMES, DIVIDE),
        ('right', UMINUS),
        )

    colourNames = {
        'red':   (1,0,0),
        'green': (0,1,0),
        'blue':  (0,0,1),
    }

    def __init__(self):
        self.vars = {}
        self.ruleFromLabel = { }
        self.axes = {'x': 0, 'y': 1, 'z': 2}

    def parse(self, grammar):
        super(Parser, self).parse(grammar)
        return self.ruleFromLabel

    @_('decls NEWLINE rules')
    def grammar(self, p):
        return

    @_('rules')
    def grammar(self, p):
        return

    @_('rules rule')
    def rules(self, p):
        p.rules.append(p.rule)
        return p.rules

    @_('rule')
    def rules(self, p):
        return [p.rule]

    @_('left ARROW right NEWLINE')
    def rule(self, p):
        newRule = Rule(p.left, p.right)
        if newRule.label in self.ruleFromLabel:
            self.ruleFromLabel[newRule.label].append(newRule)
        else:
            self.ruleFromLabel[newRule.label] = [newRule]
        return newRule

    @_('ruleName')
    def left(self, p):
        return Left(*p.ruleName)

    @_('ruleName COLON expr')
    def left(self, p):
        return Left(*p.ruleName, condition=p.expr)

    @_('label')
    def ruleName(self, p):
        return (p.label,)

    @_('label LPAR paramNames RPAR')
    def ruleName(self, p):
        return (p.label, tuple(p.paramNames))

    @_('IDENT')
    def paramNames(self, p):
        return [p.IDENT]

    @_('paramNames COMMA IDENT')
    def paramNames(self, p):
        p.paramNames.append(p.IDENT)
        return p.paramNames

    @_('IDENT')
    def label(self, p):
        return p.IDENT

    @_('op COLON expr')
    def right(self, p):
        return Right(p.op, p.expr)

    @_('op')
    def right(self, p):
        return Right(p.op)

    @_('singleOp')
    def op(self, p):
        return p.singleOp

    @_('label')
    def singleOp(self, p):
        return p.label

    @_('label LPAR ruleParams RPAR')
    def singleOp(self, p):
        return OpSetParams(*p.ruleParams, childOps=[p.label])

    @_('SPLIT LPAR axis RPAR LCURL opParams RCURL')
    def singleOp(self, p):
        return OpSplit(p.axis, perChildArgs=tuple(p.opParams[0]), childOps=p.opParams[1])

    @_('REPEAT LPAR axis RPAR LCURL expr COLON op RCURL')
    def singleOp(self, p):
        return OpRepeat(p.axis, perChildArgs=(p.expr,), childOps=[p.op])

    @_('REPEATN LPAR axis COMMA expr RPAR LCURL op RCURL')
    def singleOp(self, p):
        return OpRepeatN(p.axis, p.expr, childOps=[p.op])

    # TODO: change to use more than just face
    @_('COMP LPAR FACE RPAR LCURL compParams RCURL')
    def singleOp(self, p):
        return OpComp(perChildArgs=tuple(p.compParams[0]), childOps=p.compParams[1])

    @_('COLOUR col')
    def singleOp(self, p):
        return OpColour(*p.col)

    @_('ROTATE LPAR axis COMMA expr RPAR LCURL singleOp RCURL')
    def singleOp(self, p):
        return OpRotate(p.axis, p.expr, childOps=[p.singleOp])

    @_('RESIZESCOPE LPAR size COMMA size COMMA size RPAR LCURL singleOp RCURL')
    def singleOp(self, p):
        return OpResizeScope(p.size0, p.size1, p.size2, childOps=[p.singleOp])

    @_('TRANSLATE LPAR expr COMMA expr COMMA expr RPAR LCURL singleOp RCURL')
    def singleOp(self, p):
        return OpTranslate(p.expr0, p.expr1, p.expr2, childOps=[p.singleOp])

    @_('PRIMITIVE LPAR IDENT RPAR')
    def singleOp(self, p):
        return OpPrimitive(p.IDENT)

    @_('NIL')
    def singleOp(self, p):
        return OpNil()

    @_('LPAR expr COMMA expr COMMA expr RPAR')
    def col(self, p):
        return (p.expr0, p.expr1, p.expr2)

    @_('LPAR IDENT RPAR')
    def col(self, p):
        try:
            return self.colourNames[p.IDENT]
        except LookupError:
            raise RuntimeError(f'Unknown colour: {p.IDENT}')

    @_('size COLON op')
    def opParams(self, p):
        return ([p.size],[p.op])

    @_('opParams BAR size COLON op')
    def opParams(self, p):
        p.opParams[0].append(p.size)
        p.opParams[1].append(p.op)
        return p.opParams

    @_('FACENAME COLON op')
    def compParams(self, p):
        return ([p.FACENAME],[p.op])

    @_('compParams BAR FACENAME COLON op')
    def compParams(self, p):
        p.compParams[0].append(p.FACENAME)
        p.compParams[1].append(p.op)
        return p.compParams

    @_('expr')
    def size(self, p):
        return Size(p.expr, False)

    @_('TILDE number')
    def size(self, p):
        return Size(p.number, True)

    @_('TILDE IDENT')
    def size(self, p):
        try:
            return Size(self.vars[p.IDENT], True)
        except LookupError:
            return Size(symbols(p.IDENT), True)

    @_('TILDE LPAR expr RPAR')
    def size(self, p):
        return Size(p.expr, True)

    @_('FLOAT')
    def number(self, p):
        return p.FLOAT

    @_('INT')
    def number(self, p):
        return p.INT

    @_('RAND LPAR expr COMMA expr RPAR')
    def number(self, p):
        return RandRange(p.expr0, p.expr1)

    @_('RANDINT LPAR expr COMMA expr RPAR')
    def number(self, p):
        return RandIntRange(p.expr0, p.expr1)

    @_('PI')
    def number(self, p):
        return pi

    @_('decl')
    def decls(self, p):
        return

    @_('decls NEWLINE decl')
    def decls(self, p):
        return

    @_('IDENT ASSIGN expr')
    def decl(self, p):
        if type(p.expr) == RandRange or type(p.expr) == RandIntRange:
            self.vars[p.IDENT] = p.expr.evaluate()
        else:
            self.vars[p.IDENT] = p.expr
        return

    @_('AXIS')
    def expr(self, p):
        return self.axes[p.AXIS]

    @_('IDENT')
    def expr(self, p):
        try:
            return self.vars[p.IDENT]
        except LookupError:
            return symbols(p.IDENT)

    @_('number')
    def expr(self, p):
        return p.number

    @_('expr PLUS expr')
    def expr(self, p):
        return p.expr0 + p.expr1

    @_('expr MINUS expr')
    def expr(self, p):
        return p.expr0 - p.expr1

    @_('expr TIMES expr')
    def expr(self, p):
        return p.expr0 * p.expr1

    @_('expr DIVIDE expr')
    def expr(self, p):
        return p.expr0 / p.expr1

    @_('MINUS expr %prec UMINUS')
    def expr(self, p):
        return -p.expr

    @_('expr GT expr')
    def expr(self, p):
        return p.expr0 > p.expr1

    @_('expr LT expr')
    def expr(self, p):
        return p.expr0 < p.expr1

    @_('expr GTE expr')
    def expr(self, p):
        return p.expr0 >= p.expr1

    @_('expr LTE expr')
    def expr(self, p):
        return p.expr0 <= p.expr1

    @_('expr EQ expr')
    def expr(self, p):
        return Eq(p.expr0, p.expr1)

    @_('expr NEQ expr')
    def expr(self, p):
        return Ne(p.expr0, p.expr1)

    @_('LPAR expr RPAR')
    def expr(self, p):
        return p.expr

    @_('expr')
    def ruleParam(self, p):
        return p.expr

    #@_('axis')
    #def ruleParam(self, p):
    #    return p.axis

    @_('ruleParam')
    def ruleParams(self, p):
       return [p.ruleParam]

    @_('ruleParams COMMA ruleParam')
    def ruleParams(self, p):
        p.ruleParams.append(p.ruleParam)
        return p.ruleParams

    @_('AXIS')
    def axis(self, p):
        return self.axes[p.AXIS]
        
    @_('INT')
    def axis(self, p):
        return p.INT

    @_('IDENT')
    def axis(self, p):
        return symbols(p.IDENT)


