from Parser import *
from Parser.sly import Parser
from AbstractSyntax import *


class MyParser(Parser):

    def __init__(self, token__list):
        self.__token_list = token__list

    # Get the token list from the lexer
    tokens = MyLexer.tokens
    # debugfile = 'parser.out'
    precedence = (
        ('right', ASSIGN),
        ('left', OR),
        ('left', AND),
        ('left', EQUALS, DIFFERENT),
        ('left', LOWER, GREATER, LOWEREQUAL, GREATEREQUAL),
        ('left', PLUS, MINUS),
        ('left', MULTIPLY, DIVIDE, MODULUS),
        ('nonassoc', NOT, UMINUS)
    )

    # Grammar rules and actions
    @_('Decls')
    def Program(self, p):
        if len(p) == 0:
            return "", True
        if p[0] is None:
            return "", False
        return p[0], True

    @_('Decl Decls', '')
    def Decls(self, p):
        if len(p) == 0:
            return ""
        if len(p) == 2:
            return SequenceStatement(p[0], p[1])
        return p[0]

    @_('Type IDENTIFIER LEFTROUNDPARENTHESES FormalList RIGHTROUNDPARENTHESES LEFTCURLYBRACKET Stmts RIGHTCURLYBRACKET',
       'VOID IDENTIFIER LEFTROUNDPARENTHESES FormalList RIGHTROUNDPARENTHESES LEFTCURLYBRACKET Stmts RIGHTCURLYBRACKET')
    def Decl(self, p):
        return FunctionDeclaration(p[0], IdentifierExpression(p[1]), p[3], p[6])

    @_('Type IDENTIFIER Identifiers', '')
    def FormalList(self, p):
        if len(p) == 0:
            return None
        if len(p) == 3:
            return IdentifierList(p[0], IdentifierExpression(p[1]), p[2])
        return IdentifierList(p[0], IdentifierExpression(p[1]))

    @_('COMMA Type IDENTIFIER Identifiers', '')
    def Identifiers(self, p):
        if len(p) == 0:
            return None
        if len(p) == 4:
            return IdentifierList(p[1], IdentifierExpression(p[2]), p[3])
        return IdentifierList(p[1], IdentifierExpression(p[2]))

    @_('INT', 'BOOL')
    def Type(self, p):
        return p[0]

    @_('LEFTCURLYBRACKET Stmts RIGHTCURLYBRACKET')
    def Stmt(self, p):
        return BlockStatement(p[1])

    @_('')
    def Stmt(self, p):
        return None

    @_('Expr SEMICOLON')
    def Stmt(self, p):
        return SingleExpression(p[0])

    @_('Type IDENTIFIER SEMICOLON')
    def Stmt(self, p):
        return DefinitionStatement(p[0], IdentifierExpression(p[1]))

    @_('RETURN Expr SEMICOLON', 'RETURN SEMICOLON')
    def Stmt(self, p):
        if len(p) == 3:
            return ReturnStatement(p[1])
        return ReturnStatement()

    @_('IF LEFTROUNDPARENTHESES Expr RIGHTROUNDPARENTHESES Stmt',
       'IF LEFTROUNDPARENTHESES Expr RIGHTROUNDPARENTHESES Stmt ELSE Stmt')
    def Stmt(self, p):
        if len(p) == 7:
            return IfStatement(p[2], p[4], p[6])
        return IfStatement(p[2], p[4])

    @_('WHILE LEFTROUNDPARENTHESES Expr RIGHTROUNDPARENTHESES Stmt')
    def Stmt(self, p):
        return WhileStatement(p[2], p[4])

    @_('Stmts Stmt', '')
    def Stmts(self, p):
        if len(p) == 0:
            return None
        if len(p) == 2 and p[0] is not None and p[1] is not None:
            return SequenceStatement(p[0], p[1])
        if p[1] is not None:
            return SequenceStatement(p[1])
        if p[0] is not None:
            return SequenceStatement(p[0])

    @_('NUMBER')
    def Expr(self, p):
        return NumberExpression(p[0])

    @_('TRUE', 'FALSE')
    def Expr(self, p):
        return BooleanExpression(p[0])

    @_('IDENTIFIER ASSIGN Expr')
    def Expr(self, p):
        return AssignmentStatement(IdentifierExpression(p[0]), p[2])

    @_('Expr PLUS Expr', 'Expr MINUS Expr', 'Expr MULTIPLY Expr', 'Expr DIVIDE Expr', 'Expr EQUALS Expr',
       'Expr OR Expr', 'Expr AND Expr', 'Expr DIFFERENT Expr', 'Expr LOWEREQUAL Expr', 'Expr GREATEREQUAL Expr',
       'Expr LOWER Expr', 'Expr GREATER Expr', "Expr MODULUS Expr")
    def Expr(self, p):
        return BinaryOperatorExpression(BinaryOperatorType(p[1]), p[0], p[2])

    @_('NOT Expr', 'MINUS Expr %prec UMINUS')
    def Expr(self, p):
        return UnaryOperatorExpression(UnaryOperatorType(p[0]), p[1])

    @_('IDENTIFIER LEFTROUNDPARENTHESES ExprList RIGHTROUNDPARENTHESES')
    def Expr(self, p):
        return FunctionCallExpression(IdentifierExpression(p[0]), BlockExpression(p[2]))

    @_('IDENTIFIER')
    def Expr(self, p):
        return IdentifierExpression(p[0])

    @_('LEFTROUNDPARENTHESES Expr RIGHTROUNDPARENTHESES')
    def Expr(self, p):
        return BlockExpression(p[1])

    @_('Expr Expressions', '')
    def ExprList(self, p):
        if len(p) == 0:
            return None
        return SeparatorExpression(p[0], p[1])

    @_('COMMA Expr Expressions', '')
    def Expressions(self, p):
        if len(p) == 0:
            return None
        return SeparatorExpression(p[1], p[2])

    def error(self, token):
        if token:
            print(f'Syntax error, unespected {token.value} on line {token.lineno} column {token.index}')
        else:
            # EOF reached
            last_element = self.__token_list[-1]
            print(f'Syntax error, unexpected EOF on line {last_element.lineno} column {last_element.index+1}.')
        exit(-2)
