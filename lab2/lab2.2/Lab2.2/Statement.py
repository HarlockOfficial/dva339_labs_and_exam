from abc import ABC, abstractmethod

import Expression


class Statement(ABC):
    @abstractmethod
    def pretty(self, pretty_builder, outer_precedence: int = None, opposite: bool = None) -> None:
        pass

    def __str__(self):
        import PrettyBuilder
        builder = PrettyBuilder.PrettyBuilder()
        self.pretty(builder)
        return str(builder)


class IdentifierList(Statement):
    def __init__(self, identifier_type: str, identifier: Expression.IdentifierExpression,
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


class FunctionDeclaration(Statement):
    import Expression

    def __init__(self, return_type: str, identifier: Expression, params: IdentifierList, body: Statement):
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


class AssignmentStatement(Statement):
    def __init__(self, identifier: Expression, expr: Expression):
        self.__identifier = identifier
        self.__expr = expr

    # TODO fix outer_precedence
    def pretty(self, pretty_builder, outer_precedence: int = None, opposite: bool = None) -> None:
        if outer_precedence is None and opposite is None:
            return self.pretty(pretty_builder, 0, False)
        self.__identifier.pretty(pretty_builder, 0, False)
        pretty_builder.append(" = ")
        self.__expr.pretty(pretty_builder, 2, False)


class BlockStatement(Statement):
    def __init__(self, statement: Statement):
        self.__statement = statement

    # TODO fix outer_precedence and opposite
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


class IfStatement(Statement):
    def __init__(self, expression: Expression, statement: SequenceStatement,
                 else_statement: SequenceStatement = None):
        self.__expression = expression
        self.__statement = statement
        self.__else_statement = else_statement

    # TODO check for outer_precedence and opposite
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


class WhileStatement(Statement):
    def __init__(self, expression: Expression, body: Statement):
        self.__expression = expression
        self.__body = body

    # TODO fix outer_precedence and opposite
    def pretty(self, pretty_builder, outer_precedence: int = None, opposite: bool = None) -> None:
        if outer_precedence is None and opposite is None:
            return self.pretty(pretty_builder, 0, False)
        pretty_builder.append("while (")
        self.__expression.pretty(pretty_builder, 0, False)
        pretty_builder.append(")")
        if self.__body is not None:
            self.__body.pretty(pretty_builder, 0, False)


class ReturnStatement(Statement):
    def __init__(self, expression: Expression = None):
        self.__expression = expression

    # TODO fix outer_precedence and opposite
    def pretty(self, pretty_builder, outer_precedence: int = None, opposite: bool = None) -> None:
        if outer_precedence is None and opposite is None:
            return self.pretty(pretty_builder, 0, False)
        pretty_builder.append("return")
        if self.__expression is not None:
            pretty_builder.append(" ")
            self.__expression.pretty(pretty_builder, 0, False)
        pretty_builder.append(";")


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
