from antlr4 import *
from sys import argv
from DateAndTimeLexer import DateAndTimeLexer
from DateAndTimeParser import DateAndTimeParser


def get_tokens(string):
    input = InputStream.InputStream(string)
    lexer = DateAndTimeLexer(input)
    stream = CommonTokenStream(lexer)
    parser = DateAndTimeParser(stream)
    parser.value()
    return parser.results


if __name__ == '__main__':
    test = argv[1] if len(argv) > 1 else "si giochera' fra un venerdi"
    print get_tokens(test)
