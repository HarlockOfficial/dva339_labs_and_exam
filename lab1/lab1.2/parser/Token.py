from Type import TokenType


class Token:
    def __init__(self, token_type, lexeme, line, column):
        self.__token_type = token_type
        self.__lexeme = lexeme
        self.__line = line
        self.__column = column

    def __str__(self):
        if self.__lexeme is None:
            return "{0} {1} {2}".format(self.__token_type.name, self.__line, self.__column)
        return "{0} {1} {2} {3}".format(self.__token_type.name, self.__lexeme, self.__line, self.__column)

    def get_token_type(self) -> TokenType:
        return self.__token_type

    def get_lexeme(self):
        return self.__lexeme

    def get_line(self):
        return self.__line

    def get_column(self):
        return self.__column


class UnexpectedTokenException(Exception):
    def __init__(self, message: str):
        super().__init__(message)
