from typing import Optional

from Token import Token
from Type import TokenType

import re


class Lexer:
    __new_line = {"\n", "\r"}
    __operators = r'^\+|^:='
    __separators = r'^;|^\(|^\)|^,'
    __keywords = {"print"}

    def __init__(self, string):
        self.__string = string
        self.__token = None
        self.__row = 1
        self.__column = 1

    def isNext(self, token_type: TokenType, lexeme: str = None):
        return self.peek().get_token_type() == token_type and \
               ((self.peek().get_lexeme() == lexeme) if lexeme is not None else True)

    def next(self):
        tmp = self.peek()
        self.__token = None
        return tmp

    def peek(self):
        if self.__token is not None:
            return self.__token
        # remove spaces/tabs/newlines
        self.__trim()
        # check if EOF
        if len(self.__string) == 0:
            self.__token = Token(TokenType.EOF, "", self.__row, self.__column)
            return self.__token
        # check for separators
        self.__token = self.__match(Lexer.__separators, TokenType.SEP)
        if self.__token is None:
            # check for operators
            self.__token = self.__match(Lexer.__operators, TokenType.OP)
            if self.__token is None:
                # check for identifiers and keywords
                self.__token = self.__match_identifier()
                if self.__token is None:
                    # check for number
                    self.__token = self.__match_number()
                    if self.__token is None:
                        if len(self.__string) != 0:
                            # non recognized
                            raise LexerException()
                        # EOF
                        self.__trim()
                        self.__token = Token(TokenType.EOF, "", self.__row, self.__column)
        return self.__token

    def __trim(self):
        while len(self.__string) > 0:
            res = re.search(r'^\r?\n', self.__string)
            if res is not None:
                unused, end = res.span()
                self.__string = self.__string[end:]
                self.__column = 1
                self.__row += 1
                continue
            if ' ' == self.__string[0]:
                self.__column += 1
                self.__string = self.__string[1:]
                continue
            if '\t' == self.__string[0]:
                self.__column += 8
                self.__string = self.__string[1:]
                continue
            break

    def __match_identifier(self) -> Optional[Token]:
        res = re.search(r'^[a-zA-Z][a-zA-Z0-9]*', self.__string)
        if res is not None:
            unused, end = res.span()
            pattern = self.__string[0:end]
            self.__string = self.__string[end:]
            self.__column += end
            if pattern in Lexer.__keywords:
                return Token(TokenType.KEYW, pattern, self.__row, self.__column-end)
            return Token(TokenType.ID, pattern, self.__row, self.__column-end)
        return None

    def __match_number(self) -> Optional[Token]:
        res = re.search(r'^[0-9]+', self.__string)
        if res is not None:
            unused, end = res.span()
            pattern = self.__string[0:end]
            self.__string = self.__string[end:]
            self.__column += end
            return Token(TokenType.NUM, pattern, self.__row, self.__column - end)
        return None

    def __match(self, regex, token_type) -> Optional[Token]:
        res = re.search(regex, self.__string)
        if res is not None:
            unused, end = res.span()
            pattern = self.__string[0:end]
            self.__string = self.__string[end:]
            self.__column += end
            return Token(token_type, pattern, self.__row, self.__column - end)
        return None


class LexerException(Exception):
    pass
