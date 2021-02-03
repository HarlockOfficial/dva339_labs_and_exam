from abc import ABC, abstractmethod

from Type import BinaryOperatorType, UnaryOperatorType


class Expression(ABC):
    @abstractmethod
    def pretty(self, pretty_builder, outer_precedence: int = None, opposite: bool = None) -> None:
        pass

    def __str__(self):
        import PrettyBuilder
        builder = PrettyBuilder.PrettyBuilder()
        self.pretty(builder)
        return str(builder)


class IdentifierExpression(Expression):
    def __init__(self, identifier: str):
        self.__identifier = identifier

    def pretty(self, pretty_builder, outer_precedence: int = None, opposite: bool = None) -> None:
        if outer_precedence is None and opposite is None:
            self.pretty(pretty_builder, 0, False)
            return
        pretty_builder.append(str(self.__identifier))


class NumberExpression(Expression):
    def __init__(self, num: int):
        self.__num = num

    def pretty(self, pretty_builder, outer_precedence: int = None, opposite: bool = None) -> None:
        if outer_precedence is None and opposite is None:
            self.pretty(pretty_builder, 0, False)
            return
        pretty_builder.append(str(self.__num))


class BooleanExpression(Expression):
    def __init__(self, boolean: bool):
        self.__boolean = boolean

    def pretty(self, pretty_builder, outer_precedence: int = None, opposite: bool = None) -> None:
        if outer_precedence is None and opposite is None:
            self.pretty(pretty_builder, 0, False)
            return
        pretty_builder.append(str(self.__boolean))


class BinaryOperatorExpression(Expression):
    def __init__(self, bin_op_type: BinaryOperatorType, left: Expression, right: Expression):
        self.__bin_op_type = bin_op_type
        self.__left = left
        self.__right = right

    # TODO fix outer_precedence and opposite
    def pretty(self, pretty_builder, outer_precedence: int = None, opposite: bool = None) -> None:
        if outer_precedence is None and opposite is None:
            self.pretty(pretty_builder, 0, False)
            return
        self.__left.pretty(pretty_builder, 0, False)
        pretty_builder.append(self.__bin_op_type.value)
        self.__right.pretty(pretty_builder, 0, False)


class UnaryOperatorExpression(Expression):
    def __init__(self, unary_op_type: UnaryOperatorType, expression: Expression):
        self.__unary_op_type = unary_op_type
        self.__expression = expression

    # TODO fix outer_precedence and opposite
    def pretty(self, pretty_builder, outer_precedence: int = None, opposite: bool = None) -> None:
        if outer_precedence is None and opposite is None:
            self.pretty(pretty_builder, 0, False)
            return
        pretty_builder.append(self.__unary_op_type.value)
        self.__expression.pretty(pretty_builder, 0, False)


class SeparatorExpression(Expression):
    def __init__(self, actual_expression: Expression, next_expression: Expression = None):
        self.__actual_expression = actual_expression
        self.__next_expression = next_expression

    # TODO fix outer_precedence and opposite
    def pretty(self, pretty_builder, outer_precedence: int = None, opposite: bool = None) -> None:
        if outer_precedence is None and opposite is None:
            self.pretty(pretty_builder, 0, False)
            return
        self.__actual_expression.pretty(pretty_builder, 0, False)
        if self.__next_expression is not None:
            pretty_builder.append(", ")
            self.__next_expression.pretty(pretty_builder, 0, False)


class BlockExpression(Expression):
    def __init__(self, expression: Expression):
        self.__expression = expression

    # TODO fix outer_precedence and opposite
    def pretty(self, pretty_builder, outer_precedence: int = None, opposite: bool = None) -> None:
        if outer_precedence is None and opposite is None:
            self.pretty(pretty_builder, 0, False)
            return
        pretty_builder.append("(")
        if self.__expression is not None:
            self.__expression.pretty(pretty_builder, 0, False)
        pretty_builder.append(")")


class FunctionCallExpression(Expression):
    def __init__(self, identifier: IdentifierExpression, expression: BlockExpression):
        self.__identifier = identifier
        self.__expression = expression

    # TODO fix outer_precedence and opposite
    def pretty(self, pretty_builder, outer_precedence: int = None, opposite: bool = None) -> None:
        if outer_precedence is None and opposite is None:
            self.pretty(pretty_builder, 0, False)
            return
        self.__identifier.pretty(pretty_builder, 0, False)
        self.__expression.pretty(pretty_builder, 0, False)


class SingleExpression(Expression):
    def __init__(self, expression: Expression):
        self.__expression = expression

    # TODO Fix outer_precedence
    def pretty(self, pretty_builder, outer_precedence: int = None, opposite: bool = None) -> None:
        if outer_precedence is None and opposite is None:
            self.pretty(pretty_builder, 0, False)
            return
        self.__expression.pretty(pretty_builder, 0, False)
        pretty_builder.append(";")
