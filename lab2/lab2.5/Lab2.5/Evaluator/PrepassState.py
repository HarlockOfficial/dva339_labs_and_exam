class PrepassState:
    def __init__(self):
        self.__nameStack = list()
        self.__countStack = list()
        self.enter_scope()

    def enter_scope(self):
        self.__nameStack.append(dict())
        self.__countStack.append(dict())

    def exit_scope(self):
        self.__nameStack.pop()
        self.__countStack.pop()

    def bind(self, name: str):
        count = 0
        for count_dict in self.__countStack:
            if name in count_dict.keys():
                count = count_dict[name]

        self.__countStack[len(self.__countStack) - 1][name] = count + 1
        self.__nameStack[len(self.__nameStack) - 1][name] = (name if count == 0 else "{0}_{1}".format(name, count))

    def rename(self, name: str):
        result = name
        for name_dict in self.__nameStack:
            if name in name_dict.keys():
                result = name_dict[name]
        return result
