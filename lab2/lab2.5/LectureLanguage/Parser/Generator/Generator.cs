using System;
using System.Collections.Generic;
using System.Text;

namespace LectureLanguage
{

    public class GeneratorState
    {
        public Dictionary<string, int> OffsetMap = new Dictionary<string, int>();
        public int NextOffset = -1;

        public void Bind(string name)
        {
            OffsetMap[name] = NextOffset;
            NextOffset--;
        }

        public int Lookup(string name)
        {
            return OffsetMap[name];
        }

        public void Unbind(string name)
        {
            OffsetMap.Remove(name);
            NextOffset++;
        }
    }

    public partial class ExpressionProgram
    {
        // List<LiftedFunctionExpression> Functions;
        // Expression MainExpression;

        public Trac42Program Compile()
        {
            var state = new GeneratorState();
            var program = new Trac42Program();
            Functions.ForEach(function => function.Compile(state, program));
            program.Emit(new Instruction(Instruction.OPCODE.LABEL, "main"));

            MainExpression.Compile(state, program);
            program.Emit(new Instruction(Instruction.OPCODE.END));
            return program;
        }
    }

    public abstract partial class Expression
    {
        // public int Line;
        // public int Column;



        public abstract void Compile(GeneratorState state, Trac42Program program);

    }

    public partial class LetExpression : Expression
    {
        // public string Name;
        // public Expression Expression;
        // public Expression Recipient;
        // public Type Type;

        public override void Compile(GeneratorState state, Trac42Program program)
        {
            program.Emit(new Instruction(Instruction.OPCODE.DECL, 1));
            state.Bind(Name);
            Expression.Compile(state, program);

            switch (Type)
            {
                case Type.BoolType:
                    program.Emit(new Instruction(Instruction.OPCODE.ASSBOOL));
                    break;
                case Type.NumType:
                    program.Emit(new Instruction(Instruction.OPCODE.ASSINT));
                    break;
            }

            Recipient.Compile(state, program);
            state.Unbind(Name);
            program.Emit(new Instruction(Instruction.OPCODE.POP, 1));

        }
    }

    public partial class LiftedFunctionExpression
    {
        // public string Name;
        // public List<string> ArgumentNames;
        // public Type ReturnType;
        // public Expression Body;

        public override void Compile(GeneratorState state, Trac42Program program)
        {
            program.Emit(new Instruction(Instruction.OPCODE.LABEL, Name));
            var argumentOffset = 2;

            foreach (var argumentName in ArgumentNames)
            {
                state.OffsetMap[argumentName] = argumentOffset;
                argumentOffset++;
            }
            var returnOffset = argumentOffset;

            program.Emit(new Instruction(Instruction.OPCODE.LINK));
            program.Emit(new Instruction(Instruction.OPCODE.LVAL, returnOffset));

            Body.Compile(state, program);

            switch (ReturnType)
            {
                case Type.BoolType:
                    program.Emit(new Instruction(Instruction.OPCODE.ASSBOOL));
                    break;
                case Type.NumType:
                    program.Emit(new Instruction(Instruction.OPCODE.ASSINT));
                    break;
            }

            program.Emit(new Instruction(Instruction.OPCODE.UNLINK));
            program.Emit(new Instruction(Instruction.OPCODE.RTS));

        }
    }

    public partial class LetRecExpression : Expression
    {
        // public string Name;
        // public string ArgumentName;
        // public Type ArgumentType;
        // public Type ReturnType;
        // public Expression Body;
        // public Expression Recipient;

        public override void Compile(GeneratorState state, Trac42Program program)
        {
            // not present after lift
            throw new NotImplementedException();
        }
    }

    public partial class LiftedFunctionCallExpression : Expression
    {
        // public string Name;
        // public List<Expression> Arguments;

        public override void Compile(GeneratorState state, Trac42Program program)
        {
            program.Emit(new Instruction(Instruction.OPCODE.DECL, 1));

            for (var i = Arguments.Count - 1; i >= 0; i--)
            {
                Arguments[i].Compile(state, program);
            }

            program.Emit(new Instruction(Instruction.OPCODE.BSR, Name));
            program.Emit(new Instruction(Instruction.OPCODE.POP, Arguments.Count));
        }
    }

    public partial class ApplicationExpression : Expression
    {
        // public string Name;
        // public Expression Argument;

        public override void Compile(GeneratorState state, Trac42Program program)
        {
            // not present after lift
            throw new NotImplementedException();
        }
    }

    public partial class SequenceExpression : Expression
    {
        // public Expression Expression1;
        // public Expression Expression2;

        public override void Compile(GeneratorState state, Trac42Program program)
        {
            Expression1.Compile(state, program);
            program.Emit(new Instruction(Instruction.OPCODE.POP, 1));
            Expression2.Compile(state, program);
        }
    }

    public partial class BinaryOperatorExpression : Expression
    {
        // public BinaryOperator Operator;
        // public Expression Expression1;
        // public Expression Expression2;

        public override void Compile(GeneratorState state, Trac42Program program)
        {
            Expression1.Compile(state, program);
            Expression2.Compile(state, program);

            switch (Operator)
            {
                case BinaryOperator.Add:
                    program.Emit(new Instruction(Instruction.OPCODE.ADD));
                    break;
                case BinaryOperator.Sub:
                    program.Emit(new Instruction(Instruction.OPCODE.SUB));
                    break;
                case BinaryOperator.Eq:
                    switch (OperandType)
                    {
                        case Type.BoolType:
                            program.Emit(new Instruction(Instruction.OPCODE.EQBOOL));
                            break;
                        case Type.NumType:
                            program.Emit(new Instruction(Instruction.OPCODE.EQINT));
                            break;
                    }
                    break;
                case BinaryOperator.Lt:
                    program.Emit(new Instruction(Instruction.OPCODE.LTINT));
                    break;
            }

        }
    }

    public partial class VariableExpression : Expression
    {
        // public string Name;

        public override void Compile(GeneratorState state, Trac42Program program)
        {
            var offset = state.Lookup(Name);
            switch (Type)
            {
                case Type.BoolType:
                    program.Emit(new Instruction(Instruction.OPCODE.RVALBOOL, offset));
                    break;
                case Type.NumType:
                    program.Emit(new Instruction(Instruction.OPCODE.RVALINT, offset));
                    break;
            }
        }
    }

    public partial class NumberExpression : Expression
    {
        // public int Value;

        public override void Compile(GeneratorState state, Trac42Program program)
        {
            program.Emit(new Instruction(Instruction.OPCODE.PUSHINT, Value));

        }
    }

    public partial class BoolExpression : Expression
    {
        // public bool Value;

        public override void Compile(GeneratorState state, Trac42Program program)
        {
            program.Emit(new Instruction(Instruction.OPCODE.PUSHBOOL, Value ? 1 : 0));
        }
    }

}
