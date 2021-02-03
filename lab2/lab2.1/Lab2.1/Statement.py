from abc import ABC, abstractmethod

from Expression import IdentifierExpression, Expression


class Statement(ABC):
    @abstractmethod
    def pretty(self) -> str:
        pass

    def __str__(self):
        return self.pretty()


class IdentifierList(Statement):
    def __init__(self, identifier_type: str, identifier: IdentifierExpression, next_identifier: Statement = None):
        self.__identifier_type = identifier_type
        self.__identifier = identifier
        self.__next = next_identifier

    def pretty(self) -> str:
        string = str(self.__identifier_type) + " " + str(self.__identifier)
        if self.__next is not None:
            string += ", " + str(self.__next)
        return string


class FunctionDeclaration(Statement):
    def __init__(self, return_type: str, identifier: IdentifierExpression, params: Expression, body: Statement):
        self.__return_type = return_type
        self.__name = identifier
        self.__params = params
        self.__body = body

    def pretty(self) -> str:
        string = self.__return_type + " " + str(self.__name) + " ("
        if self.__params is not None:
            string += str(self.__params)
        string += ") { "
        if self.__body is not None:
            string += str(self.__body)
        return string + " } "


class SequenceStatement(Statement):
    def __init__(self, head: Statement, tail: Statement = None):
        self.__head = head
        self.__tail = tail

    def pretty(self):
        string = ""
        if self.__head is not None:
            string += str(self.__head)
        if self.__tail is not None:
            string += str(self.__tail)
        return string


class AssignmentStatement(Statement):
    def __init__(self, identifier: str, expr: Expression):
        self.__identifier = identifier
        self.__expr = expr

    def pretty(self) -> str:
        return self.__identifier + " = " + str(self.__expr)


class BlockStatement(Statement):
    def __init__(self, statement: Statement):
        self.__statement = statement

    def pretty(self) -> str:
        if self.__statement is None:
            return "{ } "
        return "{ " + str(self.__statement) + " }"


class IfStatement(Statement):
    def __init__(self, expression: Expression, statement: SequenceStatement,
                 else_statement: SequenceStatement = None):
        self.__expression = expression
        self.__statement = statement
        self.__else_statement = else_statement

    def pretty(self) -> str:
        string = "if (" + str(self.__expression) + ") "
        if self.__statement is not None:
            string += str(self.__statement)
        else:
            string += "{ }"
        if self.__else_statement is not None:
            string += "else " + str(self.__else_statement)
        return string


class WhileStatement(Statement):
    def __init__(self, expression: Expression, body: Statement):
        self.__expression = expression
        self.__body = body

    def pretty(self) -> str:
        string = "while (" + str(self.__expression) + ") "
        if self.__body is not None:
            string += str(self.__body)
        else:
            string += "{ }"
        return string


class ReturnStatement(Statement):
    def __init__(self, expression: Expression = None):
        self.__expression = expression

    def pretty(self) -> str:
        if self.__expression is not None:
            return "return " + str(self.__expression) + ";"
        return "return ;"


class DefinitionStatement(Statement):
    def __init__(self, variable_type: str, identifier: IdentifierExpression):
        self.__variable_type = variable_type
        self.__identifier = identifier

    def pretty(self) -> str:
        return self.__variable_type + " " + str(self.__identifier) + "; "
