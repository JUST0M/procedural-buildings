from .ParserAbstract import ParserAbstract
from .Lexer import Lexer
from .Parser import Parser
from .Checker import Checker


class GrammarParser(ParserAbstract):

    def parse(self, grammar):
        lexer = Lexer()
        parser = Parser()
        checker = Checker()
        return(
            checker.check(
                parser.parse(
                    lexer.tokenize(grammar)
                )
            )
        )
