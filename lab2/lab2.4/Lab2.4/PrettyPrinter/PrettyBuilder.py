from typing import Union, List
from AbstractSyntax import Statement, Expression


class PrettyBuilder:
    def __init__(self):
        self.__indent = 0
        self.__string = ""

    def indent(self) -> None:
        self.__indent += 2

    def un_indent(self) -> None:
        self.__indent -= 2

    def append(self, string: str) -> None:
        self.__string += string

    def new_line(self) -> None:
        self.append("\n")
        if self.__indent > 0:
            self.append(' ' * self.__indent)

    def intersperse(self, separator: str, pretties: Union[List[Statement], List[Expression]]) -> None:
        first = True
        for x in pretties:
            if not first:
                self.append(separator)
            first = False
            x.pretty(self)

    def vertical(self, pretties: Union[List[Statement], List[Expression]]):
        pass

    def layout(self) -> str:
        pass

    def __str__(self):
        return self.__string
