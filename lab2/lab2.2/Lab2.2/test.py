import os
import subprocess
from main import parse, lex


def test_main():
    output = subprocess.Popen(["C:\\Users\\Admin\\Desktop\\university\\dva339\\lab2\\lab2.1\\Test2.1\\Test21.exe",
                               "./false.bat",
                               "1"],
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()[0].decode()
    p = output[output.find(")") + 1:].strip()
    pretty_parse_p = str(parse(lex(p))[0])
    pretty_parse_pretty_parse_p = str(parse(lex(pretty_parse_p))[0])
    return equals_program(p, pretty_parse_p), equals_program(pretty_parse_p, pretty_parse_pretty_parse_p), p


# TODO check if the parentheses are more then necessary
# TODO fix the outher scope and opposite
def strip_program(program_to_strip: list) -> list:
    i = 0
    while True:
        try:
            if program_to_strip[i].strip() == '':
                program_to_strip.pop(i)
            elif i > 0 and program_to_strip[i].strip() == '{':
                program_to_strip[i - 1] = program_to_strip[i - 1] + ' {'
                program_to_strip.pop(i)
            else:
                i += 1
        except IndexError:
            break
    return program_to_strip


def equals_program(program1: str, program2: str) -> bool:
    program2 = strip_program(program2.split('\n'))
    program1 = strip_program(program1.split('\n'))
    for line in program1:
        if len(program2) == 0 or line != program2.pop(0):
            return False
    return len(program2) == 0


if __name__ == "__main__":
    with open("false.bat", "w") as f:
        f.write("@echo off\necho 'false'")
    print("Process Started")
    for _ in range(100):
        res1, res2, program = test_main()
        if not (res1 and res2):
            print(program)
            break
    os.remove("false.bat")
