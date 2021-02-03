from typing import Union

from Generator.OpCode import OpCode


class Instruction:
    def __init__(self, op_code: OpCode, argument: Union[int, str] = None, target: str = None):
        self.__op_code = op_code
        self.__argument = argument
        self.target = target

    def get_op_code(self):
        return self.__op_code

    def __str__(self):
        if self.__op_code == OpCode.LABEL:
            return "[" + str(self.target) + "]"
        elif self.__op_code == OpCode.BSR or self.__op_code == OpCode.BRF or self.__op_code == OpCode.BRA:
            return str(self.__op_code.value) + " " + str(self.target)
        else:
            out = str(self.__op_code.value) + " "
            if not (self.__op_code == OpCode.ASSINT or self.__op_code == OpCode.ASSBOOL or self.__op_code == OpCode.ADD
                    or self.__op_code == OpCode.SUB or self.__op_code == OpCode.EQINT or self.__op_code == OpCode.LTINT
                    or self.__op_code == OpCode.WRITEINT or self.__op_code == OpCode.WRITEBOOL or
                    self.__op_code == OpCode.LINK or self.__op_code == OpCode.UNLINK or self.__op_code == OpCode.RTS or
                    self.__op_code == OpCode.END or self.__op_code == OpCode.NOT or self.__op_code == OpCode.NEG or
                    self.__op_code == OpCode.OR or self.__op_code == OpCode.LEINT or self.__op_code == OpCode.MULT or
                    self.__op_code == OpCode.DIV or self.__op_code == OpCode.AND):
                out += str(self.__argument)
                if self.__op_code == OpCode.LVAL or self.__op_code == OpCode.RVALINT or \
                        self.__op_code == OpCode.RVALBOOL:
                    out += "(FP)"
                elif not (self.__op_code == OpCode.PUSHINT or self.__op_code == OpCode.PUSHBOOL or
                          self.__op_code == OpCode.POP or self.__op_code == OpCode.DECL):
                    raise Exception("Impossible exception in Instruction")
            return out
