from abc import ABC, abstractmethod

from AbstractSyntax import Expression
import Evaluator


class Statement(ABC):
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
    def __init__(self, identifier_type: str, identifier: Expression,
                 next_identifier: Statement = None):
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


class FunctionDeclaration(Statement):
    def __init__(self, return_type: str, identifier: Expression, params: IdentifierList = None, body: Statement = None):
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


class SequenceStatement(Statement):
    def __init__(self, head: Statement, tail: Statement = None):
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
                raise Evaluator.EvaluatorException("INTERPRETATION ERROR: Required function 'main' not found")
            main = state.lookup_function("main")
            if main[2]:
                val, ret = main[2].evaluate(state)
                provided_type = type(val).__name__
                if provided_type == "NoneType":
                    provided_type = "void"
                if ret == Evaluator.ReturnType.RETURN and provided_type != main[0]:
                    raise Evaluator.EvaluatorException("INTERPRETATION ERROR: Return type of 'main': {0}, provided {1} "
                                                       "instead".format(main[0], provided_type))
            return
        val, ret = self.__head.evaluate(state)
        if self.__tail is not None and self.__tail != "" and ret != Evaluator.ReturnType.RETURN:
            val, ret = self.__tail.evaluate(state)
        return val, ret


class AssignmentStatement(Statement):
    def __init__(self, identifier: Expression, expr: Expression):
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
            raise Evaluator.Evaluator.EvaluatorException("INTERPRETATION ERROR: Expected value got void")
        current_val = state.lookup(str(self.__identifier))
        if type(current_val) != type(val):
            raise Evaluator.Evaluator.EvaluatorException("INTERPRETATION ERROR: Expected {0} got {1} instead".format(
                type(current_val).__name__, type(val).__name__))
        state.bind(str(self.__identifier), val)
        return val, Evaluator.ReturnType.CONTINUE


class BlockStatement(Statement):
    def __init__(self, statement: Statement):
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


class IfStatement(Statement):
    def __init__(self, expression: Expression, statement: SequenceStatement,
                 else_statement: SequenceStatement = None):
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
            raise Evaluator.Evaluator.EvaluatorException("INTERPRETATION ERROR: Expected boolean condition got {0}".
                                                         format(type(val)))
        res = None
        ret = Evaluator.ReturnType.CONTINUE
        if val:
            if self.__statement is not None:
                res, ret = self.__statement.evaluate(state)
        elif self.__else_statement is not None and ret != Evaluator.ReturnType.RETURN:
            res, ret = self.__else_statement.evaluate(state)
        return res, ret


class WhileStatement(Statement):
    def __init__(self, expression: Expression, body: Statement):
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
                raise Evaluator.Evaluator.EvaluatorException("INTERPRETATION ERROR: Expected boolean condition got {0}".
                                                             format(type(expr)))
            if expr:
                result, ret = self.__body.evaluate(state)
                if result is not None:
                    if res is None:
                        res = list()
                    res.append(result)
                if ret != Evaluator.ReturnType.RETURN:
                    continue
            return res, ret


class ReturnStatement(Statement):
    def __init__(self, expression: Expression = None):
        self.__expression = expression

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


class DefinitionStatement(Statement):
    def __init__(self, variable_type: str, identifier: Expression):
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
