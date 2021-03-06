import re
import sys

from Parser.MyLexer import MyLexer, find_column
from Parser.MyParser import MyParser
from Generator import ExpressionProgram
import TypeChecker
import Optimizer


def main():
    """if len(sys.argv) == 1:
        print(f"Usage; {sys.argv[0]} [-t | <file_name>]")
        return
    string = None
    if sys.argv[1] == "-t":
        string = sys.stdin.read()
    else:
        with open(sys.argv[1], "r") as f:
            string = f.read()
    if string is None:
        print("Unknown Error, try again")
        return"""
    string = """"""
    string = sys.stdin.read()
    # remove comments
    lines = ""
    string = re.split(r'\r\n|\r|\n', string.strip())
    for line in string:
        start = re.search("//", line)
        if start:
            lines += line[:start.span()[0]] + "\n"
        else:
            lines += line + "\n"
    # ---------------------------------------------------
    del line
    del start
    string = lines
    del lines
    abstract_syntax_tree = parse(lex(string))[0]
    del string
    if abstract_syntax_tree != "":
        abstract_syntax_tree.prepass()
        try:
            abstract_syntax_tree.typecheck()
            state = Optimizer.OptimizerState()
            while True:
                state.new_scope()
                abstract_syntax_tree.optimize(state)
                state.assign_constants_to_delete()
                if not state.start_again:
                    break
            for message in state.get_warnings():
                sys.stderr.write(message+"\n")
            variables_first_use = state.first_uses
            del state
            # print the optimized source code
            # print(str(abstract_syntax_tree))
            # necessary only to obtain the function list from the typecheking state
            unused, type_checking_state = abstract_syntax_tree.typecheck()
            functions = {}
            for name in type_checking_state.get_all_functions():
                functions[name] = type_checking_state.lookup_function(name)
            del type_checking_state
            decls_count = abstract_syntax_tree.get_decl_count()
            del abstract_syntax_tree
            program = ExpressionProgram(functions, decls_count)
            compiled_program = program.compile(variables_first_use)
            del program
            del variables_first_use
            del decls_count
            compiled_program.link()
            # print the optimized assembly Trac42 code
            print(str(compiled_program))
            del compiled_program
        except TypeChecker.TypecheckerException as e:
            error = str(e)
            result = re.search(r'[0-9]+', error)
            line = ""
            column = ""
            if result is not None:
                line = error[result.start():result.end()]
                error = error[result.end():]
                result = re.search(r'[0-9]+', error)
                if result is not None:
                    column = error[result.start():result.end()]
            print("fail {0} {1} {2}".format(line, column, str(e)))
        """try:
            abstract_syntax_tree.evaluate()
        except EvaluatorException as e:
            print(e)"""


def lex(string: str) -> list:
    lexer = MyLexer()
    token_list = []
    for token in lexer.tokenize(string):
        token.index = find_column(string, token)
        token_list.append(token)
    return token_list


def parse(token_list: list) -> tuple:
    parser = MyParser(token_list)
    return parser.parse(iter(token_list))


if __name__ == "__main__":
    main()
