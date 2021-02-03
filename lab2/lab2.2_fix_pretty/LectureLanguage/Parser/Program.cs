using System;
using System.IO;
using System.Text;

namespace Parser
{
    class Program
    {
        static void Main(string[] args)
        {
            var prg = "(let f x = 1 in let g y = y in (f (g 1), x, y, g)) + 1, 5, 6, 7 ";
            var data = Encoding.ASCII.GetBytes(prg);
            var stream = new MemoryStream(data, 0, data.Length);

            var l = new Scanner(stream);
            var p = new Parser(l);

            Console.WriteLine(p.Parse());
            Console.WriteLine(p.Program);

       

        }
    }
}
