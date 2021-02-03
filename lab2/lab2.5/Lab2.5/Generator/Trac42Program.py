import Generator.Instruction as Instruction
from Generator.OpCode import OpCode


class Trac42Program:
    def __init__(self):
        self.__program = list()

    def link(self):
        link_map = {}
        for i in range(len(self.__program)):
            if self.__program[i].get_op_code() == OpCode.LABEL:
                link_map[self.__program[i].target] = i

        for instruction in self.__program:
            if instruction.get_op_code() == OpCode.BSR or instruction.get_op_code() == OpCode.BRF or \
                    instruction.get_op_code() == OpCode.BRA:
                instruction.target = link_map[instruction.target]

    def emit(self, instruction: Instruction):
        self.__program.append(instruction)

    def __str__(self):
        out = ""
        for i in range(len(self.__program)):
            out += str(i)+"\t"+str(self.__program[i])+"\n"
        return out
