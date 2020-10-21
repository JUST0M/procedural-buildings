from .parsing.GrammarParser import GrammarParser
#from ScopeNewNew import Scope
from .Scope import Scope
import numpy as np
from .ContextObj import ContextOBJ
from .Ops import OpRepeat, OpSplit, OpNil
from .parsing.Rule import Size
from .ObjReader import objsToOpGraph, objToOpGraph
from .RandomOpGraph import genRandOpGraph
from time import time

class Processor:
    grammarDir = '../grammars/'
    outDir = 'outputs/'
    engineeredDir = 'engineered/'
    fileExt = 'obj'

    # Given an op graph, run it on the given scope and write the output to a file
    def opGraphToObj(self, opGraph, startScope, outFile, context=ContextOBJ()):
        context.reset()
        print("Running op graph to create obj")
        opGraph.run(context, startScope, {})
        print("Writing obj to file")
        context.writeToFile(outFile)

    # Given an op graph, run it some number of times and write the resulting buildings to the same file
    def opGraphToManyObjs(self, opGraph, n, startScope, repeatAxis, gap, outFile, context=ContextOBJ()):
        # Construct a new initial scope by expanding the given start scope according to n and gap
        startScopeSize = startScope.size[repeatAxis]
        newSize = (startScopeSize + gap) * n
        newScope = startScope.resizeAxis(repeatAxis, newSize)
        # Create a split operation that creates a gap next to each building
        split = OpSplit(repeatAxis, perChildArgs=(Size(startScopeSize, False), Size(gap,False)), childOps=[opGraph, OpNil()])
        # Repeat the building-gap operation n times
        newOp = OpRepeat(repeatAxis, perChildArgs=(startScopeSize + gap,), childOps=[split])
        # Run this repeat operation
        self.opGraphToObj(newOp, newScope, outFile, context)

    # Given a grammar file and start rule, return the operation graph corresponding to that grammar
    def grammarFileToOpGraph(self, grammarName, startRule):
        print("Creating operation graph from grammar...")
        with open(self.grammarDir + grammarName) as f:
            grammarText = f.read()
        parser = GrammarParser()
        return parser.parse(grammarText)[startRule]

    # Given a grammar, write the result of running that grammar to an output file
    def grammarToObject(self, grammarName, startRule, startScope, outFile):
        opGraph = self.grammarFileToOpGraph(grammarName, startRule)
        self.opGraphToObj(opGraph, startScope, outFile)

    # Given a grammar, write the result of running that grammar n times to a single output file
    def grammarToManyObjs(self, grammarName, startRule, startScope, n, gap, outFile):
        opGraph = self.grammarFileToOpGraph(grammarName, startRule)
        self.opGraphToManyObjs(opGraph, n, startScope, 0, gap, outFile)

    # Given a grammar, write the result of running that grammar n times to n different output files
    def grammarToManyObjFiles(self, grammarName, startRule, startScope, n, filePrefix):
        opGraph = self.grammarFileToOpGraph(grammarName, startRule)
        fileNames = []
        for i in range(n):
            print(f"Generating obj file {i+1}/{n}")
            fname = f"{filePrefix}{i}.{self.fileExt}"
            self.opGraphToObj(opGraph, startScope, fname)
            fileNames.append(fname)
        return fileNames

    # Given a grammar generate some op graphs then combine those into one
    def grammarToRegenOpGraph(self, grammarName, startRule, n):
        opGraph = self.grammarFileToOpGraph(grammarName, startRule)
        return opGraph.regenOpFromExamples(n)

    # Given a set of example object files, return an operation graph representing the examples
    def objsToOpGraph(self, objFiles):
        print("Generating operation graph from objects")
        return objsToOpGraph(objFiles)

    # Given a set of example object files, construct a grammar representing the examples
    def objsToGrammar(self, objFiles, grammarFile):
        opGraph, prims = self.objsToOpGraph(objFiles)
        print("Creating grammar from op graph")
        grammarText = opGraph.toGrammarText()
        print("Writing grammar to file")
        with open(f"{self.engineeredDir}{grammarFile}", "w") as f:
            f.write(grammarText)
        print("Done")

    # Given a set of example object files, write a new set of inferred buildings to a single output file
    def objsToObjs(self, objFiles, scope, n, gap, outFile):
        opGraph, prims = self.objsToOpGraph(objFiles)
        context = ContextOBJ(prims)
        self.opGraphToManyObjs(opGraph, n, scope, 0, gap, outFile, context)

    # Run a speed test by generating many operation graphs, turning those into
    # object files and then inferring operation graphs from those object files
    def speedTest(self, maxDepth, maxBranch):
        startScope = Scope.freshScope(np.array([0,0,0]),np.array([1000,1000,1000]))
        results = []
        # repeats determines how many tests we run for each combination of op graph parameters
        repeats = 5
        for depth in range(1, maxDepth):
            for branch in range(1, maxBranch):
                maxPrims = branch**depth
                numPrims = 1
                while numPrims < maxPrims:
                    print(depth, branch, numPrims)
                    runs = ([],[])
                    for i in range(repeats):
                        # Create a random operation graph with the given args
                        op = genRandOpGraph(depth, branch, numPrims)
                        t0 = time()
                        # Create an object from the operation graph
                        self.opGraphToObj(op, startScope, 'temp.obj')
                        t1 = time()
                        # Reverse-engineer an operation graph from the random obj file
                        objToOpGraph('temp.obj')
                        t2 = time()
                        runs[0].append(t1-t0)
                        runs[1].append(t2-t1)
                    opToObj = sum(runs[0])/repeats
                    objToOp = sum(runs[1])/repeats
                    results.append([depth, branch, numPrims, round(opToObj,3), round(objToOp,3)])
                    numPrims *= 2

        print("max depth\tmax branch\tnum prims\top-to-obj time\tobj-to-op time")
        for r in results:
            print("\t\t".join(str(x) for x in r))

# Modern house example
if __name__ == '__main__':
    startScope = Scope.freshScope(np.array([0,0,0]),np.array([10,10,1.5]))
    p = Processor()
    objFiles = p.grammarToManyObjFiles('city', 'plot', startScope, 10, 'temp')
    p.objsToObjs(objFiles, startScope,  10, 10, 'outputs/city_gen.obj')
