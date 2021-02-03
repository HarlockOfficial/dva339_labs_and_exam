from abc import ABC, abstractmethod
from typing import List

from Expression import Expression


class Statement(ABC):
    @abstractmethod
    def pretty(self) -> str:
        pass

    def __str__(self):
        return self.pretty()


class SequenceStatement(Statement):
    def __init__(self, head: Statement, tail: Statement):
        self.__head = head
        self.__tail = tail

    def pretty(self):
        return self.__head.pretty()+"; "+self.__tail.pretty()


class PrintStatement(Statement):
    def __init__(self, expr: List[Expression]):
        self.__expr = expr

    def pretty(self) -> str:
        out = "print ("
        for x in self.__expr:
            out += x.pretty()+", "
        return out[:-2]+")"


class AssignmentStatement(Statement):
    def __init__(self, identifier: str, expr: Expression):
        self.__identifier = identifier
        self.__expr = expr

    def pretty(self) -> str:
        return self.__identifier + " := " + self.__expr.pretty()
