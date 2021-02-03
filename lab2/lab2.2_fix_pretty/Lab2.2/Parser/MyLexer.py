import re

from Parser.sly import Lexer


class MyLexer(Lexer):
    # Set of token names.   This is always required
    tokens = {IDENTIFIER, IF, ELSE, WHILE, RETURN, INT, BOOL, VOID, TRUE, FALSE, LEFTROUNDPARENTHESES, RIGHTROUNDPARENTHESES,
              LEFTCURLYBRACKET, RIGHTCURLYBRACKET, SEMICOLON, COMMA, EQUALS, OR, AND, DIFFERENT, LOWEREQUAL,
              GREATEREQUAL, LOWER, GREATER, PLUS, MINUS, MULTIPLY, DIVIDE, MODULUS, NOT, ASSIGN, NUMBER}

    # Regular expression rules for tokens
    IDENTIFIER = r'[a-zA-Z_][a-zA-Z0-9_]*'
    IDENTIFIER['if'] = IF
    IDENTIFIER['else'] = ELSE
    IDENTIFIER['while'] = WHILE
    IDENTIFIER['return'] = RETURN
    IDENTIFIER['int'] = INT
    IDENTIFIER['bool'] = BOOL
    IDENTIFIER['void'] = VOID
    IDENTIFIER['true'] = TRUE
    IDENTIFIER['false'] = FALSE
    LEFTROUNDPARENTHESES = r'\('
    RIGHTROUNDPARENTHESES = r'\)'
    LEFTCURLYBRACKET = r'\{'
    RIGHTCURLYBRACKET = r'\}'
    SEMICOLON = r';'
    COMMA = r','
    EQUALS = r'=='
    OR = r'\|\|'
    AND = r'&&'
    DIFFERENT = r'!='
    LOWEREQUAL = r'<='
    GREATEREQUAL = r'>='
    LOWER = r'<'
    GREATER = r'>'
    PLUS = r'\+'
    MINUS = r'-'
    MULTIPLY = r'\*'
    DIVIDE = r'/'
    MODULUS = r'%'
    NOT = r'!'
    ASSIGN = '='
    NUMBER = r'[0-9]+'

    # ignored patterns
    ignore_comment = r'//.*'
    ignore_newline = r'\r\n|\r|\n'
    ignore_tab = r'\t'
    ignore_spaces = r' '

    @_(r'\r\n', r'\r', r'\n')
    def ignore_newline(self, t):
        self.lineno += len(t.value)

    # Error handling rule
    def error(self, t):
        print("Illegal character '{0}' on line {1}".format(t.value[0], self.lineno))
        exit(-1)


def find_column(string, token):
    split = re.split(r'\r\n|\r|\n', string[:token.index])  # divide by lines until start of the token
    string = split[len(split)-1]  # taken line before the token start
    string = re.sub(r'\t', '        ', string)  # replaced tabs with 8 spaces (if present)
    return len(string) + 1  # token starting position = length of the string before the token + 1
