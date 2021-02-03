import sys

from Lexer import Lexer
from Parser import Parser
from Type import TokenType


def main():
    '''if len(sys.argv) == 1:
        print("Usage; {0} [-t | <filename>]".format(sys.argv[0]))
        return
    string = None
    if sys.argv[1] == "-t":
        string = sys.stdin.read()
    else:
        with open(sys.argv[1], "r") as f:
            string = f.read()
    if string is None:
        print("Unknown Error, try again")
        return'''

    string = sys.stdin.read()

    parser = Parser(string)
    abstract_syntax_tree = parser.parse()
    print(abstract_syntax_tree)


if __name__ == "__main__":
    main()
