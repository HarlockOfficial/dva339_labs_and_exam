using System;
namespace Parser
{


    public class Expression
    {
        public int Line;
        public int Column;
        public void SetLocation(QUT.Gppg.LexLocation loc)
        {
            Line = loc.StartLine;
            Column = loc.StartColumn;
        }

    }

    public class LetExpression : Expression
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

    public class LetRecExpression : Expression
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

    public class SequenceExpression : Expression
    {
        public Expression Expression1;
        public Expression Expression2;

        public SequenceExpression(Expression expression1, Expression expression2)
        {
            Expression1 = expression1;
            Expression2 = expression2;
        }
    }

    public enum BinaryOperator { Add, Sub, Mul, Div };

    public class BinaryOperatorExpression : Expression
    {
        public Expression Expression1;
        public Expression Expression2;
        public BinaryOperator Operator;

        public BinaryOperatorExpression(Expression expression1, Expression expression2, BinaryOperator op)
        {
            Expression1 = expression1;
            Expression2 = expression2;
            Operator = op;
        }
    }

    public class ApplicationExpression : Expression
    {
        public string Name;
        public Expression Argument;

        public ApplicationExpression(string name, Expression argument)
        {
            Name = name;
            Argument = argument;
        }
    }

    public class VariableExpression : Expression
    {
        public string Name;

        public VariableExpression(string name)
        {
            Name = name;
        }
    }

    public class NumberExpression : Expression
    {
        public int Value;

        public NumberExpression(string value)
        {
            Value = Convert.ToInt32(value); 
        }

    }
}
