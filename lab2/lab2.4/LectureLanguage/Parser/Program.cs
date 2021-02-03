using System;
using System.IO;
using System.Text;

namespace LectureLanguage
{
    class Program
    {
        // let rec f x = .. .and g x = ... in
        static void Main(string[] args)
        {
            var prg = "let f x : bool -> num = x + 2 in let x = 5 in f x + true == 11";
            var data = Encoding.ASCII.GetBytes(prg);
            var stream = new MemoryStream(data, 0, data.Length);

            var l = new Scanner(stream);
            var p = new Parser(l);

            if (p.Parse())
            {
                try
                {
                    p.Program.Prepass();

                    // var value = p.Program.Evaluate();
                    // Console.WriteLine(value);

                    var type = p.Program.Typecheck();
                    Console.WriteLine(type);
                } catch (Exception e)
                {
                    Console.WriteLine(e.Message);
                }
            }
        }
    }
}
