from abc import ABC, abstractmethod

import Evaluator
from Evaluator import PrepassState, EvaluationState, EvaluatorException
from Parser.Type import BinaryOperatorType, UnaryOperatorType


class Expression(ABC):
    @abstractmethod
    def evaluate(self, state: EvaluationState = None):
        if state is None:
            return self.evaluate(EvaluationState())

    @abstractmethod
    def prepass(self, prepass: PrepassState = None):
        if prepass is None:
            self.prepass(PrepassState())

    @abstractmethod
    def pretty(self, pretty_builder, outer_precedence: int = None, opposite: bool = None) -> None:
        pass

    def __str__(self):
        from PrettyPrinter import PrettyBuilder
        builder = PrettyBuilder()
        self.pretty(builder)
        return str(builder)


class IdentifierExpression(Expression):
    def __init__(self, identifier: str):
        self.__identifier = identifier
        self.__original_identifier = identifier

    def pretty(self, pretty_builder, outer_precedence: int = None, opposite: bool = None) -> None:
        if outer_precedence is None and opposite is None:
            self.pretty(pretty_builder, 0, False)
            return
        pretty_builder.append(str(self.__identifier))

    def prepass(self, prepass: PrepassState = None):
        if prepass is None:
            self.prepass(PrepassState())
            return
        self.__identifier = prepass.rename(self.__identifier)

    def evaluate(self, state: EvaluationState = None):
        if state is None:
            return self.evaluate(state)
        if not state.has(str(self.__identifier)):
            raise EvaluatorException("INTERPRETATION ERROR: undeclared variable")
        return state.lookup(str(self.__identifier)), Evaluator.ReturnType.CONTINUE


class NumberExpression(Expression):
    def __init__(self, num: int):
        self.__num = num

    def pretty(self, pretty_builder, outer_precedence: int = None, opposite: bool = None) -> None:
        if outer_precedence is None and opposite is None:
            self.pretty(pretty_builder, 0, False)
            return
        pretty_builder.append(str(self.__num))

    def prepass(self, prepass: PrepassState = None):
        pass

    def evaluate(self, state: EvaluationState = None):
        if state is None:
            return self.evaluate(EvaluationState())
        return int(self.__num), Evaluator.ReturnType.CONTINUE


class BooleanExpression(Expression):
    def __init__(self, boolean: bool):
        self.__boolean = boolean

    def pretty(self, pretty_builder, outer_precedence: int = None, opposite: bool = None) -> None:
        if outer_precedence is None and opposite is None:
            self.pretty(pretty_builder, 0, False)
            return
        pretty_builder.append(str(self.__boolean))

    def prepass(self, prepass: PrepassState = None):
        pass

    def evaluate(self, state: EvaluationState = None):
        if state is None:
            return self.evaluate(EvaluationState())
        if self.__boolean == "false":
            return False, Evaluator.ReturnType.CONTINUE
        if self.__boolean == "true":
            return True, Evaluator.ReturnType.CONTINUE
        raise EvaluatorException("INTERPRETATION ERROR: expected boolean value got {0}".format(self.__boolean))


class BinaryOperatorExpression(Expression):
    def __init__(self, bin_op_type: BinaryOperatorType, left: Expression, right: Expression):
        self.__bin_op_type = bin_op_type
        self.__left = left
        self.__right = right

    def pretty(self, pretty_builder, outer_precedence: int = None, opposite: bool = None) -> None:
        if outer_precedence is None and opposite is None:
            self.pretty(pretty_builder, 0, False)
            return
        self.__left.pretty(pretty_builder, 0, False)
        pretty_builder.append(self.__bin_op_type.value)
        self.__right.pretty(pretty_builder, 0, False)

    def prepass(self, prepass: PrepassState = None):
        if prepass is None:
            self.prepass(PrepassState())
            return
        self.__left.prepass(prepass)
        self.__right.prepass(prepass)

    def evaluate(self, state: EvaluationState = None):
        if state is None:
            return self.evaluate(EvaluationState())

        val1, ret = self.__left.evaluate(state)
        val2, ret = self.__right.evaluate(state)

        if self.__bin_op_type == BinaryOperatorType.OR:
            if type(val1) is not bool:
                raise EvaluatorException("INTERPRETATION ERROR: Expected boolean got {0}".format(type(val1)))
            if val1:
                return True, Evaluator.ReturnType.CONTINUE
            if type(val2) is not bool:
                raise EvaluatorException("INTERPRETATION ERROR: Expected boolean got {0}".format(type(val2)))
            return val2, Evaluator.ReturnType.CONTINUE
        if self.__bin_op_type == BinaryOperatorType.AND:
            if type(val1) is not bool:
                raise EvaluatorException("INTERPRETATION ERROR: Expected boolean got {0}".format(type(val1)))
            if not val1:
                return False, Evaluator.ReturnType.CONTINUE
            if type(val2) is not bool:
                raise EvaluatorException("INTERPRETATION ERROR: Expected boolean got {0}".format(type(val2)))
            return val1 and val2, Evaluator.ReturnType.CONTINUE
        if self.__bin_op_type == BinaryOperatorType.NOT_EQUALS:
            if type(val1) is not int:
                raise EvaluatorException("INTERPRETATION ERROR: Expected integer got {0}".format(type(val1)))
            if type(val2) is not int:
                raise EvaluatorException("INTERPRETATION ERROR: Expected integer got {0}".format(type(val2)))
            return val1 != val2, Evaluator.ReturnType.CONTINUE
        if self.__bin_op_type == BinaryOperatorType.LOWER_EQ:
            if type(val1) is not int:
                raise EvaluatorException("INTERPRETATION ERROR: Expected integer got {0}".format(type(val1)))
            if type(val2) is not int:
                raise EvaluatorException("INTERPRETATION ERROR: Expected integer got {0}".format(type(val2)))
            return val1 <= val2, Evaluator.ReturnType.CONTINUE
        if self.__bin_op_type == BinaryOperatorType.GREATER_EQUAL:
            if type(val1) is not int:
                raise EvaluatorException("INTERPRETATION ERROR: Expected integer got {0}".format(type(val1)))
            if type(val2) is not int:
                raise EvaluatorException("INTERPRETATION ERROR: Expected integer got {0}".format(type(val2)))
            return val1 >= val2, Evaluator.ReturnType.CONTINUE
        if self.__bin_op_type == BinaryOperatorType.LOWER:
            if type(val1) is not int:
                raise EvaluatorException("INTERPRETATION ERROR: Expected integer got {0}".format(type(val1)))
            if type(val2) is not int:
                raise EvaluatorException("INTERPRETATION ERROR: Expected integer got {0}".format(type(val2)))
            return val1 < val2, Evaluator.ReturnType.CONTINUE
        if self.__bin_op_type == BinaryOperatorType.GREATER:
            if type(val1) is not int:
                raise EvaluatorException("INTERPRETATION ERROR: Expected integer got {0}".format(type(val1)))
            if type(val2) is not int:
                raise EvaluatorException("INTERPRETATION ERROR: Expected integer got {0}".format(type(val2)))
            return val1 > val2, Evaluator.ReturnType.CONTINUE
        if self.__bin_op_type == BinaryOperatorType.PLUS:
            if type(val1) is not int:
                raise EvaluatorException("INTERPRETATION ERROR: Expected integer got {0}".format(type(val1)))
            if type(val2) is not int:
                raise EvaluatorException("INTERPRETATION ERROR: Expected integer got {0}".format(type(val2)))
            return val1 + val2, Evaluator.ReturnType.CONTINUE
        if self.__bin_op_type == BinaryOperatorType.MINUS:
            if type(val1) is not int:
                raise EvaluatorException("INTERPRETATION ERROR: Expected integer got {0}".format(type(val1)))
            if type(val2) is not int:
                raise EvaluatorException("INTERPRETATION ERROR: Expected integer got {0}".format(type(val2)))
            return val1 - val2, Evaluator.ReturnType.CONTINUE
        if self.__bin_op_type == BinaryOperatorType.MULTIPLY:
            if type(val1) is not int:
                raise EvaluatorException("INTERPRETATION ERROR: Expected integer got {0}".format(type(val1)))
            if type(val2) is not int:
                raise EvaluatorException("INTERPRETATION ERROR: Expected integer got {0}".format(type(val2)))
            return val1 * val2, Evaluator.ReturnType.CONTINUE
        if self.__bin_op_type == BinaryOperatorType.DIVIDE:
            if type(val1) is not int:
                raise EvaluatorException("INTERPRETATION ERROR: Expected integer got {0}".format(type(val1)))
            if type(val2) is not int:
                raise EvaluatorException("INTERPRETATION ERROR: Expected integer got {0}".format(type(val2)))
            return int(val1 / val2), Evaluator.ReturnType.CONTINUE
        if self.__bin_op_type == BinaryOperatorType.MODULUS:
            if type(val1) is not int:
                raise EvaluatorException("INTERPRETATION ERROR: Expected integer got {0}".format(type(val1)))
            if type(val2) is not int:
                raise EvaluatorException("INTERPRETATION ERROR: Expected integer got {0}".format(type(val2)))
            return int(val1 % val2), Evaluator.ReturnType.CONTINUE
        if self.__bin_op_type == BinaryOperatorType.EQUALS:
            if type(val1) is not int:
                raise EvaluatorException("INTERPRETATION ERROR: Expected integer got {0}".format(type(val1)))
            if type(val2) is not int:
                raise EvaluatorException("INTERPRETATION ERROR: Expected integer got {0}".format(type(val2)))
            return val1 == val2, Evaluator.ReturnType.CONTINUE
        raise EvaluatorException("INTERPRETATION ERROR: Invalid binary operator expression")


class UnaryOperatorExpression(Expression):
    def __init__(self, unary_op_type: UnaryOperatorType, expression: Expression):
        self.__unary_op_type = unary_op_type
        self.__expression = expression

    def pretty(self, pretty_builder, outer_precedence: int = None, opposite: bool = None) -> None:
        if outer_precedence is None and opposite is None:
            self.pretty(pretty_builder, 0, False)
            return
        pretty_builder.append(self.__unary_op_type.value)
        self.__expression.pretty(pretty_builder, 0, False)

    def prepass(self, prepass: PrepassState = None):
        if prepass is None:
            self.prepass(PrepassState())
            return
        self.__expression.prepass(prepass)

    def evaluate(self, state: EvaluationState = None):
        if state is None:
            return self.evaluate(EvaluationState())
        val, ret = self.__expression.evaluate(state)
        if self.__unary_op_type == UnaryOperatorType.NOT:
            if type(val) is not bool:
                raise EvaluatorException("INTERPRETATION ERROR: Expected boolean got {0}".format(type(val)))
            return not val, Evaluator.ReturnType.CONTINUE
        if self.__unary_op_type == UnaryOperatorType.MINUS:
            if type(val) is not int:
                raise EvaluatorException("INTERPRETATION ERROR: Expected integer got {0}".format(type(val)))
            return -val, Evaluator.ReturnType.CONTINUE
        raise EvaluatorException("INTERPRETATION ERROR: Invalid unary operator expression")


class SeparatorExpression(Expression):
    def __init__(self, actual_expression: Expression, next_expression: Expression = None):
        self.__current_expression = actual_expression
        self.__next_expression = next_expression

    def pretty(self, pretty_builder, outer_precedence: int = None, opposite: bool = None) -> None:
        if outer_precedence is None and opposite is None:
            self.pretty(pretty_builder, 0, False)
            return
        self.__current_expression.pretty(pretty_builder, 0, False)
        if self.__next_expression is not None:
            pretty_builder.append(", ")
            self.__next_expression.pretty(pretty_builder, 0, False)

    def prepass(self, prepass: PrepassState = None):
        if prepass is None:
            self.prepass(PrepassState())
            return
        self.__current_expression.prepass(prepass)
        if self.__next_expression is not None:
            self.__next_expression.prepass(prepass)

    def evaluate(self, state: EvaluationState = None):
        if state is None:
            return self.evaluate(EvaluationState())
        if self.__next_expression is None:
            val, ret = self.__current_expression.evaluate(state)
            return [val], Evaluator.ReturnType.CONTINUE
        val, ret = self.__next_expression.evaluate(state)
        val2, ret = self.__current_expression.evaluate(state)
        val.insert(0, val2)
        return val, Evaluator.ReturnType.CONTINUE


class BlockExpression(Expression):
    def __init__(self, expression: Expression):
        self.__expression = expression

    def pretty(self, pretty_builder, outer_precedence: int = None, opposite: bool = None) -> None:
        if outer_precedence is None and opposite is None:
            self.pretty(pretty_builder, 0, False)
            return
        pretty_builder.append("(")
        if self.__expression is not None:
            self.__expression.pretty(pretty_builder, 0, False)
        pretty_builder.append(")")

    def prepass(self, prepass: PrepassState = None):
        if prepass is None:
            self.prepass(PrepassState())
            return
        if self.__expression is not None:
            self.__expression.prepass(prepass)

    def evaluate(self, state: EvaluationState = None):
        if state is None:
            return self.evaluate(EvaluationState())
        if self.__expression is not None:
            val, ret = self.__expression.evaluate(state)
        else:
            val = list()
            ret = Evaluator.ReturnType.CONTINUE
        return val, ret


class FunctionCallExpression(Expression):
    def __init__(self, identifier: IdentifierExpression, expression: BlockExpression):
        self.__identifier = identifier
        self.__expression = expression

    def pretty(self, pretty_builder, outer_precedence: int = None, opposite: bool = None) -> None:
        if outer_precedence is None and opposite is None:
            self.pretty(pretty_builder, 0, False)
            return
        self.__identifier.pretty(pretty_builder, 0, False)
        self.__expression.pretty(pretty_builder, 0, False)

    def prepass(self, prepass: PrepassState = None):
        if prepass is None:
            self.prepass(PrepassState())
            return
        # self.__identifier.prepass(prepass)
        self.__expression.prepass(prepass)

    def evaluate(self, state: EvaluationState = None):
        if state is None:
            return self.evaluate(EvaluationState())
        if str(self.__identifier) == "print":
            val, ret = self.__expression.evaluate(state)
            for elem in val:
                print(elem, end=" ")
            print()
            return None, Evaluator.ReturnType.CONTINUE
        if not state.has_function(str(self.__identifier)):
            raise EvaluatorException("INTERPRETATION ERROR: Undefined function {0}".format(str(self.__identifier)))
        fun = state.lookup_function(str(self.__identifier))
        params = fun[1]
        if params:
            params, ret = params.evaluate(state)
        passed_values, ret = self.__expression.evaluate(state)
        if (params is not None and passed_values is None) or (params is None and passed_values is not None) or \
                (params is not None and passed_values is not None and len(params) != len(passed_values)):
            raise EvaluatorException("INTERPRETATION ERROR: number of parameters not valid")
        state.enter_scope()
        if passed_values is not None and params is not None:
            for i in range(len(passed_values)):
                state.bind(params[i][1], passed_values[i])
        if fun[2]:
            res, ret = fun[2].evaluate(state)
            if ret == Evaluator.ReturnType.RETURN and type(res).__name__ != fun[0]:
                provided_type = type(res).__name__
                if provided_type == "NoneType":
                    provided_type = "void"
                raise Evaluator.EvaluatorException("INTERPRETATION ERROR: Return type of '{0}': {1}, provided {2} "
                                                   "instead".format(str(self.__identifier), fun[0], provided_type))
        else:
            res = None
            ret = Evaluator.ReturnType.CONTINUE
        state.exit_scope()
        return res, ret


class SingleExpression(Expression):
    def __init__(self, expression: Expression):
        self.__expression = expression

    def pretty(self, pretty_builder, outer_precedence: int = None, opposite: bool = None) -> None:
        if outer_precedence is None and opposite is None:
            self.pretty(pretty_builder, 0, False)
            return
        self.__expression.pretty(pretty_builder, 0, False)
        pretty_builder.append(";")

    def prepass(self, prepass: PrepassState = None):
        if prepass is None:
            self.prepass(PrepassState())
            return
        self.__expression.prepass(prepass)

    def evaluate(self, state: EvaluationState = None):
        if state is None:
            return self.evaluate(EvaluationState())
        res, ret = self.__expression.evaluate(state)
        return res, ret
