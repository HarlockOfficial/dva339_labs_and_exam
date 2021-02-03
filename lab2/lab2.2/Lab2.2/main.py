import sys
from MyLexer import MyLexer, find_column
from MyParser import MyParser


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
    string = sys.stdin.read()
    abstract_syntax_tree = parse(lex(string))[0]
    pretty = str(abstract_syntax_tree)
    print(pretty)


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
    main()
