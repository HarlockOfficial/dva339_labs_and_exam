%output=Generated/Parser.cs
%namespace Parser

%union {
	public string Value;
	public Expression Expression;
}

%token <Value> ID
%token <Value> NUM
%token <Value> LEXERR

%token LET "let"
%token IN "in"

%token ASN "="
%token ADD "+"
%token SUB "-"
%token MUL "*"
%token DIV "/"
%token COMMA ","
%token LPAR "("
%token RPAR ")"

%type <Expression> E, E1, E2, E3, E4, E5

%start P

%%

P : E EOF						{ Program = $1; }
  ;

E: E "," E1					    { $$ = new SequenceExpression($1, $3); $$.SetLocation(@$); }
  | E1							{ $$ = $1; }
  ;

E1 : "let" ID "=" E "in" E1		{ $$ = new LetExpression($2, $4, $6); $$.SetLocation(@$); }
  | "let" ID ID "=" E "in" E1   { $$ = new LetRecExpression($2, $3, $5, $7); $$.SetLocation(@$); }
  | E2							{ $$ = $1; }
  ;

E2: E2 "+" E3					{ $$ = new BinaryOperatorExpression(BinaryOperator.Add, $1, $3); $$.SetLocation(@$); }
  | E2 "-" E3					{ $$ = new BinaryOperatorExpression(BinaryOperator.Sub, $1, $3); $$.SetLocation(@$); }
  | E3							{ $$ = $1; }
  ;

E3: E3 "*" E4					{ $$ = new BinaryOperatorExpression(BinaryOperator.Mul, $1, $3); $$.SetLocation(@$); }
  | E3 "/" E4					{ $$ = new BinaryOperatorExpression(BinaryOperator.Div, $1, $3); $$.SetLocation(@$); }
  | E4							{ $$ = $1; }
  ;

E4: ID E5					    { $$ = new ApplicationExpression($1, $2); $$.SetLocation(@$); }
  | E5							{ $$ = $1; }
  ;

E5: "(" E ")"					{ $$ = $2; }
  | ID							{ $$ = new VariableExpression($1); $$.SetLocation(@$); }
  | NUM							{ $$ = new NumberExpression($1); $$.SetLocation(@$); }
  ;

%%

public Expression Program;

public Parser(Scanner s) : base(s) { }