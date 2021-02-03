using System;
using System.IO;
using System.Text;

namespace Parser
{
    class MainClass
    {
        public static void Main(string[] args)
        {
            var prg = "let x = 1 in x + 1";
            var data = Encoding.ASCII.GetBytes(prg);
            MemoryStream stream = new MemoryStream(data, 0, data.Length);
            Scanner l = new Scanner(stream);
            Parser p = new Parser(l);
            if (p.Parse())
            {
                Console.WriteLine(p.Program.ToString());
            }
        }
    }
}
