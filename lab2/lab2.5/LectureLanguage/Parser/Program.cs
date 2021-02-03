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
            //var prg = "let f x : num -> num = x + 2 in let x = 5 in f x + true == 11";

            var prg = "let f x : num -> num = let g z : num -> num = z + x + 2 in g 15 in let x = 5 in f x == 8";

            var data = Encoding.ASCII.GetBytes(prg);
            var stream = new MemoryStream(data, 0, data.Length);

            var l = new Scanner(stream);
            var p = new Parser(l);

            if (p.Parse())
            {
                try
                {
                    p.Program.Prepass();
                    Console.WriteLine("--------------------------------------------------------------------------------");


                    // var value = p.Program.Evaluate();
                    // Console.WriteLine(value);

                    var type = p.Program.Typecheck();
                    Console.WriteLine(type + "\n");

                    var lifted = p.Program.Lift();
                    Console.WriteLine(lifted + "\n");

                    var t42 = lifted.Compile();
                    Console.WriteLine(t42 + "\n");

                    t42.Link();
                    Console.WriteLine(t42 + "\n");

                }
                catch (Exception e)
                {
                    Console.WriteLine(e.Message);
                }

            }
        }
    }
}
