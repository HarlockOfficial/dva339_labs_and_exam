from typing import Union
import Optimizer


class OptimizerState:
    def __init__(self):
        self.__variables = None
        self.__constants = None
        self.__params = None
        self.__constants_to_delete = None
        self.__warning_list = list()
        self.first_uses = dict()
        self.start_again = False
        self.ignore_next = -1
        self.__lookup_variable = False
        self.__decl_count = 0
        self.is_last_return = False
        self.new_scope()

    def new_scope(self):
        self.start_again = False
        self.__variables = dict()
        self.__constants = dict()
        self.__params = dict()
        self.ignore_next = -1
        self.__decl_count = 0
        self.is_last_return = False

    def inc_decl(self):
        self.__decl_count += 1

    def get_decl(self):
        var = self.__decl_count
        self.__decl_count = 0
        return var

    def set_lookup_variable(self):
        self.__lookup_variable = True

    def unset_lookup_variable(self):
        self.__lookup_variable = False

    def bind(self, var: str, val: Union[int, bool, None], val_type: str, use: "Optimizer.FirstUseType" = None):
        if use is None:
            use = Optimizer.FirstUseType.UNUSED
        if var in self.__variables.keys() and self.__variables[var][2] != Optimizer.FirstUseType.UNUSED:
            use = self.__variables[var][2]
        if var in self.__constants.keys() and self.__constants[var] is not None:
            del self.__constants[var]
        else:
            # type consistency checked by the typechecker, variable type cannot change
            self.__constants[var] = (val, val_type, use)
        if var in self.__params.keys():
            self.__params[var] = (val, val_type, use)
        self.__variables[var] = (val, val_type, use)

    def bind_param(self, var: str, val_type: str):
        self.__params[var] = (None, val_type, Optimizer.FirstUseType.UNUSED)
        self.__variables[var] = (None, val_type, Optimizer.FirstUseType.UNUSED)

    def bind_first_use(self, var: str, use: "Optimizer.FirstUseType"):
        tmp = self.__variables[var]
        if tmp[2] == Optimizer.FirstUseType.UNUSED:
            tmp = (tmp[0], tmp[1], use)
            self.__variables[var] = tmp
            if var in self.__constants.keys():
                self.__constants[var] = tmp

    def lookup(self, var: str) -> Union[int, bool]:
        if self.__variables[var][0] is None:
            if self.__variables[var][1] == "int":
                return 0
            return False
        return self.__variables[var][0]

    def lookup_constant(self, var: str) -> Union[int, bool]:
        if self.__lookup_variable:
            self.__lookup_variable = False
            if var not in self.__params.keys():
                return self.lookup(var)
        if var in self.__constants.keys():
            if self.__constants[var][0] is None:
                if self.__constants[var][1] == "int":
                    return 0
                return False
            return self.__constants[var][0]
        raise OptimizerStateException("Constant {0} not found".format(var))

    def assign_constants_to_delete(self):
        if len(self.__constants.keys()) > 0:
            self.start_again = True
        tmp = dict()
        for key in self.__variables.keys():
            if self.__variables[key][2] != Optimizer.FirstUseType.UNUSED:
                tmp[key] = self.__variables[key][2]
        self.first_uses = tmp
        self.__constants_to_delete = self.__constants

    def is_del_variable(self, var: str) -> bool:
        if self.__constants_to_delete is None:
            return False
        if var in self.__constants_to_delete.keys() and var not in self.__params.keys():
            return True
        return False

    def del_costant(self, var: str):
        if var in self.__constants.keys():
            del self.__constants[var]
        if var not in self.__variables.keys():
            raise Exception("Impossible delete of undefined varaible")

    def add_warning(self, msg: str):
        if msg not in self.__warning_list:
            self.__warning_list.append(msg)

    def get_warnings(self):
        return self.__warning_list

    def get_constant_identifiers(self):
        return self.__constants.keys()


class OptimizerStateException(Exception):
    pass
