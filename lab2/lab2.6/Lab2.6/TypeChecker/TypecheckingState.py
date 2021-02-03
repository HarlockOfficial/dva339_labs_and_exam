from typing import Tuple, List, KeysView

import AbstractSyntax
import TypeChecker


class TypecheckingState:
    def __init__(self):
        self.__variable_stack = list()
        self.__functions = dict()
        self.__current_function_name = ""
        self.enter_scope()

    def enter_scope(self) -> None:
        self.__variable_stack.insert(0, dict())

    def exit_scope(self) -> None:
        self.__variable_stack.pop(0)

    def bind_variable(self, name: str, value: "TypeChecker.Types") -> None:
        self.__variable_stack[0][name] = value

    def lookup_variable(self, name: str) -> "TypeChecker.Types":
        for elem in self.__variable_stack:
            if name in elem.keys():
                return elem[name]
        raise TypecheckingStateException("Variable {0} not declared".format(name))

    def bind_function(self, name: str, value: Tuple["TypeChecker.Types", List[Tuple["TypeChecker.Types", str]],
                                                    "AbstractSyntax.Statement", int, int]) -> None:
        self.__functions[name] = value
        # value contains in order: Return Type, List[Parameter type, Parameter name], Body of Function, line, column

    def lookup_function(self, name: str) -> Tuple["TypeChecker.Types", List[Tuple["TypeChecker.Types", str]],
                                                  "AbstractSyntax.Statement", int, int]:
        if name in self.__functions.keys():
            return self.__functions[name]
        raise TypecheckingStateException("Function {0} not declared".format(name))

    def get_all_functions(self) -> KeysView:
        return self.__functions.keys()

    def get_current_function_name(self) -> str:
        return self.__current_function_name

    def set_current_function_name(self, name: str) -> None:
        self.lookup_function(name)
        self.__current_function_name = name


class TypecheckingStateException(Exception):
    pass


class TypecheckerException(Exception):
    pass
