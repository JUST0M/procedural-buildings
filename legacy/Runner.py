
class Runner:

    def __init__(self, startScope, verbose=False):
        self.currScope = startScope
        self.startScope = startScope
        self.scopeStack = []
        if hasattr(startScope, 'verbose'):
            startScope.verbose = verbose
        self.verbose = verbose
        self.initObj()

    def run(self, grammar, startRule):
        if self.verbose:
            print(f'Running grammar with start rule {startRule}')
        grammar[startRule].run(self)
        return self.obj


    def pushScope(self):
        self.scopeStack.append(self.currScope)

    def popScope(self):
        self.currScope = self.scopeStack.pop()

    def setScope(self, scope):
        self.currScope = scope

    def initObj(self):
        raise NotImplementedError

    def split(self, obj):
        raise NotImplementedError

    def colour(self, obj, colour):
        raise NotImplementedError

    def translate(self, obj, v):
        raise NotImplementedError