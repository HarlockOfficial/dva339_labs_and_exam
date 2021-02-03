from Type import Type


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

    def get_token_type(self) -> Type:
        return self.__token_type
