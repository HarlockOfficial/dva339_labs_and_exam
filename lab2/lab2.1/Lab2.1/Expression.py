from abc import ABC, abstractmethod

from Type import BinaryOperatorType, UnaryOperatorType


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
        return self.__identifier


class NumberExpression(Expression):
    def __init__(self, num: int):
        self.__num = num

    def pretty(self) -> str:
        return str(self.__num)


class BooleanExpression(Expression):
    def __init__(self, boolean: bool):
        self.__boolean = boolean

    def pretty(self) -> str:
        return str(self.__boolean)


class BinaryOperatorExpression(Expression):
    def __init__(self, bin_op_type: BinaryOperatorType, left: Expression, right: Expression):
        self.__bin_op_type = bin_op_type
        self.__left = left
        self.__right = right

    def pretty(self) -> str:
        return str(self.__left) + str(self.__bin_op_type.value) + str(self.__right)


class UnaryOperatorExpression(Expression):
    def __init__(self, unary_op_type: UnaryOperatorType, expression: Expression):
        self.__unary_op_type = unary_op_type
        self.__expression = expression

    def pretty(self) -> str:
        return str(self.__unary_op_type.value) + " " + str(self.__expression)


class SeparatorExpression(Expression):
    def __init__(self, actual_expression: Expression, next_expression: Expression = None):
        self.__actual_expression = actual_expression
        self.__next_expression = next_expression

    def pretty(self) -> str:
        return str(self.__actual_expression) + \
               ((", "+str(self.__next_expression)) if self.__next_expression is not None else "")


class BlockExpression(Expression):
    def __init__(self, expression: Expression):
        self.__expression = expression

    def pretty(self) -> str:
        string = "( "
        if self.__expression is not None:
            string += str(self.__expression)
        return string + " ) "


class FunctionCallExpression(Expression):
    def __init__(self, identifier: IdentifierExpression, expression: BlockExpression):
        self.__identifier = identifier
        self.__expression = expression

    def pretty(self) -> str:
        return str(self.__identifier)+" "+str(self.__expression)


class SingleExpression(Expression):
    def __init__(self, expression:Expression):
        self.__expression = expression

    def pretty(self) -> str:
        return str(self.__expression)+"; "
