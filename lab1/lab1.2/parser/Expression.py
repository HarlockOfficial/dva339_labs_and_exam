from abc import ABC, abstractmethod

import Statement
from Type import BinaryOperatorType


class Expression(ABC):
    @abstractmethod
    def pretty(self) -> str:
        pass

    def __str__(self):
        return self.pretty()


class IdentifierExpression(Expression):
    def __init__(self, identifier: str):
        self.__identifier = identifier

    def pretty(self) -> str:
        return str(self.__identifier)


class NumberExpression(Expression):
    def __init__(self, num: int):
        self.__num = num

    def pretty(self) -> str:
        return str(self.__num)


class BinaryOperatorExpression(Expression):
    def __init__(self, bin_op_type: BinaryOperatorType, left: Expression, right: Expression):
        self.__bin_op_type = bin_op_type
        self.__left = left
        self.__right = right

    def pretty(self) -> str:
        return self.__left.pretty() + str(self.__bin_op_type.value) + self.__right.pretty()


class LetExpression(Expression):
    def __init__(self, stmt: Statement, expr: Expression):
        self.__stmt = stmt
        self.__expr = expr

    def pretty(self) -> str:
        return "(" + self.__stmt.pretty() + "," + self.__expr.pretty() + ")"
