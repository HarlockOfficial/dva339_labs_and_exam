using System;
using System.IO;


namespace Lexer
{
	class MainClass
	{
		public static void Main(string[] args)
		{
			var stdin = new StreamReader(Console.OpenStandardInput());
			var input = stdin.ReadToEnd();
			var lex = new Lexer(input);

			Token t;
			do
			{
				t = lex.Next();
				Console.Write(t + " ");
			} while (t.type != Token.Type.EOF);

			Console.Write("\n");
		}
	}
}
