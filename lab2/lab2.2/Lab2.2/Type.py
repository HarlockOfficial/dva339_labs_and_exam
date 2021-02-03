from enum import Enum


class BinaryOperatorType(Enum):
    OR = '||'
    AND = '&&'
    NOT_EQUALS = '!='
    LOWER_EQ = '<='
    GREATER_EQUAL = '>='
    LOWER = '<'
    GREATER = '>'
    PLUS = '+'
    MINUS = '-'
    MULTIPLY = '*'
    DIVIDE = '/'
    EQUALS = '=='


class UnaryOperatorType(Enum):
    NOT = '!'
    MINUS = '-'
