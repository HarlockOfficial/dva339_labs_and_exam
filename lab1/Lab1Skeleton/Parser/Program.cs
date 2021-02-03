using System;
using System.IO;
using System.Diagnostics;

namespace Parser
{
	class MainClass
	{
		
		public static void Main(string[] args)
		{
			if (args.Length < 1)
			{
				Console.WriteLine("Usage; {0} [-t | <filename>]", Process.GetCurrentProcess().ProcessName);
				return;
			}

			try
			{
				StreamReader input;

				if (args[0] == "-t")
				{
					input = new StreamReader(Console.OpenStandardInput());
				}
				else
				{
					input = new StreamReader(args[0]);
				}

				string program = input.ReadToEnd();
				var parser = new Parser(program);
				var ast = parser.Parse();
				Console.WriteLine(ast);
			}
			catch (Exception e)
			{
				Console.WriteLine(e.Message);
			}

		}
	}
}
