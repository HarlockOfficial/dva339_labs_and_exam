using System;
using System.Collections.Generic;
using System.Text;

namespace LectureLanguage
{

    public struct FunctionLiftSupport
    {
        public string NewName;
        public HashSet<string> ExtraArguments;

        public FunctionLiftSupport(string newName, HashSet<string> extraArguments)
        {
            NewName = newName;
            ExtraArguments = extraArguments;
        }
    }

    public class LiftEnvironment
    {
        public Dictionary<string, LiftedFunctionExpression> Functions = new Dictionary<string, LiftedFunctionExpression>();
        Dictionary<string, int> NameGenerator = new Dictionary<string, int>();


        public Dictionary<string, FunctionLiftSupport> LiftMap = new Dictionary<string, FunctionLiftSupport>();

        public string NewName(string name)
        {
            if (!NameGenerator.ContainsKey(name))
            {
                NameGenerator[name] = 0;
            }

            var newName = $"{name}_{NameGenerator[name]}";
            NameGenerator[name] += 1;
            return newName;
        }
    }

    public partial class ExpressionProgram
    {
        List<LiftedFunctionExpression> Functions;
        Expression MainExpression;

        public ExpressionProgram(List<LiftedFunctionExpression> functions, Expression main)
        {
            Functions = functions;
            MainExpression = main;
        }
    }


    public abstract partial class Expression
    {
        // public int Line;
        // public int Column;

        public ExpressionProgram Lift()
        {
            var env = new LiftEnvironment();
            var _this = Lift(env);

            return new ExpressionProgram(new List<LiftedFunctionExpression>(env.Functions.Values), _this);
        }

        public abstract Expression Lift(LiftEnvironment env);
    }

    public partial class LetExpression : Expression
    {
        // public string Name;
        // public Expression Expression;
        // public Expression Recipient;


        public override Expression Lift(LiftEnvironment env)
        {
            Expression = Expression.Lift(env);
            Recipient = Recipient.Lift(env);
            return this;
        }
    }

    public partial class LiftedFunctionExpression
    {
        // public string Name;
        // public List<string> ArgumentName;
        // public List<Type> ArgumentType;
        // public Type ReturnType;
        // public Expression Body;

        public override Expression Lift(LiftEnvironment env)
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

        public override Expression Lift(LiftEnvironment env)
        {
            Body = Body.Lift(env);

            var fv = Body.FreeVariables();
            fv.Remove(Name);
            fv.Remove(ArgumentName);

            var newName = env.NewName(Name);
            var argumentNames = new List<string> { ArgumentName };
            argumentNames.AddRange(fv);

            var lf = new LiftedFunctionExpression(newName, argumentNames, ReturnType, Body);
            env.Functions[newName] = lf;

            env.LiftMap[Name] = new FunctionLiftSupport(newName, fv);
            Recipient = Recipient.Lift(env);
            env.LiftMap.Remove(Name);

            return Recipient;
        }
    }

    public partial class LiftedFunctionCallExpression : Expression
    {
        // public string Name;
        // public List<Expression> Arguments;

        public override Expression Lift(LiftEnvironment env)
        {
            throw new NotImplementedException();
        }
    }

    public partial class ApplicationExpression : Expression
    {
        // public string Name;
        // public Expression Argument;

        public override Expression Lift(LiftEnvironment env)
        {
            var support = env.LiftMap[Name];
            var arguments = new List<Expression>() { Argument };
            foreach (var name in support.ExtraArguments)
            {
                arguments.Add(new VariableExpression(name));
            }
            var lc = new LiftedFunctionCallExpression(support.NewName, arguments);

            return lc;
        }
    }

    public partial class SequenceExpression : Expression
    {
        // public Expression Expression1;
        // public Expression Expression2;

        public override Expression Lift(LiftEnvironment env)
        {
            Expression1 = Expression1.Lift(env);
            Expression2 = Expression2.Lift(env);
            return this;
        }
    }

    public partial class BinaryOperatorExpression : Expression
    {
        // public BinaryOperator Operator;
        // public Expression Expression1;
        // public Expression Expression2;

        public override Expression Lift(LiftEnvironment env)
        {
            Expression1 = Expression1.Lift(env);
            Expression2 = Expression2.Lift(env);
            return this;
        }
    }

    public partial class VariableExpression : Expression
    {
        // public string Name;

        public override Expression Lift(LiftEnvironment env)
        {
            return this;
        }
    }

    public partial class NumberExpression : Expression
    {
        // public int Value;


        public override Expression Lift(LiftEnvironment env)
        {
            return this;
        }
    }

    public partial class BoolExpression : Expression
    {
        // public bool Value;

        public override Expression Lift(LiftEnvironment env)
        {
            return this;
        }
    }

}
