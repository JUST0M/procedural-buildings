# ================================
# test: test_parser
#
# description:
#     Unit tests on the CGA shape parser
#
# ================================


from psb import *
import unittest

class TestParser(unittest.TestCase):
    basicCube = Model(Position(0,0,0), CoordinateSystem((1,0,0), (0,1,0), (0,0,1)), Size(10,10,10))

    def testSimpleSplitAndColour(self):
        grammar = Grammar("grammars\/split_and_colour", "plot")
        grammar.run(self.basicCube, 1)

    def testProbabilisticRules(self):
        grammar = Grammar("grammars\/probabilistic_split", "plot")
        grammar.run(self.basicCube, 1)

if __name__ == '__main__':
    unittest.main()