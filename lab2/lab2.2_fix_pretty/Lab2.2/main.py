import re
import sys

from Parser.MyLexer import MyLexer, find_column
from Parser.MyParser import MyParser


def main():
    """if len(sys.argv) == 1:
        print(f"Usage; {sys.argv[0]} [-t | <file_name>]")
        return
    string = None
    if sys.argv[1] == "-t":
        string = sys.stdin.read()
    else:
        with open(sys.argv[1], "r") as f:
            string = f.read()
    if string is None:
        print("Unknown Error, try again")
        return"""
    string = """"""
    string = sys.stdin.read()
    # remove comments
    lines = ""
    string = re.split(r'\r\n|\r|\n', string.strip())
    for line in string:
        start = re.search("//", line)
        if start:
            lines += line[:start.span()[0]] + "\n"
        else:
            lines += line + "\n"
    # ---------------------------------------------------
    string = lines
    abstract_syntax_tree = parse(lex(string))[0]
    pretty = str(abstract_syntax_tree)
    return pretty
    """if abstract_syntax_tree != "":
        abstract_syntax_tree.prepass()
        try:
            abstract_syntax_tree.typecheck()
            print("pass")
        except TypecheckerException as e:
            error = str(e)
            result = re.search(r'[0-9]+', error)
            line = ""
            column = ""
            if result is not None:
                line = error[result.start():result.end()]
                error = error[result.end():]
                result = re.search(r'[0-9]+', error)
                if result is not None:
                    column = error[result.start():result.end()]
            print("fail {0} {1} {2}".format(line, column, str(e)))
        try:
            abstract_syntax_tree.evaluate()
        except EvaluatorException as e:
            print(e)"""


def lex(string: str) -> list:
    lexer = MyLexer()
    token_list = []
    for token in lexer.tokenize(string):
        token.index = find_column(string, token)
        token_list.append(token)
    return token_list


def parse(token_list: list) -> tuple:
    parser = MyParser(token_list)
    return parser.parse(iter(token_list))


if __name__ == "__main__":
    pretty = main()
    print(pretty)
