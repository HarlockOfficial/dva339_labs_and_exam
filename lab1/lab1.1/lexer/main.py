from Lexer import Lexer
from Type import Type

import sys


def main():
    string = sys.stdin.read()
    lexer = Lexer(string)
    while True:
        tmp = lexer.next()
        print(tmp, end=" ")
        if tmp.get_token_type() == Type.EOF:
            break
    print()


if __name__ == "__main__":
    main()
