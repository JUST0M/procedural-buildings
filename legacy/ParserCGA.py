from ParserAbstract import ParserAbstract
from CGALexer import CGALexer
from CGAParser import CGAParser
from CGAChecker import CGAChecker


class ParserCGA(ParserAbstract):

    def parse(self, grammar):
        lexer = CGALexer()
        parser = CGAParser()
        checker = CGAChecker()
        return(
            checker.check(
                parser.parse(
                    lexer.tokenize(grammar)
                )
            )
        )


