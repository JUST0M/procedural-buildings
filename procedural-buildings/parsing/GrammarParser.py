from parsing.ParserAbstract import ParserAbstract
from parsing.Lexer import Lexer
from parsing.Parser import Parser
from parsing.Checker import Checker


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
