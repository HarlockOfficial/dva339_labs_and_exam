from abc import ABC, abstractmethod
from typing import List, Union, Tuple, Any
import copy

import Evaluator
import TypeChecker
import AbstractSyntax
import Generator
import Optimizer


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
    def optimize(self, state: "Optimizer.OptimizerState") -> Union["Statement", "AbstractSyntax.Expression"]:
        pass

    @abstractmethod
    def compile(self, state: "Generator.GeneratorState", program: "Generator.Trac42Program"):
        pass

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
    def __init__(self, line: int, column: int, identifier_type: str, identifier: "AbstractSyntax.Expression",
                 next_identifier: "IdentifierList" = None):
        super().__init__(line, column)
        self.__identifier_type = identifier_type
        self.__identifier = identifier
        self.__next = next_identifier

    def pretty(self, pretty_builder, outer_precedence: int = None, opposite: bool = None) -> None:
        pretty_builder.append(self.__identifier_type)
        pretty_builder.append(" ")
        self.__identifier.pretty(pretty_builder, 2, False)
        if self.__next is not None:
            pretty_builder.append(", ")
            self.__next.pretty(pretty_builder, 2, False)

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

    # noinspection PyArgumentList
    def typecheck(self, state: "TypeChecker.TypecheckingState" = None) -> List[Tuple[TypeChecker.Types, str]]:
        if state is None:
            return self.typecheck(TypeChecker.TypecheckingState())
        if self.__next is None:
            val = TypeChecker.Types(self.__identifier_type)  # required string, correctly given
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

    def compile(self, state: "Generator.GeneratorState", program: "Generator.Trac42Program"):
        raise Generator.CompilerException("Cannot have identifier list inside function, "
                                          "nested functions are not allowed")

    # nothing to change in identifier list
    def optimize(self, state: "Optimizer.OptimizerState") -> Union["Statement", "AbstractSyntax.Expression"]:
        return self


class FunctionDeclaration(Statement):
    def __init__(self, line: int, column: int, return_type: str, identifier: "AbstractSyntax.Expression",
                 params: IdentifierList = None,
                 body: Statement = None):
        super().__init__(line, column)
        self.__return_type = return_type
        self.__identifier = identifier
        self.__params = params
        self.__body = body
        self.__decl_count = 0

    def pretty(self, pretty_builder, outer_precedence: int = None, opposite: bool = None) -> None:
        if outer_precedence is None and opposite is None:
            return self.pretty(pretty_builder, 1, False)

        pretty_builder.append(self.__return_type)
        pretty_builder.append(" ")
        self.__identifier.pretty(pretty_builder, 1, False)
        pretty_builder.append("(")
        if self.__params is not None:
            if type(self.__params) == list:
                # noinspection PyUnresolvedReferences,PyTypeChecker
                if len(self.__params) > 0 and type(self.__params[0]) == tuple:
                    pretty_builder.intersperse(", ", self.__params)
                else:
                    # noinspection PyTypeChecker
                    for param in self.__params:
                        param.pretty(pretty_builder, 1, False)
            else:
                self.__params.pretty(pretty_builder, 1, False)
        pretty_builder.append(") {")
        if self.__body is not None:
            pretty_builder.indent()
            pretty_builder.new_line()
            self.__body.pretty(pretty_builder, 1, False)
            pretty_builder.un_indent()
            pretty_builder.new_line()
        pretty_builder.append("}")

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

    # noinspection PyArgumentList
    def typecheck(self, state: "TypeChecker.TypecheckingState" = None) -> TypeChecker.Types:
        if state is None:
            return self.typecheck(TypeChecker.TypecheckingState())
        state.enter_scope()
        ret_type = TypeChecker.Types(self.__return_type)  # required string argument correctly passed
        if self.__params is not None and type(self.__params) != list:
            self.__params = self.__params.typecheck(state)  # ignored attribute reference warning
        elif type(self.__params) != list:
            self.__params = list()
        try:
            state.lookup_function(str(self.__identifier))
            super().typecheckException("TYPECHECK EXCEPTION: Function with same name already declared")
        except TypeChecker.TypecheckingStateException:
            state.bind_function(str(self.__identifier),
                                (ret_type, self.__params, self.__body, super().get_line(), super().get_column()))
        state.exit_scope()
        return ret_type

    def compile(self, state: "Generator.GeneratorState", program: "Generator.Trac42Program"):
        raise Exception("Cannot declare nested functions")

    def get_decl_count(self) -> dict:
        ret = dict()
        ret[str(self.__identifier)]=self.__decl_count
        return ret

    def optimize(self, state: "Optimizer.OptimizerState") -> Union["Statement", "AbstractSyntax.Expression"]:
        # bind function parameters
        index_to_remove = list()
        # noinspection PyTypeChecker
        for i in range(len(self.__params)):
            # noinspection PyUnresolvedReferences
            if state.is_del_variable(self.__params[i][1]):
                index_to_remove.append(i)
                continue
            # noinspection PyUnresolvedReferences
            if self.__params[i][0] == TypeChecker.Types.INT:
                # noinspection PyUnresolvedReferences
                state.bind_param(self.__params[i][1], "int")
            else:
                # noinspection PyUnresolvedReferences
                state.bind(self.__params[i][1], "bool")
            state.del_costant(self.__params[i][1])
        for i in index_to_remove[::-1]:
            # noinspection PyUnresolvedReferences
            del self.__params[i]
        if self.__body is not None:
            self.__body = self.__body.optimize(state)
            self.__decl_count = state.get_decl()
        state.is_last_return = False
        return self


class SequenceStatement(Statement):
    def __init__(self, head: Statement, tail: Statement = None):
        super().__init__()
        self.__head = head
        self.__tail = tail
        self.__decl_list = dict()

    def pretty(self, pretty_builder, outer_precedence: int = None, opposite: bool = None) -> None:
        if outer_precedence is None and opposite is None:
            return self.pretty(pretty_builder, 0, False)
        if self.__head is not None and self.__head != "" and type(self.__head) != EmptyStatement:
            self.__head.pretty(pretty_builder, outer_precedence, opposite)
        if self.__tail is not None and self.__tail != "" and type(self.__tail) != EmptyStatement:
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

    def typecheck(self, state: "TypeChecker.TypecheckingState" = None) -> \
            Union[Tuple[bool, "TypeChecker.TypecheckingState"], List[
                Union["TypeChecker.Types", Any]], "TypeChecker.Types"]:
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
                body = None
                if fun[2] is not None:
                    body = fun[2].typecheck(state)
                if not body:
                    body = TypeChecker.Types.VOID
                if type(body) == list:
                    # noinspection PyTypeChecker
                    for ret in body:  # body is list, but recognized as "Typechecker.Types"
                        if ret['return'] != ret_type:
                            super().typecheckException(
                                "TYPECHECK ERROR: Return type mismatch: function '{0}' should return {1}, "
                                "{2} returned instead on line {3} column {4}".format(key, ret_type.value,
                                                                                     ret['return'].value,
                                                                                     fun[3], fun[4]))
                elif body != ret_type:
                    super().typecheckException(
                        "TYPECHECK ERROR: Return type mismatch: function '{0}' should return {1}, "
                        "{2} returned instead on line {3} column {4}".format(key, ret_type.value, body.value, fun[3],
                                                                             fun[4]))
                state.exit_scope()
            return True, state
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
            # noinspection PyTypeChecker
            for x in res:  # type is list
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
                # noinspection PyTypeChecker
                for x in res:  # type is list
                    ret.append(x)
        return ret

    def compile(self, state: "Generator.GeneratorState", program: "Generator.Trac42Program"):
        state.is_return_last_function = False
        self.__head.compile(state, program)
        if self.__tail is not None and self.__tail != "":
            self.__tail.compile(state, program)

    def get_decl_count(self):
        return self.__decl_list

    def optimize(self, state: "Optimizer.OptimizerState") -> Union["Statement", "AbstractSyntax.Expression"]:
        if state.ignore_next > 0:
            return EmptyStatement()
        if self.__head is not None and self.__head != "":
            # noinspection PyUnresolvedReferences
            self.__head = self.__head.optimize(state)
        if hasattr(self.__head, "get_decl_count"):
            var = self.__head.get_decl_count()
            for name in var.keys():
                self.__decl_list[name] = var[name]
        if state.is_last_return:
            self.__tail = EmptyStatement()
        if state.ignore_next > 0:
            if type(self.__tail) != ReturnStatement:
                self.__tail = EmptyStatement()
            return self
        if self.__tail is not None and self.__tail != "":
            self.__tail = self.__tail.optimize(state)
        if hasattr(self.__tail, "get_decl_count"):
            var = self.__tail.get_decl_count()
            for name in var.keys():
                self.__decl_list[name] = var[name]
        if (self.__head is None or self.__head == "" or type(self.__head) == EmptyStatement) \
                and (self.__tail is None or self.__tail == "" or type(self.__tail) == EmptyStatement):
            return EmptyStatement()
        return self


class AssignmentStatement(Statement):
    def __init__(self, line: int, column: int, identifier: "AbstractSyntax.Expression",
                 expr: "AbstractSyntax.Expression"):
        super().__init__(line, column)
        self.__identifier = identifier
        self.__expr = expr
        self.__assignment_type = None

    def pretty(self, pretty_builder, outer_precedence: int = None, opposite: bool = None) -> None:
        if outer_precedence is None and opposite is None:
            return self.pretty(pretty_builder, 4, False)
        # impossible that parentheses will be retained
        if outer_precedence > 5 or (opposite and outer_precedence == 5):
            pretty_builder.append("(")
        # non necessary to pass  outer_precedence and opposite, identifier doesn't care
        self.__identifier.pretty(pretty_builder, 5, True)
        pretty_builder.append(" = ")
        # make same check as binary operator, associativity always right on assign
        self.__expr.pretty(pretty_builder, 5, False)
        if outer_precedence > 5 or (opposite and outer_precedence == 5):
            pretty_builder.append(")")

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
            self.__assignment_type = var_type
            return var_type
        except TypeChecker.TypecheckingStateException as e:
            super().typecheckException(str(e))

    def compile(self, state: "Generator.GeneratorState", program: "Generator.Trac42Program"):
        state.is_return_last_function = False
        position = state.lookup(str(self.__identifier))
        program.emit(Generator.Instruction(Generator.OpCode.LVAL, position))
        self.__expr.compile(state, program)
        if self.__assignment_type == TypeChecker.Types.INT:
            program.emit(Generator.Instruction(Generator.OpCode.ASSINT))
            program.emit(Generator.Instruction(Generator.OpCode.RVALINT, position))
        elif self.__assignment_type == TypeChecker.Types.BOOL:
            program.emit(Generator.Instruction(Generator.OpCode.ASSBOOL))
            program.emit(Generator.Instruction(Generator.OpCode.RVALBOOL, position))

    def optimize(self, state: "Optimizer.OptimizerState") -> Union["Statement", "AbstractSyntax.Expression"]:
        if hasattr(self.__expr, "contains") and self.__expr.contains(str(self.__identifier), True):
            state.del_costant(str(self.__identifier))
            state.bind_first_use(str(self.__identifier), Optimizer.FirstUseType.READ)
        state.bind_first_use(str(self.__identifier), Optimizer.FirstUseType.WRITE)
        for identifier in state.get_constant_identifiers():
            if hasattr(self.__expr, "contains") and self.__expr.contains(str(identifier), False):
                state.bind_first_use(str(identifier), Optimizer.FirstUseType.READ)
        self.__expr = self.__expr.optimize(state)
        if type(self.__expr) in (AbstractSyntax.BooleanExpression, AbstractSyntax.NumberExpression):
            val = self.__expr.evaluate()[0]
            if type(val) == int:
                state.bind(str(self.__identifier), val, "int")
            else:
                state.bind(str(self.__identifier), val, "bool")
        # TODO check if assignment is like x=x;
        if type(self.__expr) == AbstractSyntax.IdentifierExpression and str(self.__identifier) == str(self.__expr):
            return EmptyStatement()
        try:
            state.lookup_constant(str(self.__identifier))
            state.del_costant(str(self.__identifier))
        except Optimizer.OptimizerStateException:
            pass
        return self


class BlockStatement(Statement):
    def __init__(self, line: int, column: int, statement: Statement):
        super().__init__(line, column)
        self.__statement = statement

    def is_empty_statement(self):
        if self.__statement is None or type(self.__statement) == EmptyStatement or self.__statement == "":
            return True
        return False

    def pretty(self, pretty_builder, outer_precedence: int = None, opposite: bool = None) -> None:
        if outer_precedence is None and opposite is None:
            return self.pretty(pretty_builder, 3, False)
        if self.__statement is not None:
            self.__statement.pretty(pretty_builder, 3, False)

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

    def compile(self, state: "Generator.GeneratorState", program: "Generator.Trac42Program"):
        state.is_return_last_function = False
        if self.__statement is not None:
            current_offset = state.next_offset
            self.__statement.compile(state, program)
            offset = current_offset - state.next_offset
            if offset > 0:
                state.unbind_by_offset(current_offset)
                program.emit(Generator.Instruction(Generator.OpCode.POP, argument=offset))

    def optimize(self, state: "Optimizer.OptimizerState") -> Union["Statement", "AbstractSyntax.Expression"]:
        self.__statement = self.__statement.optimize(state)
        if type(self.__statement) == EmptyStatement:
            return EmptyStatement()
        return self


class IfStatement(Statement):
    def __init__(self, line: int, column: int, expression: "AbstractSyntax.Expression", statement: SequenceStatement,
                 else_statement: SequenceStatement = None):
        super().__init__(line, column)
        self.__expression = expression
        self.__statement = statement
        self.__else_statement = else_statement

    def pretty(self, pretty_builder, outer_precedence: int = None, opposite: bool = None) -> None:
        if outer_precedence is None and opposite is None:
            return self.pretty(pretty_builder, 3, False)
        pretty_builder.append("if (")
        self.__expression.pretty(pretty_builder, 3, False)
        pretty_builder.append(") {")
        if self.__statement is not None:
            pretty_builder.indent()
            pretty_builder.new_line()
            self.__statement.pretty(pretty_builder, 3, False)
            pretty_builder.un_indent()
            pretty_builder.new_line()
        pretty_builder.append("}")
        if self.__else_statement is not None:
            pretty_builder.append(" else {")
            pretty_builder.indent()
            pretty_builder.new_line()
            self.__else_statement.pretty(pretty_builder, 3, False)
            pretty_builder.un_indent()
            pretty_builder.new_line()
            pretty_builder.append("}")

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
                # noinspection PyUnresolvedReferences
                ret.append(res)  # ret is not none, ret is list
            elif type(res) == list and type(ret) != list:
                ret = res
            elif type(res) == list and type(ret) == list:
                for x in res:
                    # noinspection PyUnresolvedReferences
                    ret.append(x)  # ret is not none, ret is list
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

    def compile(self, state: "Generator.GeneratorState", program: "Generator.Trac42Program"):
        state.is_return_last_function = False
        # if check
        self.__expression.compile(state, program)
        label_end = state.rename_label("end_if")
        label_else = label_end
        if self.__else_statement is not None:
            label_else = state.rename_label("else")
        program.emit(Generator.Instruction(Generator.OpCode.BRF, target=label_else))
        # then body
        self.__statement.compile(state, program)
        program.emit(Generator.Instruction(Generator.OpCode.BRA, target=label_end))
        if self.__else_statement is not None:
            # else body
            program.emit(Generator.Instruction(Generator.OpCode.LABEL, target=label_else))
            self.__else_statement.compile(state, program)
        program.emit(Generator.Instruction(Generator.OpCode.LABEL, target=label_end))

    def optimize(self, state: "Optimizer.OptimizerState") -> Union["Statement", "AbstractSyntax.Expression"]:
        state.set_lookup_variable()
        self.__expression = self.__expression.optimize(state)
        state.unset_lookup_variable()
        if type(self.__expression) == AbstractSyntax.BooleanExpression:
            if self.__expression.evaluate()[0]:
                self.__statement.optimize(state)
                return self.__statement
            if self.__else_statement is not None:
                self.__else_statement.optimize(state)
                return self.__else_statement
            return EmptyStatement()
        return self


class WhileStatement(Statement):
    def __init__(self, line: int, column: int, expression: "AbstractSyntax.Expression", body: "BlockStatement"):
        super().__init__(line, column)
        self.__expression = expression
        self.__body = body

    def pretty(self, pretty_builder, outer_precedence: int = None, opposite: bool = None) -> None:
        if outer_precedence is None and opposite is None:
            return self.pretty(pretty_builder, 3, False)
        pretty_builder.append("while (")
        self.__expression.pretty(pretty_builder, 3, False)
        pretty_builder.append(") {")
        if self.__body is not None:
            pretty_builder.indent()
            pretty_builder.new_line()
            self.__body.pretty(pretty_builder, 3, False)
            pretty_builder.un_indent()
            pretty_builder.new_line()
        pretty_builder.append("}")

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
                # noinspection PyUnresolvedReferences
                ret.append(res)  # ret is not none, ret is list
            elif type(res) == list and type(ret) != list:
                ret = res
            elif type(res) == list and type(ret) == list:
                # noinspection PyTypeChecker
                for x in res:  # res is not none, res is list
                    # noinspection PyUnresolvedReferences
                    ret.append(x)  # ret is not none, ret is list
        if ret is None:
            ret = TypeChecker.Types.VOID
        return ret

    def compile(self, state: "Generator.GeneratorState", program: "Generator.Trac42Program"):
        state.is_return_last_function = False
        label_while = state.rename_label("while_do")
        label_end = state.rename_label("end_while")
        program.emit(Generator.Instruction(Generator.OpCode.LABEL, target=label_while))
        # guard of while
        self.__expression.compile(state, program)
        program.emit(Generator.Instruction(Generator.OpCode.BRF, target=label_end))
        # body of while
        self.__body.compile(state, program)
        if not state.is_return_last_function:
            program.emit(Generator.Instruction(Generator.OpCode.BRA, target=label_while))
        program.emit(Generator.Instruction(Generator.OpCode.LABEL, target=label_end))

    def optimize(self, state: "Optimizer.OptimizerState") -> Union["Statement", "AbstractSyntax.Expression"]:
        old_expression = copy.deepcopy(self.__expression)
        self.__expression = self.__expression.optimize(state)
        try:
            if not self.__expression.evaluate()[0]:
                return EmptyStatement()
            else:
                if hasattr(self.__expression, "is_equivalent") and not self.__expression.is_equivalent(old_expression):
                    self.__expression = old_expression

        except Evaluator.EvaluatorException:
            # Variable not declared, means cannot simplify the expression
            pass
        if not self.__body.is_empty_statement():
            self.__body.optimize(state)
        # empty body with true condition aka infinite loop
        if self.__body.is_empty_statement():
            state.add_warning("Optimization Warning: Infinite empty loop detected on line: " + str(super().get_line()) +
                              " column: " + str(super().get_column()))
            state.ignore_next = 1
        if type(self.__expression) == AbstractSyntax.BooleanExpression and self.__expression.evaluate()[0]:
            state.add_warning("Optimization Warning: Infinite loop detected on line: " + str(super().get_line()) +
                              " column: " + str(super().get_column()))
            state.ignore_next = 1
        return self


class ReturnStatement(Statement):
    def __init__(self, line: int, column: int, expression: "AbstractSyntax.Expression" = None):
        super().__init__(line, column)
        self.__expression = expression
        self.__expected_return_type = None

    def pretty(self, pretty_builder, outer_precedence: int = None, opposite: bool = None) -> None:
        if outer_precedence is None and opposite is None:
            return self.pretty(pretty_builder, 3, False)
        pretty_builder.append("return")
        if self.__expression is not None:
            pretty_builder.append(" ")
            self.__expression.pretty(pretty_builder, 3, False)
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
            super().typecheckException(
                "TYPECHECK ERROR: Return type mismatch, expected {0} got {1}".format(self.__expected_return_type.value,
                                                                                     ret.value))
        return {"type": ret, "return": ret}

    def compile(self, state: "Generator.GeneratorState", program: "Generator.Trac42Program"):
        if self.__expression is not None:
            return_offset = state.offset_map['return']
            program.emit(Generator.Instruction(Generator.OpCode.LVAL, argument=return_offset))
            self.__expression.compile(state, program)
            if self.__expected_return_type == TypeChecker.Types.INT:
                program.emit(Generator.Instruction(Generator.OpCode.ASSINT))
            elif self.__expected_return_type == TypeChecker.Types.BOOL:
                program.emit(Generator.Instruction(Generator.OpCode.ASSBOOL))
            else:
                raise Generator.CompilerException("Invalid return type {0}".format(self.__expected_return_type))
        program.emit(Generator.Instruction(Generator.OpCode.UNLINK))
        program.emit(Generator.Instruction(Generator.OpCode.RTS))
        state.is_return_last_function = True

    def optimize(self, state: "Optimizer.OptimizerState") -> Union["Statement", "AbstractSyntax.Expression"]:
        if self.__expression is not None:
            self.__expression = self.__expression.optimize(state)
        state.is_last_return = True
        return self


class DefinitionStatement(Statement):
    def __init__(self, line: int, column: int, variable_type: str, identifier: "AbstractSyntax.Expression"):
        super().__init__(line, column)
        self.__variable_type = variable_type
        self.__identifier = identifier

    def pretty(self, pretty_builder, outer_precedence: int = None, opposite: bool = None) -> None:
        if outer_precedence is None and opposite is None:
            return self.pretty(pretty_builder, 3, False)
        pretty_builder.append(self.__variable_type)
        pretty_builder.append(" ")
        # non necessary to pass outer_precedence and opposite, identifier doesn't care
        self.__identifier.pretty(pretty_builder, 3, False)
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
        return TypeChecker.Types(self.__variable_type)  # type is string

    def compile(self, state: "Generator.GeneratorState", program: "Generator.Trac42Program"):
        state.is_return_last_function = False
        state.bind(str(self.__identifier))
        check = state.lookup_fist_use(str(self.__identifier))
        if check is not None and check == Optimizer.FirstUseType.READ:
            # assigning base value
            position = state.lookup(str(self.__identifier))
            program.emit(Generator.Instruction(Generator.OpCode.LVAL, argument=position))
            if self.__variable_type == "int":
                program.emit(Generator.Instruction(Generator.OpCode.PUSHINT, argument=0))
                program.emit(Generator.Instruction(Generator.OpCode.ASSINT))
            else:
                program.emit(Generator.Instruction(Generator.OpCode.PUSHBOOL, argument="false"))
                program.emit(Generator.Instruction(Generator.OpCode.ASSBOOL))

    def optimize(self, state: "Optimizer.OptimizerState") -> Union["Statement", "AbstractSyntax.Expression"]:
        if state.is_del_variable(str(self.__identifier)):
            return EmptyStatement()
        state.inc_decl()
        if self.__variable_type == "int":
            state.bind(str(self.__identifier), None, "int")
        else:
            state.bind(str(self.__identifier), None, "bool")
        return self


# only used in variable optimization
class EmptyStatement(Statement):
    def optimize(self, state: "Optimizer.OptimizerState") -> Union["Statement", "AbstractSyntax.Expression"]:
        pass

    def compile(self, state: "Generator.GeneratorState", program: "Generator.Trac42Program"):
        pass

    def typecheck(self, state: "TypeChecker.TypecheckingState" = None) -> TypeChecker.Types:
        pass

    def evaluate(self, state: Evaluator.EvaluationState = None):
        pass

    def prepass(self, prepass: Evaluator.PrepassState = None):
        pass

    def pretty(self, pretty_builder, outer_precedence: int = None, opposite: bool = None) -> None:
        pass
