from typing import Optional

from LexerException import LexerException
from Token import Token
from Type import Type

import re


class Lexer:
    __new_line = {'\n', '\r'}
    __operators = r'^\+|^:='
    __separators = r'^;|^\(|^\)|^,'
    __keywords = {"print"}

    def __init__(self, string):
        self.__string = string
        self.__token = None
        self.__row = 1
        self.__column = 1

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
            self.__token = Token(Type.EOF, "", self.__row, self.__column)
            return self.__token
        # check for separators
        self.__token = self.__match(Lexer.__separators, Type.SEP)
        if self.__token is None:
            # check for operators
            self.__token = self.__match(Lexer.__operators, Type.OP)
            if self.__token is None:
                # check for identifiers and keywords
                self.__token = self.__match_identifier()
                if self.__token is None:
                    # check for number
                    self.__token = self.__match_number()
                    if self.__token is None:
                        if len(self.__string) != 0:
                            # non recognized
                            return self.__peek()
                            # raise LexerException()
                        # EOF
                        self.__trim()
                        self.__token = Token(Type.EOF, "", self.__row, self.__column)
        return self.__token

    def __trim(self):
        while len(self.__string) > 0:
            res = re.search(r'^\r\n', self.__string)
            if res is not None:
                unused, end = res.span()
                self.__string = self.__string[end:]
                self.__column = 1
                self.__row += 1
                continue
            if self.__string[0] in Lexer.__new_line:
                self.__string = self.__string[1:]
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
                return Token(Type.KEYW, pattern, self.__row, self.__column-end)
            return Token(Type.ID, pattern, self.__row, self.__column-end)
        return None

    def __match_number(self) -> Optional[Token]:
        res = re.search(r'^[0-9]+', self.__string)
        if res is not None:
            unused, end = res.span()
            pattern = self.__string[0:end]
            self.__string = self.__string[end:]
            self.__column += end
            return Token(Type.NUM, pattern, self.__row, self.__column - end)
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
