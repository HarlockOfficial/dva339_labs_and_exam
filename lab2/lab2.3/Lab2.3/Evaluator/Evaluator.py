from typing import Union


class EvaluatorException(Exception):
    pass


class EvaluationState:
    def __init__(self):
        self.__call_stack = list()
        self.__function_list = dict()
        self.enter_scope()

    def enter_scope(self):
        self.__call_stack.insert(0, dict())

    def exit_scope(self):
        self.__call_stack.pop(0)

    def bind(self, name: str, value: Union[int, bool]):
        self.__call_stack[0][name] = value

    def lookup(self, name: str) -> Union[int, bool, None]:
        value: Union[int, bool, None] = None
        for frame in self.__call_stack:
            if name in frame.keys():
                value = frame[name]
                break
        return value

    def has(self, name: str) -> bool:
        for frame in self.__call_stack:
            if name in frame.keys():
                return True
        return False

    def bind_function(self, name: str, func: tuple):
        self.__function_list[name] = func

    def lookup_function(self, name: str) -> tuple:
        func = None
        if name in self.__function_list.keys():
            func = self.__function_list[name]
        return func

    def has_function(self, name: str) -> bool:
        return name in self.__function_list.keys()
