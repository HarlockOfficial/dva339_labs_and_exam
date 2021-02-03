using System;
using System.Collections.Generic;
using System.Text;

namespace LectureLanguage
{

    public class Trac42Program
    {
        public List<Instruction> Program = new List<Instruction>();

        public void Link()
        {
            var linkMap = new Dictionary<string, int>();
            for (var i = 0; i < Program.Count; i++)
            {
                if (Program[i].opcode == Instruction.OPCODE.LABEL)
                {
                    linkMap[Program[i].target] = i;
                }
            }

            Program.ForEach(instruction =>
            {
                switch (instruction.opcode)
                {
                    case Instruction.OPCODE.BSR:
                    case Instruction.OPCODE.BRF:
                    case Instruction.OPCODE.BRA:
                        instruction.target = linkMap[instruction.target].ToString();
                        break;
                }

            });
        }

        public void Emit(Instruction instruction)
        {
            Program.Add(instruction);
        }

        public override string ToString()
        {
            var b = new StringBuilder();
            for (var i = 0; i < Program.Count; i++)
            {
                b.Append($"{i}\t{Program[i]}\n");
            }
            return b.ToString();
        }
    }

    public class Instruction
    {
        public enum OPCODE
        {
            PUSHINT, PUSHBOOL, LVAL, RVALINT, RVALBOOL, ASSINT,
            ASSBOOL, ADD, SUB, EQBOOL, EQINT, LTINT, DECL, POP, BRF, BRA, WRITEINT,
            LINK, UNLINK, RTS, BSR, END,
            LABEL
        }

        public OPCODE opcode;
        public int argument;
        public string target;

        public Instruction(OPCODE opcode)
        {
            this.opcode = opcode;
        }

        public Instruction(OPCODE opcode, int argument)
        {
            this.opcode = opcode;
            this.argument = argument;
        }

        public Instruction(OPCODE opcode, string target)
        {
            this.opcode = opcode;
            this.target = target;
        }

        override public string ToString()
        {
            switch (opcode)
            {
                case OPCODE.LABEL:
                    return $"[{target}]";

                case OPCODE.BSR:
                    return opcode.ToString() + " " + target;

                case OPCODE.PUSHINT:
                case OPCODE.PUSHBOOL:

                case OPCODE.POP:
                case OPCODE.BRF:
                case OPCODE.BRA:
                case OPCODE.DECL:
                    return opcode.ToString() + " " + argument.ToString();

                case OPCODE.LVAL:
                case OPCODE.RVALINT:
                case OPCODE.RVALBOOL:
                    return opcode.ToString() + " " + argument.ToString() + "(FP)";


                case OPCODE.ASSINT:
                case OPCODE.ASSBOOL:
                case OPCODE.ADD:
                case OPCODE.SUB:
                case OPCODE.EQINT:
                case OPCODE.LTINT:
                case OPCODE.WRITEINT:
                case OPCODE.LINK:
                case OPCODE.UNLINK:
                case OPCODE.RTS:
                case OPCODE.END:

                    return opcode.ToString() + " ";
            }

            throw new NotImplementedException();
        }
    }
}
