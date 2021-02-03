using System;
using System.Collections.Generic;
using System.Text;

namespace LectureLanguage
{

    public class EvaluationException : Exception
    {
        public EvaluationException()
        {
        }

        public EvaluationException(string msg) : base(msg)
        {
        }
    }

    public class EvaluationStateException : Exception
    {
        public EvaluationStateException()
        {
        }

        public EvaluationStateException(string msg) : base(msg)
        {
        }
    }

    public class EvaluationState {
        
        Stack<Dictionary<string, int>> CallStack = new Stack<Dictionary<string, int>>();
        Stack<Dictionary<string, LetRecExpression>> FunctionStack = new Stack<Dictionary<string, LetRecExpression>>();

        public EvaluationState()
        {
            EnterScope();
        }

        public void EnterScope()
        {
            CallStack.Push(new Dictionary<string, int>());
            FunctionStack.Push(new Dictionary<string, LetRecExpression>());
        }

        public void ExitScope()
        {
            CallStack.Pop();
            FunctionStack.Pop();
        }

        public void BindVariable(string name, int value)
        {
            CallStack.Peek()[name] = value;
        }

        // let x = 1 in let f y = x + y in f 4
        public int LookupVariable(string name)
        {
            foreach (var frame in CallStack)
            {
                if (frame.ContainsKey(name))
                {
                    return frame[name];
                }
            }

            throw new EvaluationStateException($"Variable {name} not found");
        }

        public void BindFunction(string name, LetRecExpression value)
        {
            FunctionStack.Peek()[name] = value;
        }

        // let x = 1 in let f y = x + y in f 4
        public LetRecExpression LookupFunction(string name)
        {
            foreach (var frame in FunctionStack)
            {
                if (frame.ContainsKey(name))
                {
                    return frame[name];
                }
            }

            throw new EvaluationStateException($"Function {name} not found");
        }
    }

    public abstract partial class Expression
    {
        // public int Line;
        // public int Column;

        public int Evaluate()
        {
            return Evaluate(new EvaluationState());
        }
        public abstract int Evaluate(EvaluationState state);

        public void EvaluationError(string message)
        {
            throw new EvaluationException($"{message} on line {Line} colum {Column}");
        }
    }

    public partial class LetExpression : Expression
    {
        // public string Name;
        // public Expression Expression;
        // public Expression Recipient;

        override public int Evaluate(EvaluationState state)
        {
            var value = Expression.Evaluate(state);
            state.BindVariable(Name, value);
            var result = Recipient.Evaluate(state);
            return result;
        }
    }

    public partial class LetRecExpression : Expression
    {
        // public string Name;
        // public string ArgumentName;
        // public Expression Body;
        // public Expression Recipient;
        override public int Evaluate(EvaluationState state)
        {
            state.BindFunction(Name, this);
            var result = Recipient.Evaluate(state);
            return result;
        }
    }

    public partial class ApplicationExpression : Expression
    {
        // public string Name;
        // public Expression Argument;
        override public int Evaluate(EvaluationState state)
        {
            try
            {
                var function = state.LookupFunction(Name);
                var argument = Argument.Evaluate(state);

                state.EnterScope();
                state.BindVariable(function.ArgumentName, argument);
                var result = function.Body.Evaluate(state);
                state.ExitScope();
                return result;
            } catch (EvaluationStateException e)
            {
                EvaluationError(e.Message);
            }

            throw new ImpossibleException();
        }
    }

    public partial class SequenceExpression : Expression
    {
        // public Expression Expression1;
        // public Expression Expression2;
        override public int Evaluate(EvaluationState state)
        {
            Expression1.Evaluate(state);
            var result = Expression2.Evaluate(state);
            return result;
        }
    }

    public partial class BinaryOperatorExpression : Expression
    {
        // public BinaryOperator Operator;
        // public Expression Expression1;
        // public Expression Expression2;
        override public int Evaluate(EvaluationState state)
        {
            var value1 = Expression1.Evaluate(state);
            var value2 = Expression2.Evaluate(state);

            var result = 0;
            switch (Operator)
            {
                case BinaryOperator.Add:
                    result = value1 + value2;
                    break;
                case BinaryOperator.Sub:
                    result = value1 - value2;
                    break;
                case BinaryOperator.Eq:
                    result = value1 == value2 ? 1 : 0;
                    break;
                case BinaryOperator.Lt:
                    result = value1 < value2 ? 1 : 0;
                    break;
            }

            return result;
        }
    }

    public partial class VariableExpression : Expression
    {
        // public string Name;
        override public int Evaluate(EvaluationState state)
        {
            try
            {
                var result = state.LookupVariable(Name);
                return result;
            } catch (EvaluationStateException e)
            {
                EvaluationError(e.Message);
            }

            throw new ImpossibleException();
        }
    }

    public partial class NumberExpression : Expression
    {
        // public string Value;
        override public int Evaluate(EvaluationState state)
        {
            return Convert.ToInt32(Value);
        }
    }

    public partial class BoolExpression : Expression
    {
        // public string Value;
        override public int Evaluate(EvaluationState state)
        {
            return Value ? 1 : 0;
        }
    }
}
