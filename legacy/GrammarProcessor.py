from ParserCGA import ParserCGA
from RunnerText import RunnerText
from RunnerGeometry import RunnerGeometry
from VisualiserGeometry import VisualiserGeometry
from Scope import Scope
import cProfile
import numpy as np

class GrammarProcessor:
    grammarDir = '../test/grammars/'
    outDir = 'outputs/'

    # Parse the grammar text to get a runable representation of the grammar
    def parse(self, parser, grammar):
        return parser.parse(grammar)

    # Run the grammar to get an internal representation of the resulting geometry
    def run(self, runner, parsedGrammar, startRule):
        return runner.run(parsedGrammar, startRule)

    # Visualise the result
    def visualise(self, visualiser, obj):
        return visualiser.visualise(obj)

    def processGrammar(self, grammarName, startRule, startScope, outFile):
        with open(self.grammarDir + grammarName) as f:
            grammarText = f.read()
        parser = ParserCGA()
        runner = RunnerGeometry(startScope)
        visualiser = VisualiserGeometry(self.outDir + outFile)
        self.visualise(visualiser,
                       self.run(runner,
                                self.parse(parser, grammarText),
                                startRule))

if __name__ == '__main__':
    startScope = Scope.freshScope(np.array([0,0,0]),np.array([120,10,0]))
    cProfile.run("GrammarProcessor().processGrammar('nice_roof_house','plot', startScope, 'out.ply')", 'profile_stats')