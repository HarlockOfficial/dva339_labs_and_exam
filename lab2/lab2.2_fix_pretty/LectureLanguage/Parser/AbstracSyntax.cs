using System;
using System.Collections.Generic;
using System.Text;

namespace Parser
{
    public abstract partial class Expression
    {
        public int Line;
        public int Column;

        public void SetLocation(QUT.Gppg.LexLocation loc)
        {
            Line = loc.StartLine;
            Column = loc.StartColumn;
        }

        public override string ToString()
        {
            var builder = new PrettyBuilder();
            Pretty(builder);
            return builder.ToString();
        }

        public void Pretty(PrettyBuilder builder)
        {
            Pretty(builder, 0, false);
        }

        public abstract void Pretty(PrettyBuilder builder, int outerPrecedence, bool opposite);

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


    public partial class LetRecExpression : Expression
    {
        public string Name;
        public string ArgumentName;
        public Expression Body;
        public Expression Recipient;

        public LetRecExpression(string name, string argumentName, Expression body, Expression recipient)
        {
            Name = name;
            ArgumentName = argumentName;
            Body = body;
            Recipient = recipient;
        }
    }

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

    public enum BinaryOperator { Add, Sub, Mul, Div }
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
        public string Value;

        public NumberExpression(string value)
        {
            Value = value;
        }

    }



}
