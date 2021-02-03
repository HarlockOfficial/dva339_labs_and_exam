using System;
using System.Collections.Generic;
using System.Text;

namespace LectureLanguage
{


    public abstract partial class Expression
    {
        // public int Line;
        // public int Column;

        public HashSet<string> FreeVariables()
        {
            var bound = new HashSet<string>();
            var free = new HashSet<string>();
            FreeVariables(bound, free);
            return free;
        }

        public abstract void FreeVariables(HashSet<string> boundVariables, HashSet<string> freeVariables);
    }

    public partial class LetExpression : Expression
    {
        // public string Name;
        // public Expression Expression;
        // public Expression Recipient;

        public override void FreeVariables(HashSet<string> boundVariables, HashSet<string> freeVariables)
        {
            boundVariables.Add(Name);
            Expression.FreeVariables(boundVariables, freeVariables);
            Recipient.FreeVariables(boundVariables, freeVariables);
            boundVariables.Remove(Name);
        }
    }

    public partial class LiftedFunctionExpression
    {
        // public string Name;
        // public List<string> ArgumentName;
        // public Expression Body;

        public override void FreeVariables(HashSet<string> boundVariables, HashSet<string> freeVariables)
        {
            throw new NotImplementedException();
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

        public override void FreeVariables(HashSet<string> boundVariables, HashSet<string> freeVariables)
        {
            boundVariables.Add(Name);
            boundVariables.Add(ArgumentName);
            Body.FreeVariables(boundVariables, freeVariables);
            boundVariables.Remove(ArgumentName);
            Recipient.FreeVariables(boundVariables, freeVariables);
            boundVariables.Remove(Name);
        }
    }

    public partial class LiftedFunctionCallExpression : Expression
    {
        // public string Name;
        // public List<Expression> Arguments;

        public override void FreeVariables(HashSet<string> boundVariables, HashSet<string> freeVariables)
        {
            Arguments.ForEach(argument => argument.FreeVariables(boundVariables, freeVariables));
        }
    }

    public partial class ApplicationExpression : Expression
    {
        // public string Name;
        // public Expression Argument;

        public override void FreeVariables(HashSet<string> boundVariables, HashSet<string> freeVariables)
        {
            Argument.FreeVariables(boundVariables, freeVariables);
        }
    }

    public partial class SequenceExpression : Expression
    {
        // public Expression Expression1;
        // public Expression Expression2;

        public override void FreeVariables(HashSet<string> boundVariables, HashSet<string> freeVariables)
        {
            Expression1.FreeVariables(boundVariables, freeVariables);
            Expression2.FreeVariables(boundVariables, freeVariables);
        }
    }

    public partial class BinaryOperatorExpression : Expression
    {
        // public BinaryOperator Operator;
        // public Expression Expression1;
        // public Expression Expression2;

        public override void FreeVariables(HashSet<string> boundVariables, HashSet<string> freeVariables)
        {
            Expression1.FreeVariables(boundVariables, freeVariables);
            Expression2.FreeVariables(boundVariables, freeVariables);
        }
    }

    public partial class VariableExpression : Expression
    {
        // public string Name;

        public override void FreeVariables(HashSet<string> boundVariables, HashSet<string> freeVariables)
        {
            if (!boundVariables.Contains(Name))
            {
                freeVariables.Add(Name);
            }
        }
    }

    public partial class NumberExpression : Expression
    {
        // public int Value;

        public override void FreeVariables(HashSet<string> boundVariables, HashSet<string> freeVariables)
        {
        }
    }

    public partial class BoolExpression : Expression
    {
        // public bool Value;

        public override void FreeVariables(HashSet<string> boundVariables, HashSet<string> freeVariables)
        {
        }
    }

}
