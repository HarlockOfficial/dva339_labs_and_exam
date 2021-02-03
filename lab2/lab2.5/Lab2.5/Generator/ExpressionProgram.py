from typing import List, Tuple, Dict

import AbstractSyntax
from Generator import Trac42Program, GeneratorState, OpCode, Instruction, CompilerException
import TypeChecker


class ExpressionProgram:
    # functions contains function name -> (Return Type, List[Parameter Type, Parameter Name], Body, line, column)
    def __init__(self, functions: Dict[str, Tuple["TypeChecker.Types", List[Tuple["TypeChecker.Types", str]],
                                                  "AbstractSyntax.Statement", int, int]]):
        self.__functions = functions

    def compile(self) -> Trac42Program:
        state = GeneratorState()
        program = Trac42Program()

        # used to add function to labels list, should not change function names
        for name in self.__functions.keys():
            state.rename_label(name)

        for name in self.__functions.keys():
            if state.lookup_label(name) != name:
                raise CompilerException("Multiple function have same name")

        state.lookup_label("main")  # will throw exception if main not present

        program.emit(Instruction(OpCode.DECL, 1))
        program.emit(Instruction(OpCode.BSR, target="main"))
        program.emit(Instruction(OpCode.END))

        for name in self.__functions.keys():
            state.next_offset = -1
            state.offset_map = {}
            ret_type, params, body, unused, unused = self.__functions[name]
            program.emit(Instruction(OpCode.LABEL, target=name))
            argument_offset = 2
            for unused, param_name in params:
                state.offset_map[param_name] = argument_offset
                argument_offset += 1
            return_offset = argument_offset
            state.offset_map["return"] = return_offset
            program.emit(Instruction(OpCode.LINK))
            program.emit(Instruction(OpCode.LVAL, return_offset))
            body.compile(state, program)
            if ret_type == TypeChecker.Types.BOOL:
                program.emit(Instruction(OpCode.ASSBOOL))
            elif ret_type == TypeChecker.Types.INT:
                program.emit(Instruction(OpCode.ASSINT))
            program.emit(Instruction(OpCode.UNLINK))
            program.emit(Instruction(OpCode.RTS))

        return program
