class GeneratorState:
    def __init__(self):
        self.offset_map = {}
        self.next_offset = -1
        self.__labels = {}

    def bind(self, name: str):
        self.offset_map[name] = self.next_offset
        self.next_offset -= 1

    def lookup(self, name: str) -> int:
        return self.offset_map[name]

    def unbind(self, name: str):
        del self.offset_map[name]
        self.next_offset += 1

    def unbind_by_offset(self, offset: int):
        index_list = []
        for name in self.offset_map.keys():
            if self.offset_map[name] < offset:
                index_list.append(name)
        for name in index_list:
            del self.offset_map[name]
        self.next_offset = offset

    def rename_label(self, name: str):
        if name in self.__labels.keys():
            self.__labels[name] += 1
            return "{0}_{1}".format(name, self.__labels[name])
        self.__labels[name] = 0
        return name

    def lookup_label(self, name: str):
        if name in self.__labels.keys():
            if self.__labels[name] > 0:
                return "{0}_{1}".format(name, self.__labels[name])
            return name
        raise Exception("Label not present")
