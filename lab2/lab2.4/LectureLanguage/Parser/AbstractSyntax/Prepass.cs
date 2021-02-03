using System;
using System.Collections.Generic;
using System.Text;

namespace LectureLanguage
{

    // let x = 1 in (let x = 1 in 3, let x = 1 in 4, x)
   
    public class PrepassState
    {
        public Stack<Dictionary<string, string>> NameStack = new Stack<Dictionary<string, string>>();
        public Stack<Dictionary<string, int>> CountStack = new Stack<Dictionary<string, int>>();

        public void EnterScope()
        {
            NameStack.Push(new Dictionary<string, string>());
            CountStack.Push(new Dictionary<string, int>());
        }

        public void ExitScope()
        {
            NameStack.Pop();
            CountStack.Pop();
        }

        public void Bind(string name)
        {
            var count = 0;
            foreach (var countMap in CountStack)
            {
                if (countMap.ContainsKey(name))
                {
                    count = countMap[name];
                    break;
                }
            }

            CountStack.Peek()[name] = count + 1;
            NameStack.Peek()[name] = count == 0 ? name : $"{name}_{count}";
        }

        public string Rename(string name)
        {
            var result = name;
            foreach (var nameMap in NameStack)
            {
                if (nameMap.ContainsKey(name))
                {
                    result = nameMap[name];
                    break;
                }
            }
            return result;
        }

    }
    public abstract partial class Expression
    {
        // public int Line;
        // public int Column;

        public void Prepass()
        {
            Prepass(new PrepassState());
        }

        public abstract void Prepass(PrepassState state);

    }

    // let x = E in E
    public partial class LetExpression : Expression
    {
        // public string Name;
        // public Expression Expression;
        // public Expression Recipient;

        public string DisplayName;

        override public void Prepass(PrepassState state)
        {
            DisplayName = Name;

            Expression.Prepass(state);
            state.EnterScope();

            state.Bind(Name);
            Name = state.Rename(Name);

            Recipient.Prepass(state);
            state.ExitScope();

        }
    }

    // let f x = x in let f = 4 in f f
    public partial class LetRecExpression : Expression
    {
        // public string Name;
        // public string ArgumentName;
        // public Expression Body;
        // public Expression Recipient;

        public string DisplayName;
        public String DisplayArgumentName;

        override public void Prepass(PrepassState state)
        {
            DisplayName = Name;
            DisplayArgumentName = ArgumentName;

            state.EnterScope();

            state.Bind(Name);
            Name = state.Rename(Name);

            state.EnterScope();
            state.Bind(ArgumentName);
            ArgumentName = state.Rename(ArgumentName);

            Body.Prepass(state);

            state.ExitScope();

            Recipient.Prepass(state);

            state.ExitScope();
        }
    }

    public partial class ApplicationExpression : Expression
    {
        // public string Name;
        // public Expression Argument;

        public string DisplayName;
        override public void Prepass(PrepassState state)
        {
            DisplayName = Name;
            Name = state.Rename(Name);
            Argument.Prepass(state);
        }
    }

    public partial class SequenceExpression : Expression
    {
        // public Expression Expression1;
        // public Expression Expression2;
        override public void Prepass(PrepassState state)
        {
            Expression1.Prepass(state);
            Expression2.Prepass(state);
        }

    }

    public partial class BinaryOperatorExpression : Expression
    {
        // public BinaryOperator Operator;
        // public Expression Expression1;
        // public Expression Expression2;
        override public void Prepass(PrepassState state)
        {
            Expression1.Prepass(state);
            Expression2.Prepass(state);
        }
    }

    public partial class VariableExpression : Expression
    {
        // public string Name;

        public string DisplayName;
        override public void Prepass(PrepassState state)
        {
            DisplayName = Name;
            Name = state.Rename(Name);
        }

    }

    public partial class NumberExpression : Expression
    {
        // public string Value;
        override public void Prepass(PrepassState state)
        {
        }
    }

    public partial class BoolExpression : Expression
    {
        // public string Value;
        override public void Prepass(PrepassState state)
        {
        }
    }

}
