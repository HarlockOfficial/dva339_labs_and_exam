from abc import ABC, abstractmethod
from typing import List, Union, Tuple

from AbstractSyntax import Expression
import Evaluator
import TypeChecker


class Statement(ABC):
    def __init__(self, line: int = None, column: int = None):
        self.__line = line
        self.__column = column

    def get_line(self):
        return self.__line

    def get_column(self):
        return self.__column

    def evaluatorException(self, msg: str):
        if self.__line is not None:
            msg += " on line: " + str(self.__line)
            if self.__column is not None:
                msg += " column: " + str(self.__column)
        raise Evaluator.EvaluatorException(msg)

    def typecheckException(self, msg: str):
        if self.__line is not None:
            msg += " on line: " + str(self.__line)
            if self.__column is not None:
                msg += " column: " + str(self.__column)
        raise TypeChecker.TypecheckerException(msg)

    @abstractmethod
    def typecheck(self, state: "TypeChecker.TypecheckingState" = None) -> TypeChecker.Types:
        if state is None:
            return self.typecheck(TypeChecker.TypecheckingState())

    @abstractmethod
    def evaluate(self, state: Evaluator.EvaluationState = None):
        if state is None:
            return self.evaluate(Evaluator.EvaluationState())

    @abstractmethod
    def prepass(self, prepass: Evaluator.PrepassState = None):
        if prepass is None:
            self.prepass(Evaluator.PrepassState())
            return

    @abstractmethod
    def pretty(self, pretty_builder, outer_precedence: int = None, opposite: bool = None) -> None:
        pass

    def __str__(self):
        from PrettyPrinter import PrettyBuilder
        builder = PrettyBuilder()
        self.pretty(builder)
        return str(builder)


class IdentifierList(Statement):
    def __init__(self, line: int, column: int, identifier_type: str, identifier: Expression,
                 next_identifier: "IdentifierList" = None):
        super().__init__(line, column)
        self.__identifier_type = identifier_type
        self.__identifier = identifier
        self.__next = next_identifier

    def pretty(self, pretty_builder, outer_precedence: int = None, opposite: bool = None) -> None:
        if outer_precedence is None and opposite is None:
            return self.pretty(pretty_builder, 1, False)
        pretty_builder.append(self.__identifier_type)
        pretty_builder.append(" ")
        self.__identifier.pretty(pretty_builder, 1, False)
        if self.__next is not None:
            pretty_builder.append(", ")
            self.__next.pretty(pretty_builder, 1, False)

    def prepass(self, prepass: Evaluator.PrepassState = None):
        if prepass is None:
            self.prepass(Evaluator.PrepassState())
            return
        self.__identifier.prepass(prepass)
        if self.__next is not None:
            self.__next.prepass(prepass)

    def evaluate(self, state: Evaluator.Evaluator.EvaluationState = None):
        if state is None:
            self.evaluate(Evaluator.Evaluator.EvaluationState())
        if self.__next is None:
            val = [self.__identifier_type, str(self.__identifier)]
            return [val], Evaluator.ReturnType.CONTINUE
        val, ret = self.__next.evaluate(state)
        val2 = [self.__identifier_type, str(self.__identifier)]
        val.insert(0, val2)
        return val, Evaluator.ReturnType.CONTINUE

    def typecheck(self, state: "TypeChecker.TypecheckingState" = None) -> List[Tuple[TypeChecker.Types, str]]:
        if state is None:
            return self.typecheck(TypeChecker.TypecheckingState())
        if self.__next is None:
            val = TypeChecker.Types(self.__identifier_type)
            try:
                state.lookup_variable(str(self.__identifier))
                super().typecheckException(
                    "TYPECHECK ERROR: Variable {0} already defined".format(str(self.__identifier)))
            except TypeChecker.TypecheckingStateException:
                state.bind_variable(str(self.__identifier), val)
            val = (val, str(self.__identifier))
            return [val]
        val = self.__next.typecheck(state)
        val2 = TypeChecker.Types(self.__identifier_type)
        try:
            state.lookup_variable(str(self.__identifier))
            super().typecheckException("TYPECHECK ERROR: Variable {0} already defined".format(str(self.__identifier)))
        except TypeChecker.TypecheckingStateException:
            state.bind_variable(str(self.__identifier), val2)
        val2 = (val2, str(self.__identifier))
        val.insert(0, val2)
        return val


class FunctionDeclaration(Statement):
    def __init__(self, line: int, column: int, return_type: str, identifier: Expression, params: IdentifierList = None,
                 body: Statement = None):
        super().__init__(line, column)
        self.__return_type = return_type
        self.__identifier = identifier
        self.__params = params
        self.__body = body

    def pretty(self, pretty_builder, outer_precedence: int = None, opposite: bool = None) -> None:
        if outer_precedence is None and opposite is None:
            return self.pretty(pretty_builder, 0, False)

        pretty_builder.append(self.__return_type)
        pretty_builder.append(" ")
        self.__identifier.pretty(pretty_builder, 0, False)
        pretty_builder.append("(")
        if self.__params is not None:
            self.__params.pretty(pretty_builder, 0, False)
        pretty_builder.append(") {")
        pretty_builder.indent()
        pretty_builder.new_line()
        if self.__body is not None:
            self.__body.pretty(pretty_builder, 0, False)
        pretty_builder.un_indent()
        pretty_builder.new_line()
        pretty_builder.append("}")
        pretty_builder.new_line()

    def prepass(self, prepass: Evaluator.PrepassState = None):
        if prepass is None:
            self.prepass(Evaluator.PrepassState())
            return
        self.__identifier.prepass(prepass)
        prepass.enter_scope()
        if self.__params is not None:
            self.__params.prepass(prepass)
        if self.__body is not None:
            prepass.enter_scope()
            self.__body.prepass(prepass)
            prepass.exit_scope()
        prepass.exit_scope()

    def evaluate(self, state: Evaluator.Evaluator.EvaluationState = None):
        if state is None:
            return self.evaluate(Evaluator.Evaluator.EvaluationState())
        if self.__params is None:
            self.__params = list()
        state.bind_function(str(self.__identifier), (self.__return_type, self.__params, self.__body))
        return None, Evaluator.ReturnType.CONTINUE

    def typecheck(self, state: "TypeChecker.TypecheckingState" = None) -> TypeChecker.Types:
        if state is None:
            return self.typecheck(TypeChecker.TypecheckingState())
        state.enter_scope()
        ret_type = TypeChecker.Types(self.__return_type)
        if self.__params is not None:
            self.__params = self.__params.typecheck(state)
        else:
            self.__params = list()
        try:
            state.lookup_function(str(self.__identifier))
            super().typecheckException("TYPECHECK EXCEPTION: Function with same name already declared")
        except TypeChecker.TypecheckingStateException:
            state.bind_function(str(self.__identifier), (ret_type, self.__params, self.__body, super().get_line(), super().get_column()))
        state.exit_scope()
        return ret_type


class SequenceStatement(Statement):
    def __init__(self, head: Statement, tail: Statement = None):
        super().__init__()
        self.__head = head
        self.__tail = tail

    def pretty(self, pretty_builder, outer_precedence: int = None, opposite: bool = None) -> None:
        if outer_precedence is None and opposite is None:
            return self.pretty(pretty_builder, 2, False)
        if self.__head is not None and self.__head != "":
            self.__head.pretty(pretty_builder, outer_precedence, opposite)
        if self.__tail is not None and self.__tail != "":
            if self.__head is not None and self.__head != "":
                pretty_builder.new_line()
            self.__tail.pretty(pretty_builder, outer_precedence, opposite)

    def prepass(self, prepass: Evaluator.PrepassState = None):
        if prepass is None:
            self.prepass(Evaluator.PrepassState())
            return
        self.__head.prepass(prepass)
        if self.__tail is not None and self.__tail != "":
            self.__tail.prepass(prepass)

    def evaluate(self, state: Evaluator.Evaluator.EvaluationState = None):
        if state is None:
            state = Evaluator.Evaluator.EvaluationState()
            self.evaluate(state)
            if not state.has_function("main"):
                super().evaluatorException("INTERPRETATION ERROR: Required function 'main' not found")
            main = state.lookup_function("main")
            if main[2]:
                val, ret = main[2].evaluate(state)
                provided_type = type(val).__name__
                if provided_type == "NoneType":
                    provided_type = "void"
                if ret == Evaluator.ReturnType.RETURN and provided_type != main[0]:
                    super().evaluatorException("INTERPRETATION ERROR: Return type of 'main': {0}, provided {1} "
                                               "instead".format(main[0], provided_type))
            return
        val, ret = self.__head.evaluate(state)
        if self.__tail is not None and self.__tail != "" and ret != Evaluator.ReturnType.RETURN:
            val, ret = self.__tail.evaluate(state)
        return val, ret

    def typecheck(self, state: "TypeChecker.TypecheckingState" = None) -> List[TypeChecker.Types]:
        if state is None:
            state = TypeChecker.TypecheckingState()
            self.typecheck(state)
            try:
                state.lookup_function("main")
            except TypeChecker.TypecheckingStateException as e:
                super().typecheckException(str(e))
            for key in state.get_all_functions():
                state.enter_scope()
                fun = state.lookup_function(key)
                state.set_current_function_name(key)
                ret_type = fun[0]
                for elem in fun[1]:
                    # elem_type = elem[0]
                    # elem_name = elem[1]
                    state.bind_variable(elem[1], elem[0])
                if fun[2] is not None:
                    body = fun[2].typecheck(state)
                if not body:
                    body = TypeChecker.Types.VOID
                if type(body) == list:
                    for ret in body:
                        if ret['return'] != ret_type:
                            super().typecheckException(
                                "TYPECHECK ERROR: Return type mismatch: function '{0}' should return {1}, "
                                "{2} returned instead on line {3} column {4}".format(key, ret_type.value, ret['return'].value, fun[3, fun[4]]))
                elif body != ret_type:
                    super().typecheckException(
                        "TYPECHECK ERROR: Return type mismatch: function '{0}' should return {1}, "
                        "{2} returned instead on line {3} column {4}".format(key, ret_type.value, body.value, fun[3], fun[4]))
                state.exit_scope()
            return True
        ret = list()
        res = self.__head.typecheck(state)
        if type(res) == dict and type(ret) != list:
            ret = list()
            ret.append(res)
        elif type(res) == dict and type(ret) == list:
            ret.append(res)
        elif type(res) == list and type(ret) != list:
            ret = res
        elif type(res) == list and type(ret) == list:
            for x in res:
                ret.append(x)
        if self.__tail is not None and self.__tail != "":
            res = self.__tail.typecheck(state)
            if type(res) == dict and type(ret) != list:
                ret = list()
                ret.append(res)
            elif type(res) == dict and type(ret) == list:
                ret.append(res)
            elif type(res) == list and type(ret) != list:
                ret = res
            elif type(res) == list and type(ret) == list:
                for x in res:
                    ret.append(x)
        return ret


class AssignmentStatement(Statement):
    def __init__(self, line: int, column: int, identifier: Expression, expr: Expression):
        super().__init__(line, column)
        self.__identifier = identifier
        self.__expr = expr

    def pretty(self, pretty_builder, outer_precedence: int = None, opposite: bool = None) -> None:
        if outer_precedence is None and opposite is None:
            return self.pretty(pretty_builder, 0, False)
        self.__identifier.pretty(pretty_builder, 0, False)
        pretty_builder.append(" = ")
        self.__expr.pretty(pretty_builder, 2, False)

    def prepass(self, prepass: Evaluator.PrepassState = None):
        if prepass is None:
            self.prepass(Evaluator.PrepassState())
            return
        self.__expr.prepass(prepass)
        self.__identifier.prepass(prepass)

    def evaluate(self, state: Evaluator.Evaluator.EvaluationState = None):
        if state is None:
            return self.evaluate(Evaluator.Evaluator.EvaluationState())
        val, ret = self.__expr.evaluate(state)
        if val is None:
            super().evaluatorException("INTERPRETATION ERROR: Expected value got void")
        current_val = state.lookup(str(self.__identifier))
        if type(current_val) != type(val):
            super().evaluatorException("INTERPRETATION ERROR: Expected {0} got {1} instead".format(
                type(current_val).__name__, type(val).__name__))
        state.bind(str(self.__identifier), val)
        return val, Evaluator.ReturnType.CONTINUE

    def typecheck(self, state: "TypeChecker.TypecheckingState" = None) -> TypeChecker.Types:
        if state is None:
            return self.typecheck(TypeChecker.TypecheckingState())
        val = self.__expr.typecheck(state)
        try:
            var_type = state.lookup_variable(str(self.__identifier))
            if var_type != val:
                super().typecheckException("TYPECHECK ERROR: Expected {0} got {1}".format(var_type.value, val.value))
            return var_type
        except TypeChecker.TypecheckingStateException as e:
            super().typecheckException(str(e))


class BlockStatement(Statement):
    def __init__(self, line: int, column: int, statement: Statement):
        super().__init__(line, column)
        self.__statement = statement

    def pretty(self, pretty_builder, outer_precedence: int = None, opposite: bool = None) -> None:
        if outer_precedence is None and opposite is None:
            return self.pretty(pretty_builder, 0, False)
        pretty_builder.append(" {")
        pretty_builder.indent()
        pretty_builder.new_line()
        if self.__statement is not None:
            self.__statement.pretty(pretty_builder, 0, False)
        pretty_builder.un_indent()
        pretty_builder.new_line()
        pretty_builder.append("}")

    def prepass(self, prepass: Evaluator.PrepassState = None):
        if prepass is None:
            self.prepass(Evaluator.PrepassState())
            return
        if self.__statement is not None:
            prepass.enter_scope()
            self.__statement.prepass(prepass)
            prepass.exit_scope()

    def evaluate(self, state: Evaluator.Evaluator.EvaluationState = None):
        if state is None:
            return self.evaluate(Evaluator.Evaluator.EvaluationState())
        if self.__statement is not None:
            val, ret = self.__statement.evaluate(state)
            return val, ret
        return None, Evaluator.ReturnType.CONTINUE

    def typecheck(self, state: "TypeChecker.TypecheckingState" = None) -> TypeChecker.Types:
        if state is None:
            return self.typecheck(TypeChecker.TypecheckingState())
        if self.__statement is not None:
            state.enter_scope()
            val = self.__statement.typecheck(state)
            state.exit_scope()
            return val
        return TypeChecker.Types.VOID


class IfStatement(Statement):
    def __init__(self, line: int, column: int, expression: Expression, statement: SequenceStatement,
                 else_statement: SequenceStatement = None):
        super().__init__(line, column)
        self.__expression = expression
        self.__statement = statement
        self.__else_statement = else_statement

    def pretty(self, pretty_builder, outer_precedence: int = None, opposite: bool = None) -> None:
        if outer_precedence is None and opposite is None:
            return self.pretty(pretty_builder, 0, False)
        pretty_builder.append("if (")
        self.__expression.pretty(pretty_builder, 0, False)
        pretty_builder.append(")")
        self.__statement.pretty(pretty_builder, 0, False)
        if self.__else_statement is not None:
            pretty_builder.new_line()
            pretty_builder.append("else ")
            self.__else_statement.pretty(pretty_builder, 0, False)

    def prepass(self, prepass: Evaluator.PrepassState = None):
        if prepass is None:
            self.prepass(Evaluator.PrepassState())
            return
        self.__expression.prepass(prepass)
        self.__statement.prepass(prepass)
        if self.__else_statement is not None:
            self.__else_statement.prepass(prepass)

    def evaluate(self, state: Evaluator.Evaluator.EvaluationState = None):
        if state is None:
            return self.evaluate(Evaluator.Evaluator.EvaluationState())
        val, ret = self.__expression.evaluate(state)
        if type(val) is not bool:
            super().evaluatorException("INTERPRETATION ERROR: Expected boolean condition got {0}".format(type(val)))
        res = None
        ret = Evaluator.ReturnType.CONTINUE
        if val:
            if self.__statement is not None:
                res, ret = self.__statement.evaluate(state)
        elif self.__else_statement is not None and ret != Evaluator.ReturnType.RETURN:
            res, ret = self.__else_statement.evaluate(state)
        return res, ret

    def typecheck(self, state: "TypeChecker.TypecheckingState" = None) -> Union[TypeChecker.Types, List[dict]]:
        if state is None:
            return self.typecheck(TypeChecker.TypecheckingState())
        val = self.__expression.typecheck(state)
        if val != TypeChecker.Types.BOOL:
            super().typecheckException("TYPECHECK ERROR: Expected boolean condition got {0}".format(val.value))
        ret = None
        if self.__statement is not None:
            res = self.__statement.typecheck(state)
            if type(res) == dict and type(ret) != list:
                ret = list()
                ret.append(res)
            elif type(res) == dict and type(ret) == list:
                ret.append(res)
            elif type(res) == list and type(ret) != list:
                ret = res
            elif type(res) == list and type(ret) == list:
                for x in res:
                    ret.append(x)
        if self.__else_statement is not None:
            res = self.__else_statement.typecheck(state)
            if type(res) == dict and type(ret) != list:
                ret = list()
                ret.append(res)
            elif type(res) == dict and type(ret) == list:
                ret.append(res)
            elif type(res) == list and type(ret) != list:
                ret = res
            elif type(res) == list and type(ret) == list:
                for x in res:
                    ret.append(x)
        if ret is None:
            ret = TypeChecker.Types.VOID
        return ret


class WhileStatement(Statement):
    def __init__(self, line: int, column: int, expression: Expression, body: Statement):
        super().__init__(line, column)
        self.__expression = expression
        self.__body = body

    def pretty(self, pretty_builder, outer_precedence: int = None, opposite: bool = None) -> None:
        if outer_precedence is None and opposite is None:
            return self.pretty(pretty_builder, 0, False)
        pretty_builder.append("while (")
        self.__expression.pretty(pretty_builder, 0, False)
        pretty_builder.append(")")
        if self.__body is not None:
            self.__body.pretty(pretty_builder, 0, False)

    def prepass(self, prepass: Evaluator.PrepassState = None):
        if prepass is None:
            self.prepass(Evaluator.PrepassState())
            return
        self.__expression.prepass(prepass)
        self.__body.prepass(prepass)

    def evaluate(self, state: Evaluator.Evaluator.EvaluationState = None):
        if state is None:
            return self.evaluate(Evaluator.Evaluator.EvaluationState())
        res = None
        while True:
            expr, ret = self.__expression.evaluate(state)
            if type(expr) is not bool:
                super().evaluatorException("INTERPRETATION ERROR: Expected boolean condition got {0}"
                                           .format(type(expr)))
            if expr:
                result, ret = self.__body.evaluate(state)
                if result is not None:
                    if res is None:
                        res = list()
                    res.append(result)
                if ret != Evaluator.ReturnType.RETURN:
                    continue
            return res, ret

    def typecheck(self, state: "TypeChecker.TypecheckingState" = None) -> TypeChecker.Types:
        if state is None:
            return self.typecheck(TypeChecker.TypecheckingState())
        val = self.__expression.typecheck(state)
        if val != TypeChecker.Types.BOOL:
            super().typecheckException("TYPECHECK ERROR: Expected boolean condition got {0}".format(val.value))
        ret = None
        if self.__body is not None:
            res = self.__body.typecheck(state)
            if type(res) == dict and type(ret) != list:
                ret = list()
                ret.append(res)
            elif type(res) == dict and type(ret) == list:
                ret.append(res)
            elif type(res) == list and type(ret) != list:
                ret = res
            elif type(res) == list and type(ret) == list:
                for x in res:
                    ret.append(x)
        if ret is None:
            ret = TypeChecker.Types.VOID
        return ret


class ReturnStatement(Statement):
    def __init__(self, line: int, column: int, expression: Expression = None):
        super().__init__(line, column)
        self.__expression = expression
        self.__expected_return_type = None

    def pretty(self, pretty_builder, outer_precedence: int = None, opposite: bool = None) -> None:
        if outer_precedence is None and opposite is None:
            return self.pretty(pretty_builder, 0, False)
        pretty_builder.append("return")
        if self.__expression is not None:
            pretty_builder.append(" ")
            self.__expression.pretty(pretty_builder, 0, False)
        pretty_builder.append(";")

    def prepass(self, prepass: Evaluator.PrepassState = None):
        if prepass is None:
            self.prepass(Evaluator.PrepassState())
            return
        if self.__expression is not None:
            self.__expression.prepass(prepass)

    def evaluate(self, state: Evaluator.Evaluator.EvaluationState = None):
        if state is None:
            return self.evaluate(Evaluator.Evaluator.EvaluationState())
        if self.__expression is not None:
            val, ret = self.__expression.evaluate(state)
            return val, Evaluator.ReturnType.RETURN
        return None, Evaluator.ReturnType.RETURN

    def typecheck(self, state: "TypeChecker.TypecheckingState" = None) -> dict:
        if state is None:
            return self.typecheck(TypeChecker.TypecheckingState())
        ret = TypeChecker.Types.VOID
        if self.__expression is not None:
            ret = self.__expression.typecheck(state)
        self.__expected_return_type = state.lookup_function(state.get_current_function_name())[0]
        if ret != self.__expected_return_type:
            super().typecheckException("TYPECHECK ERROR: Return type missmatch, expected {0} got {1}".format(self.__expected_return_type.value, ret.value))
        return {"type": ret, "return": ret}


class DefinitionStatement(Statement):
    def __init__(self, line: int, column: int, variable_type: str, identifier: Expression):
        super().__init__(line, column)
        self.__variable_type = variable_type
        self.__identifier = identifier

    def pretty(self, pretty_builder, outer_precedence: int = None, opposite: bool = None) -> None:
        if outer_precedence is None and opposite is None:
            return self.pretty(pretty_builder, 2, False)
        pretty_builder.append(self.__variable_type)
        pretty_builder.append(" ")
        self.__identifier.pretty(pretty_builder, 2, False)
        pretty_builder.append(";")

    def prepass(self, prepass: Evaluator.PrepassState = None):
        if prepass is None:
            self.prepass(Evaluator.PrepassState())
            return
        prepass.bind(str(self.__identifier))
        self.__identifier.prepass(prepass)

    def evaluate(self, state: Evaluator.EvaluationState = None):
        if self.__variable_type == "int":
            val = 0
        else:
            val = False
        state.bind(str(self.__identifier), val)
        val, ret = self.__identifier.evaluate(state)
        return val, Evaluator.ReturnType.CONTINUE

    def typecheck(self, state: "TypeChecker.TypecheckingState" = None) -> TypeChecker.Types:
        if state is None:
            return self.typecheck(TypeChecker.TypecheckingState())
        try:
            state.lookup_variable(str(self.__identifier))
            super().typecheckException(
                "TYPECHECK ERROR: Variable '{0}' already declared".format(str(self.__identifier)))
        except TypeChecker.TypecheckingStateException:
            state.bind_variable(str(self.__identifier), TypeChecker.Types(self.__variable_type))
        return TypeChecker.Types(self.__variable_type)
