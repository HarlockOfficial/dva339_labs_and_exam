using System;
using System.Collections.Generic;
using System.Text;

namespace LectureLanguage
{

    public enum Type { NumType, BoolType }

    public class AbstractSyntaxException : Exception
    {
        public AbstractSyntaxException()
        {
        }

        public AbstractSyntaxException(string msg) : base(msg)
        {
        }
    }

    public abstract partial class Expression
    {
        public int Line;
        public int Column;

        public void SetLocation(QUT.Gppg.LexLocation loc)
        {
            Line = loc.StartLine;
            Column = loc.StartColumn;
        }

    }

    public partial class LetExpression : Expression
    {
        public string Name;
        public Expression Expression;
        public Expression Recipient;

        public LetExpression(string name, Expression expression, Expression recipient)
        {
            Name = name;
            Expression = expression;
            Recipient = recipient;
        }
    }


    public partial class LiftedFunctionExpression : Expression
    {
        public string Name;
        public List<string> ArgumentNames;
        public Type ReturnType;
        public Expression Body;

        public LiftedFunctionExpression(string name, List<string> argumentNames, Type returnType, Expression body)
        {
            Name = name;
            ArgumentNames = argumentNames;
            ReturnType = returnType;
            Body = body;
        }

        public override int Evaluate(EvaluationState state)
        {
            throw new NotImplementedException();
        }

        public override void Prepass(PrepassState state)
        {
            throw new NotImplementedException();
        }

        public override Type Typecheck(TypecheckingState state)
        {
            throw new NotImplementedException();
        }
    }


    public partial class LetRecExpression : Expression
    {
        public string Name;
        public string ArgumentName;
        public Type ArgumentType;
        public Type ReturnType;
        public Expression Body;
        public Expression Recipient;

        public LetRecExpression(string name, string argumentName, string argumentType, string returnType, Expression body, Expression recipient)
        {
            Name = name;
            ArgumentName = argumentName;

            switch (argumentType)
            {
                case "num": ArgumentType = Type.NumType; break;
                case "bool": ArgumentType = Type.BoolType; break;
                default: throw new ImpossibleException();
            }

            switch (returnType)
            {
                case "num": ReturnType = Type.NumType; break;
                case "bool": ReturnType = Type.BoolType; break;
                default: throw new ImpossibleException();
            }


            Body = body;
            Recipient = recipient;
        }
    }

    public partial class LiftedFunctionCallExpression : Expression
    {
        public string Name;
        public List<Expression> Arguments;

        public LiftedFunctionCallExpression(string name, List<Expression> arguments)
        {
            Name = name;
            Arguments = arguments;
        }

        public override int Evaluate(EvaluationState state)
        {
            throw new NotImplementedException();
        }

        public override void Prepass(PrepassState state)
        {
            throw new NotImplementedException();
        }

        public override Type Typecheck(TypecheckingState state)
        {
            throw new NotImplementedException();
        }
    }

    // 

    public partial class ApplicationExpression : Expression
    {
        public string Name;
        public Expression Argument;

        public ApplicationExpression(string name, Expression argument)
        {
            Name = name;
            Argument = argument;
        }
    }

    public partial class SequenceExpression : Expression
    {
        public Expression Expression1;
        public Expression Expression2;

        public SequenceExpression(Expression expression1, Expression expression2)
        {
            Expression1 = expression1;
            Expression2 = expression2;
        }
    }

    public enum BinaryOperator { Add, Sub, Eq, Lt }

    public partial class BinaryOperatorExpression : Expression
    {
        public BinaryOperator Operator;
        public Expression Expression1;
        public Expression Expression2;

        public BinaryOperatorExpression(BinaryOperator op, Expression expression1, Expression expression2)
        {
            Operator = op;
            Expression1 = expression1;
            Expression2 = expression2;
        }
    }

    public partial class VariableExpression : Expression
    {
        public string Name;

        public VariableExpression(string name)
        {
            Name = name;
        }

    }

    public partial class NumberExpression : Expression
    {
        public int Value;

        public NumberExpression(string value)
        {
            Value = Convert.ToInt32(value);
        }

    }

    public partial class BoolExpression : Expression
    {
        public bool Value;

        public BoolExpression(string value)
        {
            switch (value)
            {
                case "true": Value = true; break;
                case "false": Value = false; break;
                default: throw new ImpossibleException();
            }
        }

    }

}
