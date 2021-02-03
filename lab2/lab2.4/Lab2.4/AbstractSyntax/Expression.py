from abc import ABC, abstractmethod
from typing import List

import Evaluator
from Evaluator import PrepassState, EvaluationState, EvaluatorException
from Parser.Type import BinaryOperatorType, UnaryOperatorType
import TypeChecker


class Expression(ABC):
    def __init__(self, line: int = None, column: int = None):
        self.__line = line
        self.__column = column

    def evaluatorException(self, msg: str):
        if self.__line is not None:
            msg += " on line: " + str(self.__line)
            if self.__column is not None:
                msg += " column: " + str(self.__column)
        raise EvaluatorException(msg)

    def typecheckException(self, msg: str):
        if self.__line is not None:
            msg += " on line: " + str(self.__line)
            if self.__column is not None:
                msg += " column: " + str(self.__column)
        raise TypeChecker.TypecheckerException(msg)

    @abstractmethod
    def typecheck(self, state: TypeChecker.TypecheckingState = None) -> TypeChecker.Types:
        if state is None:
            return self.typecheck(TypeChecker.TypecheckingState())

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
    def __init__(self, line: int, column: int, identifier: str):
        super().__init__(line, column)
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
            super().evaluatorException("INTERPRETATION ERROR: undeclared variable")
        return state.lookup(str(self.__identifier)), Evaluator.ReturnType.CONTINUE

    def typecheck(self, state: TypeChecker.TypecheckingState = None) -> TypeChecker.Types:
        if state is None:
            return self.typecheck(TypeChecker.TypecheckingState())
        try:
            return state.lookup_variable(str(self.__identifier))
        except TypeChecker.TypecheckingStateException as e:
            super().typecheckException(str(e))


class NumberExpression(Expression):
    def __init__(self, line: int, column: int, num: int):
        super().__init__(line, column)
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
        if type(self.__num) != int:
            super().evaluatorException("INTERPRETATION ERROR: expected integer value got {0}".format(self.__num))
        return int(self.__num), Evaluator.ReturnType.CONTINUE

    def typecheck(self, state: TypeChecker.TypecheckingState = None) -> TypeChecker.Types:
        if state is None:
            return self.typecheck(TypeChecker.TypecheckingState())
        try:
            int(self.__num)
        except ValueError:
            super().typecheckException("INTERPRETATION ERROR: expected integer got {0}".format(self.__num))
        return TypeChecker.Types.INT


class BooleanExpression(Expression):
    def __init__(self, line: int, column: int, boolean: bool):
        super().__init__(line, column)
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
        super().evaluatorException("INTERPRETATION ERROR: expected boolean value got {0}".format(self.__boolean))

    def typecheck(self, state: TypeChecker.TypecheckingState = None) -> TypeChecker.Types:
        if state is None:
            return self.typecheck(TypeChecker.TypecheckingState())
        if self.__boolean != 'true' and self.__boolean != 'false':
            super().typecheckException("TYPECHECK ERROR: expected boolean got {0}".format(self.__boolean))
        return TypeChecker.Types.BOOL


class BinaryOperatorExpression(Expression):
    def __init__(self, line: int, column: int, bin_op_type: BinaryOperatorType, left: Expression, right: Expression):
        super().__init__(line, column)
        self.__bin_op_type = bin_op_type
        self.__left = left
        self.__right = right
        self.__expected_parameters_type = None

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
                super().evaluatorException("INTERPRETATION ERROR: Expected boolean got {0}".format(type(val1)))
            if val1:
                return True, Evaluator.ReturnType.CONTINUE
            if type(val2) is not bool:
                super().evaluatorException("INTERPRETATION ERROR: Expected boolean got {0}".format(type(val2)))
            return val2, Evaluator.ReturnType.CONTINUE
        if self.__bin_op_type == BinaryOperatorType.AND:
            if type(val1) is not bool:
                super().evaluatorException("INTERPRETATION ERROR: Expected boolean got {0}".format(type(val1)))
            if not val1:
                return False, Evaluator.ReturnType.CONTINUE
            if type(val2) is not bool:
                super().evaluatorException("INTERPRETATION ERROR: Expected boolean got {0}".format(type(val2)))
            return val1 and val2, Evaluator.ReturnType.CONTINUE
        if self.__bin_op_type == BinaryOperatorType.NOT_EQUALS:
            if type(val1) is not int:
                super().evaluatorException("INTERPRETATION ERROR: Expected integer got {0}".format(type(val1)))
            if type(val2) is not int:
                super().evaluatorException("INTERPRETATION ERROR: Expected integer got {0}".format(type(val2)))
            return val1 != val2, Evaluator.ReturnType.CONTINUE
        if self.__bin_op_type == BinaryOperatorType.LOWER_EQ:
            if type(val1) is not int:
                super().evaluatorException("INTERPRETATION ERROR: Expected integer got {0}".format(type(val1)))
            if type(val2) is not int:
                super().evaluatorException("INTERPRETATION ERROR: Expected integer got {0}".format(type(val2)))
            return val1 <= val2, Evaluator.ReturnType.CONTINUE
        if self.__bin_op_type == BinaryOperatorType.GREATER_EQUAL:
            if type(val1) is not int:
                super().evaluatorException("INTERPRETATION ERROR: Expected integer got {0}".format(type(val1)))
            if type(val2) is not int:
                super().evaluatorException("INTERPRETATION ERROR: Expected integer got {0}".format(type(val2)))
            return val1 >= val2, Evaluator.ReturnType.CONTINUE
        if self.__bin_op_type == BinaryOperatorType.LOWER:
            if type(val1) is not int:
                super().evaluatorException("INTERPRETATION ERROR: Expected integer got {0}".format(type(val1)))
            if type(val2) is not int:
                super().evaluatorException("INTERPRETATION ERROR: Expected integer got {0}".format(type(val2)))
            return val1 < val2, Evaluator.ReturnType.CONTINUE
        if self.__bin_op_type == BinaryOperatorType.GREATER:
            if type(val1) is not int:
                super().evaluatorException("INTERPRETATION ERROR: Expected integer got {0}".format(type(val1)))
            if type(val2) is not int:
                super().evaluatorException("INTERPRETATION ERROR: Expected integer got {0}".format(type(val2)))
            return val1 > val2, Evaluator.ReturnType.CONTINUE
        if self.__bin_op_type == BinaryOperatorType.PLUS:
            if type(val1) is not int:
                super().evaluatorException("INTERPRETATION ERROR: Expected integer got {0}".format(type(val1)))
            if type(val2) is not int:
                super().evaluatorException("INTERPRETATION ERROR: Expected integer got {0}".format(type(val2)))
            return val1 + val2, Evaluator.ReturnType.CONTINUE
        if self.__bin_op_type == BinaryOperatorType.MINUS:
            if type(val1) is not int:
                super().evaluatorException("INTERPRETATION ERROR: Expected integer got {0}".format(type(val1)))
            if type(val2) is not int:
                super().evaluatorException("INTERPRETATION ERROR: Expected integer got {0}".format(type(val2)))
            return val1 - val2, Evaluator.ReturnType.CONTINUE
        if self.__bin_op_type == BinaryOperatorType.MULTIPLY:
            if type(val1) is not int:
                super().evaluatorException("INTERPRETATION ERROR: Expected integer got {0}".format(type(val1)))
            if type(val2) is not int:
                super().evaluatorException("INTERPRETATION ERROR: Expected integer got {0}".format(type(val2)))
            return val1 * val2, Evaluator.ReturnType.CONTINUE
        if self.__bin_op_type == BinaryOperatorType.DIVIDE:
            if type(val1) is not int:
                super().evaluatorException("INTERPRETATION ERROR: Expected integer got {0}".format(type(val1)))
            if type(val2) is not int:
                super().evaluatorException("INTERPRETATION ERROR: Expected integer got {0}".format(type(val2)))
            return int(val1 / val2), Evaluator.ReturnType.CONTINUE
        if self.__bin_op_type == BinaryOperatorType.MODULUS:
            if type(val1) is not int:
                super().evaluatorException("INTERPRETATION ERROR: Expected integer got {0}".format(type(val1)))
            if type(val2) is not int:
                super().evaluatorException("INTERPRETATION ERROR: Expected integer got {0}".format(type(val2)))
            return int(val1 % val2), Evaluator.ReturnType.CONTINUE
        if self.__bin_op_type == BinaryOperatorType.EQUALS:
            if type(val1) is not int:
                super().evaluatorException("INTERPRETATION ERROR: Expected integer got {0}".format(type(val1)))
            if type(val2) is not int:
                super().evaluatorException("INTERPRETATION ERROR: Expected integer got {0}".format(type(val2)))
            return val1 == val2, Evaluator.ReturnType.CONTINUE
        super().evaluatorException("INTERPRETATION ERROR: Invalid binary operator expression")

    def typecheck(self, state: TypeChecker.TypecheckingState = None) -> TypeChecker.Types:
        if state is None:
            return self.typecheck(TypeChecker.TypecheckingState())
        val1 = self.__left.typecheck(state)
        val2 = self.__right.typecheck(state)

        if self.__bin_op_type == BinaryOperatorType.PLUS or self.__bin_op_type == BinaryOperatorType.MINUS or \
                self.__bin_op_type == BinaryOperatorType.MULTIPLY or self.__bin_op_type == BinaryOperatorType.DIVIDE or\
                self.__bin_op_type == BinaryOperatorType.MODULUS:
            self.__expected_parameters_type = TypeChecker.Types.INT
            if val1 != self.__expected_parameters_type:
                super().typecheckException("TYPECHECK ERROR: Expected integer type got {0}".format(val1.value))
            if val2 != self.__expected_parameters_type:
                super().typecheckException("TYPECHECK ERROR: Expected integer type got {0}".format(val2.value))
            return TypeChecker.Types.INT

        if self.__bin_op_type == BinaryOperatorType.GREATER or self.__bin_op_type == BinaryOperatorType.LOWER or \
                self.__bin_op_type == BinaryOperatorType.GREATER_EQUAL or \
                self.__bin_op_type == BinaryOperatorType.LOWER_EQ:
            self.__expected_parameters_type = TypeChecker.Types.INT
            if val1 != self.__expected_parameters_type:
                super().typecheckException("TYPECHECK ERROR: Expected integer type got {0}".format(val1.value))
            if val2 != self.__expected_parameters_type:
                super().typecheckException("TYPECHECK ERROR: Expected integer type got {0}".format(val2.value))
            return TypeChecker.Types.BOOL

        if self.__bin_op_type == BinaryOperatorType.AND or self.__bin_op_type == BinaryOperatorType.OR:
            self.__expected_parameters_type = TypeChecker.Types.BOOL
            if val1 != self.__expected_parameters_type:
                super().typecheckException("TYPECHECK ERROR: Expected boolean type got {0}".format(val1.value))
            if val2 != self.__expected_parameters_type:
                super().typecheckException("TYPECHECK ERROR: Expected boolean type got {0}".format(val2.value))
            return TypeChecker.Types.BOOL

        if self.__bin_op_type == BinaryOperatorType.EQUALS or self.__bin_op_type == BinaryOperatorType.NOT_EQUALS:
            if val1 != val2:
                super().typecheckException(
                    "TYPECHECK ERROR: Expected same type got {0} and {1}".format(val1.value, val2.value))
            self.__expected_parameters_type = val1
            return TypeChecker.Types.BOOL

        super().typecheckException("TYPECHECK ERROR: Unknown binary operator {0}".format(self.__bin_op_type.value))


class UnaryOperatorExpression(Expression):
    def __init__(self, line: int, column: int, unary_op_type: UnaryOperatorType, expression: Expression):
        super().__init__(line, column)
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
                super().evaluatorException("INTERPRETATION ERROR: Expected boolean got {0}".format(type(val)))
            return not val, Evaluator.ReturnType.CONTINUE
        if self.__unary_op_type == UnaryOperatorType.MINUS:
            if type(val) is not int:
                super().evaluatorException("INTERPRETATION ERROR: Expected integer got {0}".format(type(val)))
            return -val, Evaluator.ReturnType.CONTINUE
        super().evaluatorException("INTERPRETATION ERROR: Invalid unary operator expression")

    def typecheck(self, state: TypeChecker.TypecheckingState = None) -> TypeChecker.Types:
        if state is None:
            return self.typecheck(TypeChecker.TypecheckingState())
        val = self.__expression.typecheck(state)
        if self.__unary_op_type == UnaryOperatorType.NOT:
            if val != TypeChecker.Types.BOOL:
                super().typecheckException("TYPECHECK ERROR: Expected boolean type got {0}".format(val.value))
            return TypeChecker.Types.BOOL
        if self.__unary_op_type == UnaryOperatorType.MINUS:
            if val != TypeChecker.Types.INT:
                super().typecheckException("TYPECHECK ERROR: Expected integer type got {0}".format(val.value))
            return TypeChecker.Types.INT
        super().typecheckException("TYPECHECK ERROR: Unknown unary operator {0}".format(self.__unary_op_type.value))


class SeparatorExpression(Expression):
    def __init__(self, actual_expression: Expression, next_expression: "SeparatorExpression" = None):
        super().__init__()
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

    def typecheck(self, state: TypeChecker.TypecheckingState = None) -> List[TypeChecker.Types]:
        if state is None:
            return self.typecheck(TypeChecker.TypecheckingState())
        if self.__next_expression is None:
            val = self.__current_expression.typecheck(state)
            return [val]
        val = self.__next_expression.typecheck(state)
        val2 = self.__current_expression.typecheck(state)
        val.insert(0, val2)
        return val


class BlockExpression(Expression):
    def __init__(self, line: int, column: int, expression: SeparatorExpression):
        super().__init__(line, column)
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

    def typecheck(self, state: TypeChecker.TypecheckingState = None) -> List[TypeChecker.Types]:
        if state is None:
            return self.typecheck(TypeChecker.TypecheckingState())
        if self.__expression is not None:
            return self.__expression.typecheck(state)
        return []


class FunctionCallExpression(Expression):
    def __init__(self, line: int, column: int, identifier: IdentifierExpression, expression: BlockExpression):
        super().__init__(line, column)
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
            super().evaluatorException("INTERPRETATION ERROR: Undefined function {0}".format(str(self.__identifier)))
        fun = state.lookup_function(str(self.__identifier))
        params = fun[1]
        if params:
            params, ret = params.evaluate(state)
        passed_values, ret = self.__expression.evaluate(state)
        if (params is not None and passed_values is None) or (params is None and passed_values is not None) or \
                (params is not None and passed_values is not None and len(params) != len(passed_values)):
            super().evaluatorException("INTERPRETATION ERROR: number of parameters not valid")
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
                super().evaluatorException("INTERPRETATION ERROR: Return type of '{0}': {1}, provided {2} "
                                           "instead".format(str(self.__identifier), fun[0], provided_type))
        else:
            res = None
            ret = Evaluator.ReturnType.CONTINUE
        state.exit_scope()
        return res, ret

    def typecheck(self, state: TypeChecker.TypecheckingState = None) -> TypeChecker.Types:
        if state is None:
            return self.typecheck(TypeChecker.TypecheckingState())
        if str(self.__identifier) == "print":
            self.__expression.typecheck(state)
            return TypeChecker.Types.VOID
        try:
            # funct[0] == ret_Type; funct[1] == list(params_type)
            funct = state.lookup_function(str(self.__identifier))
            # args_type == list(types)
            args_type = self.__expression.typecheck(state)
            if len(funct[1]) != len(args_type):
                super().typecheckException("TYPECHECK ERROR: Parameters quantity mismatch")
            for i in range(len(funct[1])):
                if funct[1][i][0] != args_type[i]:
                    super().typecheckException("TYPECHECK ERROR: Parameter type mismatch")
            return funct[0]
        except TypeChecker.TypecheckingStateException as e:
            super().typecheckException(str(e))


class SingleExpression(Expression):
    def __init__(self, line: int, column: int, expression: Expression):
        super().__init__(line, column)
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

    def typecheck(self, state: TypeChecker.TypecheckingState = None) -> TypeChecker.Types:
        if state is None:
            return self.typecheck(TypeChecker.TypecheckingState())
        return self.__expression.typecheck(state)
