from Statement import PrintStatement, AssignmentStatement, SequenceStatement, Statement
from Expression import LetExpression, BinaryOperatorExpression, IdentifierExpression, NumberExpression, Expression
from Token import UnexpectedTokenException
from Type import BinaryOperatorType, TokenType
from Lexer import Lexer
from typing import List, Union


class Parser:
    def __init__(self, string: str = None, lexer: Lexer = None):
        if str is not None:
            self.__lexer = Lexer(string)
        elif lexer is not None:
            self.__lexer = lexer
        else:
            raise ValueError("String or Lexer object should be passed")

    def parse(self) -> str:
        x = self.__parseS()
        return str(x)

    def __parseS(self) -> Statement:
        head = self.__parseT()
        tail = self.__parseTs()
        if tail is not None:
            return SequenceStatement(head, tail)
        return head

    def __parseTs(self) -> Union[Statement, None]:
        if self.__lexer.isNext(TokenType.SEP, ';'):
            self.__lexer.next()
            return self.__parseS()
        return None

    def __parseT(self) -> Statement:
        if self.__lexer.isNext(TokenType.ID):
            tmp = self.__lexer.next()
            identifier = tmp.get_lexeme()
            elem = self.__lexer.next()
            if elem.get_lexeme() != ':=':
                self.__unexpected_token("Expected ':='. Found " + str(elem.get_token_type().name) + " ("
                                        + elem.get_lexeme() + ") at line " + str(elem.get_line()) + " column " +
                                        str(elem.get_column()) + ".")
            expression = self.__parseE()
            return AssignmentStatement(identifier, expression)
        if self.__lexer.isNext(TokenType.KEYW, "print"):
            self.__lexer.next()
            elem = self.__lexer.next()
            if elem.get_lexeme() != '(':
                self.__unexpected_token("Expected '('. Found " + str(elem.get_token_type().name) + " ("
                                        + elem.get_lexeme() + ") at line " + str(elem.get_line()) + " column " +
                                        str(elem.get_column()) + ".")
            expression = self.__parseL()
            elem = self.__lexer.next()
            if elem.get_lexeme() != ')':
                self.__unexpected_token("Expected ')'. Found " + str(elem.get_token_type().name) + " ("
                                        + elem.get_lexeme() + ") at line " + str(elem.get_line()) + " column " +
                                        str(elem.get_column()) + ".")
            return PrintStatement(expression)
        elem = self.__lexer.next()
        self.__unexpected_token("Expected ID or PRINT. Found " + str(elem.get_token_type().name) + " ("
                                + elem.get_lexeme() + ") at line " + str(elem.get_line()) + " column " +
                                str(elem.get_column()) + ".")

    def __parseE(self) -> Expression:
        expression_left = self.__parseF()
        expression_right = self.__parseFs()
        if expression_right is not None:
            return BinaryOperatorExpression(BinaryOperatorType.ADD, expression_left, expression_right)
        return expression_left

    def __parseL(self) -> List[Expression]:
        expr_1 = self.__parseE()
        expr_2 = self.__parseMs()
        if expr_2 is not None:
            expr_2.insert(0, expr_1)
            return expr_2
        return [expr_1]

    def __parseFs(self) -> Union[Expression, None]:
        if self.__lexer.isNext(TokenType.OP, "+"):
            self.__lexer.next()
            return self.__parseE()
        return None

    def __parseF(self) -> Expression:
        if self.__lexer.isNext(TokenType.ID):
            tmp = self.__lexer.next()
            return IdentifierExpression(str(tmp.get_lexeme()))

        if self.__lexer.isNext(TokenType.NUM):
            tmp = self.__lexer.next()
            return NumberExpression(int(tmp.get_lexeme()))

        if self.__lexer.isNext(TokenType.SEP, '('):
            self.__lexer.next()
            statement = self.__parseS()
            elem = self.__lexer.next()
            if elem.get_lexeme() != ',':
                self.__unexpected_token("Expected ','. Found " + str(elem.get_token_type().name) + " ("
                                        + elem.get_lexeme() + ") at line " + str(elem.get_line()) + " column " +
                                        str(elem.get_column()) + ".")
            expression = self.__parseE()
            elem = self.__lexer.next()
            if elem.get_lexeme() != ')':
                self.__unexpected_token("Expected ')'. Found " + str(elem.get_token_type().name) + " ("
                                        + elem.get_lexeme() + ") at line " + str(elem.get_line()) + " column " +
                                        str(elem.get_column()) + ".")
            return LetExpression(statement, expression)
        elem = self.__lexer.next()
        self.__unexpected_token("Expected ID, NUM or '('. Found " + str(elem.get_token_type().name) + " ("
                                + elem.get_lexeme() + ") at line " + str(elem.get_line()) + " column " +
                                str(elem.get_column()) + ".")

    tmp_count = 0

    def __parseMs(self):
        Parser.tmp_count += 1
        if self.__lexer.isNext(TokenType.SEP, ","):
            self.__lexer.next()
            tmp = self.__parseL()
            return tmp
        return None

    def __unexpected_token(self, message: str):
        raise UnexpectedTokenException(message)
