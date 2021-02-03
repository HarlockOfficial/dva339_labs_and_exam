from abc import ABC, abstractmethod
from typing import List, Tuple, Union

import Evaluator
import TypeChecker
import Generator
from Evaluator import PrepassState, EvaluationState, EvaluatorException
from Parser.Type import BinaryOperatorType, UnaryOperatorType
import Optimizer
import AbstractSyntax


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

    def get_line(self):
        return self.__line

    def get_column(self):
        return self.__column

    @abstractmethod
    def optimize(self, state: "Optimizer.OptimizerState") -> Union["Expression", "AbstractSyntax.Statement"]:
        pass

    @abstractmethod
    def compile(self, state: "Generator.GeneratorState", program: "Generator.Trac42Program"):
        pass

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
        self.__type = None

    def pretty(self, pretty_builder, outer_precedence: int = None, opposite: bool = None) -> None:
        # precedence 4, not really necessary, just appends the identifier string
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
            self.__type = state.lookup_variable(str(self.__identifier))
            return self.__type
        except TypeChecker.TypecheckingStateException as e:
            super().typecheckException(str(e))

    def compile(self, state: "Generator.GeneratorState", program: "Generator.Trac42Program"):
        state.is_return_last_function = False
        position = state.lookup(str(self.__identifier))
        if self.__type == TypeChecker.Types.INT:
            program.emit(Generator.Instruction(Generator.OpCode.RVALINT, argument=position))
        elif self.__type == TypeChecker.Types.BOOL:
            program.emit(Generator.Instruction(Generator.OpCode.RVALBOOL, argument=position))
        else:
            raise Exception("Impossible type {0} expected int or bool".format(self.__type))
        return self.__type

    def contains(self, identifier: str, unused: bool = False):
        return identifier == self.__identifier

    def optimize(self, state: "Optimizer.OptimizerState") -> Union["Expression", "AbstractSyntax.Statement"]:
        if state.is_del_variable(self.__identifier):
            if self.__type == TypeChecker.Types.INT:
                return NumberExpression(super().get_line(), super().get_column(), 0)
            else:
                return BooleanExpression(super().get_line(), super().get_column(), False)
        try:
            var = state.lookup_constant(self.__identifier)
            if type(var) == int:
                return NumberExpression(super().get_line(), super().get_column(), var)
            else:
                if var:
                    return BooleanExpression(super().get_line(), super().get_column(), "true")
                return BooleanExpression(super().get_line(), super().get_column(), "false")
        except Optimizer.OptimizerStateException:
            pass
        return self


class NumberExpression(Expression):
    def __init__(self, line: int, column: int, num: int):
        super().__init__(line, column)
        self.__num = num

    def pretty(self, pretty_builder, outer_precedence: int = None, opposite: bool = None) -> None:
        # precedence 4, not really necessary, just appends a value
        pretty_builder.append(str(self.__num))

    def prepass(self, prepass: PrepassState = None):
        pass

    def evaluate(self, state: EvaluationState = None):
        if state is None:
            return self.evaluate(EvaluationState())
        try:
            return int(self.__num), Evaluator.ReturnType.CONTINUE
        except ValueError:
            super().evaluatorException("INTERPRETATION ERROR: expected integer value got {0}".format(self.__num))

    def typecheck(self, state: TypeChecker.TypecheckingState = None) -> TypeChecker.Types:
        if state is None:
            return self.typecheck(TypeChecker.TypecheckingState())
        try:
            int(self.__num)
        except ValueError:
            super().typecheckException("INTERPRETATION ERROR: expected integer got {0}".format(self.__num))
        return TypeChecker.Types.INT

    def compile(self, state: "Generator.GeneratorState", program: "Generator.Trac42Program"):
        state.is_return_last_function = False
        program.emit(Generator.Instruction(Generator.OpCode.PUSHINT, argument=int(self.__num)))
        return TypeChecker.Types.INT

    # nothing to do in number expression
    def optimize(self, state: "Optimizer.OptimizerState") -> Union["Expression", "AbstractSyntax.Statement"]:
        return self


class BooleanExpression(Expression):
    def __init__(self, line: int, column: int, boolean: str):
        super().__init__(line, column)
        self.__boolean = boolean

    def pretty(self, pretty_builder, outer_precedence: int = None, opposite: bool = None) -> None:
        # precedence 4, not really necessary, just appends a value
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

    def compile(self, state: "Generator.GeneratorState", program: "Generator.Trac42Program"):
        state.is_return_last_function = False
        if self.__boolean != "true" and self.__boolean != "false":
            raise Exception("Impossible already checked by typechecker")
        program.emit(Generator.Instruction(Generator.OpCode.PUSHBOOL, argument=self.__boolean))
        return TypeChecker.Types.BOOL

    # nothing to do in boolean expression
    def optimize(self, state: "Optimizer.OptimizerState") -> Union["Expression", "AbstractSyntax.Statement"]:
        return self


class BinaryOperatorExpression(Expression):
    def __init__(self, line: int, column: int, bin_op_type: BinaryOperatorType, left: Expression, right: Expression):
        super().__init__(line, column)
        self.__bin_op_type = bin_op_type
        self.__left = left
        self.__right = right
        self.__expected_parameters_type = None
        self.__identifier_to_save = list()

    def pretty(self, pretty_builder, outer_precedence: int = None, opposite: bool = None) -> None:
        if outer_precedence is None and opposite is None:
            self.pretty(pretty_builder, 4, False)
            return
        # ordered list containing all binary operators in order of precedence
        operators_precedence = [
            (BinaryOperatorType.OR,),
            (BinaryOperatorType.AND,),
            (BinaryOperatorType.EQUALS, BinaryOperatorType.NOT_EQUALS),
            (BinaryOperatorType.LOWER, BinaryOperatorType.GREATER,
             BinaryOperatorType.LOWER_EQ, BinaryOperatorType.GREATER_EQUAL),
            (BinaryOperatorType.PLUS, BinaryOperatorType.MINUS),
            (BinaryOperatorType.MULTIPLY, BinaryOperatorType.DIVIDE, BinaryOperatorType.MODULUS)
        ]
        precedence = -1
        for i in range(len(operators_precedence)):
            for operator in operators_precedence[i]:
                if self.__bin_op_type == operator:
                    precedence = 4 + i + 1
                    break
            if precedence != -1:
                break
        if precedence == -1:  # impossible
            print("Unknown operator error")
            exit(-3)
        if outer_precedence > precedence or (opposite and outer_precedence == precedence):
            pretty_builder.append("(")
        # (associativity == right) -> False (associativity always left in these binary operators)
        self.__left.pretty(pretty_builder, precedence, False)
        pretty_builder.append(" " + str(self.__bin_op_type.value) + " ")
        # (associativity == left) -> True (associativity always left in these binary operators)
        self.__right.pretty(pretty_builder, precedence, True)
        if outer_precedence > precedence or (opposite and outer_precedence == precedence):
            pretty_builder.append(")")

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
                self.__bin_op_type == BinaryOperatorType.MULTIPLY or self.__bin_op_type == BinaryOperatorType.DIVIDE \
                or self.__bin_op_type == BinaryOperatorType.MODULUS:
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

    def compile(self, state: "Generator.GeneratorState", program: "Generator.Trac42Program"):
        state.is_return_last_function = False
        if self.__bin_op_type == BinaryOperatorType.MODULUS:
            self.__left.compile(state, program)
        self.__left.compile(state, program)
        self.__right.compile(state, program)
        if self.__bin_op_type == BinaryOperatorType.OR:
            program.emit(Generator.Instruction(Generator.OpCode.OR))
        elif self.__bin_op_type == BinaryOperatorType.AND:
            program.emit(Generator.Instruction(Generator.OpCode.AND))
        elif self.__bin_op_type == BinaryOperatorType.NOT_EQUALS:
            if self.__expected_parameters_type == TypeChecker.Types.INT:
                program.emit(Generator.Instruction(Generator.OpCode.EQINT))
            elif self.__expected_parameters_type == TypeChecker.Types.BOOL:
                program.emit(Generator.Instruction(Generator.OpCode.EQBOOL))
            else:
                raise Exception("Expected parameters for not equal is {0} expected int or bool"
                                .format(self.__expected_parameters_type))
            program.emit(Generator.Instruction(Generator.OpCode.NOT))
        elif self.__bin_op_type == BinaryOperatorType.LOWER_EQ:
            program.emit(Generator.Instruction(Generator.OpCode.LEINT))
        elif self.__bin_op_type == BinaryOperatorType.GREATER_EQUAL:
            program.emit(Generator.Instruction(Generator.OpCode.LTINT))
            program.emit(Generator.Instruction(Generator.OpCode.NOT))
        elif self.__bin_op_type == BinaryOperatorType.LOWER:
            program.emit(Generator.Instruction(Generator.OpCode.LTINT))
        elif self.__bin_op_type == BinaryOperatorType.GREATER:
            program.emit(Generator.Instruction(Generator.OpCode.LEINT))
            program.emit(Generator.Instruction(Generator.OpCode.NOT))
        elif self.__bin_op_type == BinaryOperatorType.PLUS:
            program.emit(Generator.Instruction(Generator.OpCode.ADD))
        elif self.__bin_op_type == BinaryOperatorType.MINUS:
            program.emit(Generator.Instruction(Generator.OpCode.SUB))
        elif self.__bin_op_type == BinaryOperatorType.MULTIPLY:
            program.emit(Generator.Instruction(Generator.OpCode.MULT))
        elif self.__bin_op_type == BinaryOperatorType.DIVIDE:
            program.emit(Generator.Instruction(Generator.OpCode.DIV))
        elif self.__bin_op_type == BinaryOperatorType.MODULUS:
            program.emit(Generator.Instruction(Generator.OpCode.DIV))
            self.__right.compile(state, program)
            program.emit(Generator.Instruction(Generator.OpCode.MULT))
            program.emit(Generator.Instruction(Generator.OpCode.SUB))
        elif self.__bin_op_type == BinaryOperatorType.EQUALS:
            if self.__expected_parameters_type == TypeChecker.Types.INT:
                program.emit(Generator.Instruction(Generator.OpCode.EQINT))
            elif self.__expected_parameters_type == TypeChecker.Types.BOOL:
                program.emit(Generator.Instruction(Generator.OpCode.EQBOOL))
            else:
                raise Exception("Expected parameters for not equal is {0} expected int or bool"
                                .format(self.__expected_parameters_type))
        else:
            raise Exception("Unkenown operation {0}".format(self.__bin_op_type))
        return self.__expected_parameters_type

    def __optimize_left(self, state: "Optimizer.OptimizerState", expected_expression_type: type) -> Union[int, bool,
                                                                                                          None]:
        if type(self.__left) == expected_expression_type:
            ret, unused = self.__left.evaluate(None)
            return ret
        elif type(self.__left) == IdentifierExpression:
            try:
                return state.lookup_constant(str(self.__left))
            except Optimizer.OptimizerStateException:
                pass
        return None

    def __optimize_right(self, state: "Optimizer.OptimizerState", expected_expression_type: type) -> Union[int, bool,
                                                                                                           None]:
        if type(self.__right) == expected_expression_type:
            ret, unused = self.__right.evaluate(None)
            return ret
        elif type(self.__right) == IdentifierExpression:
            try:
                return state.lookup_constant(str(self.__right))
            except Optimizer.OptimizerStateException:
                pass
        return None

    def contains(self, identifier: str, to_save: bool = False):
        if hasattr(self.__left, "contains") and self.__left.contains(identifier):
            if "left" not in self.__identifier_to_save and to_save:
                    self.__identifier_to_save.append("left")
            return True
        if hasattr(self.__right, "contains") and self.__right.contains(identifier):
            if "right" not in self.__identifier_to_save and to_save:
                    self.__identifier_to_save.append("right")
            return True
        return False

    def optimize(self, state: "Optimizer.OptimizerState") -> Union["Expression", "AbstractSyntax.Statement"]:
        if type(self.__left) != IdentifierExpression or "left" not in self.__identifier_to_save:
            self.__left = self.__left.optimize(state)
        if type(self.__right != IdentifierExpression) or "right" not in self.__identifier_to_save:
            self.__right = self.__right.optimize(state)

        if self.__expected_parameters_type == TypeChecker.Types.INT:
            val1 = val2 = None
            if "left" not in self.__identifier_to_save:
                val1 = self.__optimize_left(state, NumberExpression)
            else:
                self.__identifier_to_save.remove("left")
            if "right" not in self.__identifier_to_save:
                val2 = self.__optimize_right(state, NumberExpression)
            else:
                self.__identifier_to_save.remove("right")
            if val1 == 0:
                if self.__bin_op_type in (BinaryOperatorType.PLUS, BinaryOperatorType.MINUS):
                    return self.__right
                if self.__bin_op_type in (BinaryOperatorType.MULTIPLY, BinaryOperatorType.DIVIDE, BinaryOperatorType.MODULUS):
                    return NumberExpression(super().get_line(), super().get_column(), 0)
            if val2 == 0:
                if self.__bin_op_type in (BinaryOperatorType.PLUS, BinaryOperatorType.MINUS):
                    return self.__left
                if self.__bin_op_type == BinaryOperatorType.MULTIPLY:
                    return NumberExpression(super().get_line(), super().get_column(), 0)
                if self.__bin_op_type in (BinaryOperatorType.DIVIDE, BinaryOperatorType.MODULUS):
                    state.add_warning("Optimization Warning: Division or Modulus by 0 found on line {0} column {1}"
                                      .format(super().get_line(), super().get_column()))

            if val1 is not None and val2 is not None:
                ret = eval(str(val1) + str(self.__bin_op_type.value) + str(val2))
                if type(ret) == bool:
                    if ret:
                        return BooleanExpression(-1, -1, "true")
                    return BooleanExpression(-1, -1, "false")
                else:
                    return NumberExpression(-1, -1, ret)
            return self
        else:
            val1 = val2 = None
            if "left" not in self.__identifier_to_save:
                val1 = self.__optimize_left(state, BooleanExpression)
            else:
                self.__identifier_to_save.remove("left")
            if "right" not in self.__identifier_to_save:
                val2 = self.__optimize_right(state, BooleanExpression)
            else:
                self.__identifier_to_save.remove("right")
            if val1 is not None and val1:
                if self.__bin_op_type == BinaryOperatorType.OR:
                    return BooleanExpression(super().get_line(), super().get_column(), True)
                if self.__bin_op_type == BinaryOperatorType.AND:
                    return self.__right
            if val2 is not None and val2:
                if self.__bin_op_type == BinaryOperatorType.OR:
                    return BooleanExpression(super().get_line(), super().get_column(), True)
                if self.__bin_op_type == BinaryOperatorType.AND:
                    return self.__left
            if val1 is not None and not val1:
                if self.__bin_op_type == BinaryOperatorType.OR:
                    return self.__right
                if self.__bin_op_type == BinaryOperatorType.AND:
                    return BooleanExpression(super().get_line(), super().get_column(), False)
            if val2 is not None and not val2:
                if self.__bin_op_type == BinaryOperatorType.OR:
                    return self.__left
                if self.__bin_op_type == BinaryOperatorType.AND:
                    return BooleanExpression(super().get_line(), super().get_column(), False)
            if val1 is not None and val2 is not None:
                operator = self.__bin_op_type.value
                if operator == "||":
                    operator = "or"
                elif operator == "&&":
                    operator = "and"
                ret = eval(str(val1) + " " + str(operator) + " " + str(val2))
                if ret:
                    return BooleanExpression(-1, -1, "true")
                return BooleanExpression(-1, -1, "false")
            return self


class UnaryOperatorExpression(Expression):
    def __init__(self, line: int, column: int, unary_op_type: UnaryOperatorType, expression: Expression):
        super().__init__(line, column)
        self.__unary_op_type = unary_op_type
        self.__expression = expression
        self.__expected_type = None

    def pretty(self, pretty_builder, outer_precedence: int = None, opposite: bool = None) -> None:
        if outer_precedence is None and opposite is None:
            self.pretty(pretty_builder, 4, False)
            return
        pretty_builder.append(self.__unary_op_type.value)
        if outer_precedence > 4 or (opposite and outer_precedence == 4):
            pretty_builder.append("(")
        # forcing non-associative unary operators '!' and '-' to be right associative
        self.__expression.pretty(pretty_builder, 4, True)
        if outer_precedence > 4 or (opposite and outer_precedence == 4):
            pretty_builder.append(")")

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
            self.__expected_type = TypeChecker.Types.BOOL
        if self.__unary_op_type == UnaryOperatorType.MINUS:
            if val != TypeChecker.Types.INT:
                super().typecheckException("TYPECHECK ERROR: Expected integer type got {0}".format(val.value))
            self.__expected_type = TypeChecker.Types.INT
        if self.__expected_type is None:
            super().typecheckException("TYPECHECK ERROR: Unknown unary operator {0}".format(self.__unary_op_type.value))
        return self.__expected_type

    def compile(self, state: "Generator.GeneratorState", program: "Generator.Trac42Program"):
        state.is_return_last_function = False
        self.__expression.compile(state, program)
        if self.__unary_op_type == UnaryOperatorType.NOT:
            program.emit(Generator.Instruction(Generator.OpCode.NOT))
        elif self.__unary_op_type == UnaryOperatorType.MINUS:
            program.emit(Generator.Instruction(Generator.OpCode.NEG))
        return self.__expected_type

    def is_equivalent(self, expr: Expression):
        return expr.evaluate()[0] == self.__expression

    def optimize(self, state: "Optimizer.OptimizerState") -> Union["Expression", "AbstractSyntax.Statement"]:
        if type(self.__expression) == IdentifierExpression:
            if state.is_del_variable(str(self.__expression)):
                self.__expression = self.__expression.optimize(state)
        else:
            self.__expression = self.__expression.optimize(state)
        if self.__expected_type == TypeChecker.Types.INT:
            if type(self.__expression) == NumberExpression:
                return NumberExpression(-1, -1, -self.__expression.evaluate(None))
            elif type(self.__expression) == IdentifierExpression:
                try:
                    return NumberExpression(-1, -1, -state.lookup(str(self.__expression)))
                except Optimizer.OptimizerStateException:
                    pass
            return self
        else:
            if type(self.__expression) == BooleanExpression:
                if not self.__expression.evaluate(None)[0]:
                    return BooleanExpression(-1, -1, "true")
                return BooleanExpression(-1, -1, "false")
            elif type(self.__expression) == IdentifierExpression and state.is_del_variable(str(self.__expression)):
                try:
                    if not state.lookup_constant(str(self.__expression)):
                        return BooleanExpression(-1, -1, "true")
                    return BooleanExpression(-1, -1, "false")
                except Optimizer.OptimizerStateException:
                    pass
            return self


class SeparatorExpression(Expression):
    def __init__(self, current_expression: Expression, next_expression: "SeparatorExpression" = None):
        super().__init__()
        self.__current_expression = current_expression
        self.__next_expression = next_expression

    def pretty(self, pretty_builder, outer_precedence: int = None, opposite: bool = None) -> None:
        if outer_precedence is None and opposite is None:
            self.pretty(pretty_builder, 5, False)
            return
        self.__current_expression.pretty(pretty_builder, 5, False)
        if self.__next_expression is not None:
            pretty_builder.append(", ")
            self.__next_expression.pretty(pretty_builder, 5, False)

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

    def compile(self, state: "Generator.GeneratorState", program: "Generator.Trac42Program") -> \
            Tuple[int, List[TypeChecker.Types]]:
        state.is_return_last_function = False
        val = 0
        type_list = list()
        if self.__next_expression is not None:
            val, type_list = self.__next_expression.compile(state, program)
        expr_type = self.__current_expression.compile(state, program)
        type_list.append(expr_type)
        return val + 1, type_list

    def optimize(self, state: "Optimizer.OptimizerState") -> Union["Expression", "AbstractSyntax.Statement"]:
        self.__current_expression = self.__current_expression.optimize(state)
        if self.__next_expression is not None:
            self.__next_expression = self.__next_expression.optimize(state)
        return self


class BlockExpression(Expression):
    def __init__(self, line: int, column: int, expression: SeparatorExpression):
        super().__init__(line, column)
        self.__expression = expression

    def pretty(self, pretty_builder, outer_precedence: int = None, opposite: bool = None) -> None:
        if outer_precedence is None and opposite is None:
            self.pretty(pretty_builder, 4, False)
            return
        if self.__expression is not None:
            self.__expression.pretty(pretty_builder, outer_precedence, False)

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

    def compile(self, state: "Generator.GeneratorState", program: "Generator.Trac42Program"):
        state.is_return_last_function = False
        if self.__expression is not None:
            return self.__expression.compile(state, program)
        return 0, list()

    def optimize(self, state: "Optimizer.OptimizerState") -> Union["Expression", "AbstractSyntax.Statement"]:
        self.__expression = self.__expression.optimize(state)
        return self


class FunctionCallExpression(Expression):
    def __init__(self, line: int, column: int, identifier: IdentifierExpression, expression: BlockExpression):
        super().__init__(line, column)
        self.__identifier = identifier
        self.__expression = expression
        self.__expected_return_type = None

    def pretty(self, pretty_builder, outer_precedence: int = None, opposite: bool = None) -> None:
        if outer_precedence is None and opposite is None:
            self.pretty(pretty_builder, 4, False)
            return
        # non necessary to pass outer_precedence and opposite, identifier doesn't care
        self.__identifier.pretty(pretty_builder, 4, False)
        pretty_builder.append(" (")
        self.__expression.pretty(pretty_builder, 4, False)
        pretty_builder.append(" );")

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
            self.__expected_return_type = TypeChecker.Types.VOID
            return self.__expected_return_type
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
            self.__expected_return_type = funct[0]
            return self.__expected_return_type
        except TypeChecker.TypecheckingStateException as e:
            super().typecheckException(str(e))

    def compile(self, state: "Generator.GeneratorState", program: "Generator.Trac42Program"):
        state.is_return_last_function = False
        if str(self.__identifier) == "print":
            unused, arguments_type = self.__expression.compile(state, program)
            for arg in reversed(arguments_type):
                if arg == TypeChecker.Types.INT:
                    program.emit(Generator.Instruction(Generator.OpCode.WRITEINT))
                elif arg == TypeChecker.Types.BOOL:
                    program.emit(Generator.Instruction(Generator.OpCode.WRITEBOOL))
                else:
                    raise Generator.CompilerException("print only accepts parameters of type int or bool, "
                                                      "{0} given".format(arg))
                # remove the parameter that was just printed
                program.emit(Generator.Instruction(Generator.OpCode.POP, 1))
            return self.__expected_return_type
        else:
            ret_type = state.get_ret_type(str(self.__identifier))
            if ret_type != TypeChecker.Types.VOID:
                # allocate space for return value
                program.emit(Generator.Instruction(Generator.OpCode.DECL, 1))
            # evaluate params in reverse order
            arguments_quantity, unused = self.__expression.compile(state, program)
            # call function
            program.emit(Generator.Instruction(Generator.OpCode.BSR, target=str(self.__identifier)))
            if arguments_quantity > 0:
                # remove all arguments
                program.emit(Generator.Instruction(Generator.OpCode.POP, argument=arguments_quantity))
            return self.__expected_return_type

    def optimize(self, state: "Optimizer.OptimizerState") -> Union["Expression", "AbstractSyntax.Statement"]:
        self.__expression = self.__expression.optimize(state)
        return self


class SingleExpression(Expression):
    def __init__(self, line: int, column: int, expression: Expression):
        super().__init__(line, column)
        self.__expression = expression

    def pretty(self, pretty_builder, outer_precedence: int = None, opposite: bool = None) -> None:
        if outer_precedence is None and opposite is None:
            self.pretty(pretty_builder, 3, False)
            return
        self.__expression.pretty(pretty_builder, outer_precedence, False)
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

    def compile(self, state: "Generator.GeneratorState", program: "Generator.Trac42Program"):
        state.is_return_last_function = False
        self.__expression.compile(state, program)

    def optimize(self, state: "Optimizer.OptimizerState") -> Union["Expression", "AbstractSyntax.Statement"]:
        self.__expression = self.__expression.optimize(state)
        if type(self.__expression) in (NumberExpression, BooleanExpression, type(None), IdentifierExpression):
            return AbstractSyntax.EmptyStatement()
        return self