from enum import Enum


class TokenType(Enum):
    KEYW = "KEYW"
    SEP = "SEP"
    OP = "OP"
    ID = "ID"
    NUM = "NUM"
    EOF = "EOF"


class BinaryOperatorType(Enum):
    ADD = " + "
