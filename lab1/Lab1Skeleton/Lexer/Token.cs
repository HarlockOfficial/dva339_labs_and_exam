using System;

namespace Lexer
{
	public class Token 
	{
		public Type type;
		public string lexeme;

		public int line;
		public int column;

		public enum Type { KEYW, SEP, OP, ID, NUM, EOF };

		public Token(Type type, string lexeme, int line, int column)
		{
			this.type = type;
			this.lexeme = lexeme;
			this.line = line;
			this.column = column;
		}

		override public string ToString()
		{
			if (lexeme != null) { return string.Format("{0} {1} {2} {3}", type, lexeme, line, column); }
			return string.Format("{0} {1} {2}", type, line, column);
		}

	}
}
