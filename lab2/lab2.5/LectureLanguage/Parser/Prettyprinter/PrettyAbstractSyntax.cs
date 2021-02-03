using System;
using System.Collections.Generic;
using System.Text;

namespace LectureLanguage
{


    public partial class ExpressionProgram
    {
        // List<LiftedFunctionExpression> Functions;
        // Expression MainExpression;

        public override string ToString()
        {
            var builder = new PrettyBuilder();
            Functions.ForEach(
                function => {
                    function.Pretty(builder);
                    builder.NewLine();
            });
            MainExpression.Pretty(builder);
            return builder.ToString();
        }

    }

    public partial class Expression
    {
        // public int Line;
        // public int Column;

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

        // prec: 1
        public partial class LetExpression : Expression
    {
        // public string Name;
        // public Expression Expression;
        // public Expression Recipient;

        override public void Pretty(PrettyBuilder builder, int outerPrecedence, bool opposite)
        {
            if (outerPrecedence > 1)
            {
                builder.Append("(");
            }

            builder.Append($"let {Name} = ");
            Expression.Pretty(builder, 1, false);
            builder.Append(" in ");
            Recipient.Pretty(builder, 1, false);

            if (outerPrecedence > 1)
            {
                builder.Append(")");
            }
        }

    }

    public partial class LiftedFunctionExpression : Expression
    {
        // public string Name;
        // public List<string> ArgumentNames;
        // public List<Type> ArgumentTypes;
        // public Type ReturnType;
        // public Expression Body;
      

        public override void Pretty(PrettyBuilder builder, int outerPrecedence, bool opposite)
        {
            if (outerPrecedence > 1)
            {
                builder.Append("(");
            }

            builder.Append($"let {Name} ");
            for (var i = 0; i < ArgumentNames.Count; i++)
            {
                builder.Append($"{ArgumentNames[i]} ");
            }
            builder.Append($"= ");

           Body.Pretty(builder, 1, false);

            if (outerPrecedence > 1)
            {
                builder.Append(")");
            }
        }
    }


    public partial class LetRecExpression : Expression
    {
        // public string Name;
        // public string ArgumentName;
        // public Type ArgumentType
        // public Type ReturnType
        // public Expression Body;
        // public Expression Recipient;

        override public void Pretty(PrettyBuilder builder, int outerPrecedence, bool opposite)
        {
            if (outerPrecedence > 1)
            {
                builder.Append("(");
            }

            builder.Append($"let {Name} {ArgumentName} : {ArgumentType} -> {ReturnType} = ");
            Body.Pretty(builder, 1, false);
            builder.Append(" in ");
            Recipient.Pretty(builder, 1, false);

            if (outerPrecedence > 1)
            {
                builder.Append(")");
            }
        }
    }

    public partial class LiftedFunctionCallExpression : Expression
    {
        // public string Name;
        // public List<Expression> Arguments;

        public override void Pretty(PrettyBuilder builder, int outerPrecedence, bool opposite)
        {
            if (outerPrecedence >= 4)
            {
                builder.Append("(");
            }

            builder.Append($"{Name}");
            Arguments.ForEach(argument =>
            {
                builder.Append(" ");
                argument.Pretty(builder, 4, false);
            });

            if (outerPrecedence >= 4)
            {
                builder.Append(")");
            }
        }
    }

    public partial class ApplicationExpression : Expression
    {
        // public string Name ;
        // public Expression Argument;

        override public void Pretty(PrettyBuilder builder, int outerPrecedence, bool opposite)
        {
            if (outerPrecedence >= 4)
            {
                builder.Append("(");
            }

            builder.Append($"{Name} ");
            Argument.Pretty(builder, 4, false);

            if (outerPrecedence >= 4)
            {
                builder.Append(")");
            }
        }
    }

    // prec 0
    public partial class SequenceExpression : Expression
    {
        // public Expression Expression1;
        // public Expression Expression2;

        override public void Pretty(PrettyBuilder builder, int outerPrecedence, bool opposite)
        {
            if (outerPrecedence > 0)
            {
                builder.Append("(");
                builder.Indent();
                builder.NewLine();
            }
            Expression1.Pretty(builder, 0, false);
            builder.Append(", ");
            builder.NewLine();
            Expression2.Pretty(builder, 0, false);
            if (outerPrecedence > 0)
            {
                builder.Unindent();
                builder.NewLine();
                builder.Append(")");
                builder.NewLine();
            }

        }
    }

    public partial class BinaryOperatorExpression : Expression
    {
        // public BinaryOperator Operator;
        // public Expression Expression1;
        // public Expression Expression2;

        static Dictionary<BinaryOperator, int> Precedences = new Dictionary<BinaryOperator, int>
        {
            { BinaryOperator.Add, 3 },
            { BinaryOperator.Sub, 3 },
            { BinaryOperator.Eq, 2 },
            { BinaryOperator.Lt, 2 }
        };

        static Dictionary<BinaryOperator, string> Strings = new Dictionary<BinaryOperator, string>
        {
            { BinaryOperator.Add, " + " },
            { BinaryOperator.Sub, " - " },
            { BinaryOperator.Eq, " == " },
            { BinaryOperator.Lt, " < " }
        };

        enum Associativity { Left, Right, Both }

        static Dictionary<BinaryOperator, Associativity> Associativities = new Dictionary<BinaryOperator, Associativity>
        {
            { BinaryOperator.Add, Associativity.Both },
            { BinaryOperator.Sub, Associativity.Left },
            { BinaryOperator.Eq, Associativity.Left },
            { BinaryOperator.Lt, Associativity.Left }
        };

        override public void Pretty(PrettyBuilder builder, int outerPrecedence, bool opposite)
        {
            var precedence = Precedences[Operator];
            var associativity = Associativities[Operator];

            if (outerPrecedence > precedence || opposite && outerPrecedence == precedence)
            {
                builder.Append("(");
            }

            Expression1.Pretty(builder, precedence, associativity == Associativity.Right);
            builder.Append(Strings[Operator]);
            Expression2.Pretty(builder, precedence, associativity == Associativity.Left);

            if (outerPrecedence > precedence || opposite && outerPrecedence == precedence)
            {
                builder.Append(")");
            }
        }
    }

    public partial class VariableExpression : Expression
    {
        // public string Name;

        override public void Pretty(PrettyBuilder builder, int outerPrecedence, bool opposite)
        {
            builder.Append(Name);
        }

    }

    public partial class NumberExpression : Expression
    {
        // public string Value;
        override public void Pretty(PrettyBuilder builder, int outerPrecedence, bool opposite)
        {
            builder.Append(Value.ToString());
        }
    }

    public partial class BoolExpression : Expression
    {
        // public string Value;
        override public void Pretty(PrettyBuilder builder, int outerPrecedence, bool opposite)
        {
            builder.Append(Value.ToString());
        }
    }

}
