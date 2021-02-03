using System;
using System.Collections.Generic;

using Lexer;

namespace Parser
{
	public class Parser
	{
		Lexer.Lexer lexer;

		public Parser(string prg)
		{
			lexer = new Lexer.Lexer(prg);
		}

		public Parser(Lexer.Lexer lexer)
		{
			this.lexer = lexer;
		}

		public Statement Parse()
		{
			throw new NotImplementedException();
		}


	}
}
