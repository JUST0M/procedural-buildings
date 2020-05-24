from sly import Parser
from Rule import Rule, Right, Left, Size
from CGALexer import CGALexer
from Ops import *
from sympy import symbols
from numpy import pi


class CGAParser(Parser):
    #debugfile = 'parser.out'

    tokens = CGALexer.tokens

    precedence = (
        ('left', PLUS, MINUS),
        ('left', TIMES, DIVIDE),
        ('right', UMINUS),
        )

    def __init__(self):
        self.vars = {}
        self.ruleFromLabel = { }
        self.rand = symbols("rand")

    def parse(self, grammar):
        super(CGAParser, self).parse(grammar)
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
        # Just do LOD=1 for now
        newRule = Rule(p.left, p.right, 1)
        if newRule.label in self.ruleFromLabel:
            self.ruleFromLabel[newRule.label].append(newRule)
        else:
            self.ruleFromLabel[newRule.label] = [newRule]
        return newRule

    # TODO: add cond
    @_('INT COLON label')
    def left(self, p):
        return Left(p.INT, p.label)

    # TODO: should be able to give params too
    @_('IDENT')
    def label(self, p):
        return p.IDENT

    @_('op COLON expr')
    def right(self, p):
        return Right(p.op, p.expr)

    @_('op')
    def right(self, p):
        return Right(p.op)

    @_('opList')
    def op(self, p):
        return OpSeq(p.opList)

    @_('singleOp')
    def opList(self, p):
        return [p.singleOp]

    @_('opList singleOp')
    def opList(self, p):
        p.opList.append(p.singleOp)
        return p.opList

    @_('label')
    def singleOp(self, p):
        return p.label

    @_('SPLIT LPAR AXIS RPAR LCURL opParams RCURL')
    def singleOp(self, p):
        return OpSplit(p.AXIS, p.opParams[0], p.opParams[1])

    @_('REPEAT LPAR AXIS RPAR LCURL expr COLON op RCURL')
    def singleOp(self, p):
        return OpRepeat(p.AXIS, p.expr, [p.op])

    # TODO: change to use more than just face
    @_('COMP LPAR FACE RPAR LCURL compParams RCURL')
    def singleOp(self, p):
        return OpComp(p.compParams[0], p.compParams[1])

    @_('COLOUR col')
    def singleOp(self, p):
        return OpColour(p.col)

    @_('ROTATE LPAR AXIS COMMA expr RPAR')
    def singleOp(self, p):
        return OpRotate(p.AXIS, p.expr)

    @_('RESIZESCOPE LPAR size COMMA size COMMA size RPAR')
    def singleOp(self, p):
        return OpResizeScope(p.size0, p.size1, p.size2)

    @_('TRANSLATE LPAR exprParams RPAR')
    def singleOp(self, p):
        return OpTranslate(p.exprParams)

    @_('PRIMITIVE LPAR IDENT RPAR')
    def singleOp(self, p):
        return OpPrimitive(p.IDENT)

    @_('NIL')
    def singleOp(self, p):
        return OpNil()

    @_('LPAR expr COMMA expr COMMA expr RPAR')
    def col(self, p):
        return [p.expr0, p.expr1, p.expr2]

    @_('LPAR IDENT RPAR')
    def col(self, p):
        return p.IDENT

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
            raise RuntimeError(f'Undefined variable {p.IDENT!r}')

    @_('TILDE LPAR expr RPAR')
    def size(self, p):
        return Size(p.expr, True)

    @_('FLOAT')
    def number(self, p):
        return p.FLOAT

    @_('INT')
    def number(self, p):
        return p.INT

    @_('RAND')
    def number(self, p):
        return self.rand

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
        self.vars[p.IDENT] = p.expr
        return

    @_('IDENT')
    def expr(self, p):
        try:
            return self.vars[p.IDENT]
        except LookupError:
            raise RuntimeError(f'Undefined variable {p.IDENT!r}')

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

    @_('LPAR expr RPAR')
    def expr(self, p):
        return p.expr

    @_('expr')
    def exprParams(self, p):
        return [p.expr]

    @_('exprParams COMMA expr')
    def exprParams(self, p):
        p.exprParams.append(p.expr)
        return p.exprParams


