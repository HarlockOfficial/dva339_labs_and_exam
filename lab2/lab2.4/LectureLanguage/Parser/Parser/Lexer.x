﻿%namespace LectureLanguage
%using QUT.Gppg;
%option out:Generated/Lexer.cs

alpha [a-zA-Z]
digit [0-9]
alphanum {alpha}|{digit}

%%

" "|\n|\r	{}
//.*$		{}

"let"	{ return (int) Tokens.LET;  }
"in"	{ return (int) Tokens.IN;  }

"->"		{ return (int) Tokens.RARROW;  }
"="		{ return (int) Tokens.ASN;  }
"+"		{ return (int) Tokens.ADD;  }
"-"		{ return (int) Tokens.SUB;  }
"=="	{ return (int) Tokens.EQ;  }
"<"		{ return (int) Tokens.LT;  }
","		{ return (int) Tokens.COMMA;  }
"("		{ return (int) Tokens.LPAR;  }
")"		{ return (int) Tokens.RPAR;  }
":"		{ return (int) Tokens.COLON;  }

"num"|"bool" {
	yylval.Value = yytext;
	return (int) Tokens.TYPE;
}

"true"|"false" {
	yylval.Value = yytext;
	return (int) Tokens.BOOL;
}

{digit}+	{
	yylval.Value = yytext;
	return (int) Tokens.NUM;
}

{alpha}{alphanum}* {
	yylval.Value = yytext;
	return (int) Tokens.ID;
}

. {
	yylval.Value = yytext;
	return (int) Tokens.LEXERR;
}

%{
	yylloc = new LexLocation(tokLin, tokCol, tokELin, tokECol);
%}


%%

override public void yyerror(string msg, object[] args) {
	Console.WriteLine("{0} on line {1} column {2}", msg, yylloc.StartLine, yylloc.StartColumn);
}