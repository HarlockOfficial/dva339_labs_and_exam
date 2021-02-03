using System;
using System.Collections.Generic;
using System.Text;

namespace LectureLanguage
{

    public class TypechekingException : Exception
    {
        public TypechekingException()
        {
        }

        public TypechekingException(string msg) : base(msg)
        {
        }
    }

    public class TypechekingStateException : Exception
    {
        public TypechekingStateException()
        {
        }

        public TypechekingStateException(string msg) : base(msg)
        {
        }
    }

    public class TypecheckingState
    {
        Stack<Dictionary<string, Type>> VariableStack = new Stack<Dictionary<string, Type>>();
        Stack<Dictionary<string, LetRecExpression>> FunctionStack = new Stack<Dictionary<string, LetRecExpression>>();

        public TypecheckingState()
        {
            EnterScope();
        }

        public void EnterScope()
        {
            VariableStack.Push(new Dictionary<string, Type>());
            FunctionStack.Push(new Dictionary<string, LetRecExpression>());
        }

        public void ExitScope()
        {
            VariableStack.Pop();
            FunctionStack.Pop();
        }

        public void BindVariable(string name, Type type)
        {
            VariableStack.Peek()[name] = type;
        }

        public Type LookupVariable(string name)
        {

            foreach (var frame in VariableStack)
            {
                if (frame.ContainsKey(name))
                {
                    return frame[name];
                }
            }

            throw new TypechekingStateException($"Variable {name} not declared.");
        }

        public void BindFunction(string name, LetRecExpression value)
        {
            FunctionStack.Peek()[name] = value;
        }

        public LetRecExpression LookupFunction(string name)
        {
            foreach (var frame in FunctionStack)
            {
                if (frame.ContainsKey(name))
                {
                    return frame[name];
                }
            }

            throw new TypechekingStateException($"Function {name} not declared.");
        }

    }


    public abstract partial class Expression
    {
        // public int Line;
        // public int Column;

        public Type Typecheck()
        {
            return Typecheck(new TypecheckingState());
        }

        public abstract Type Typecheck(TypecheckingState state);

        public void TypeError(string msg)
        {
            throw new TypechekingException($"{msg} on line {Line} column {Column}");
        }
    }

    public partial class LetExpression : Expression
    {
        // public string Name;
        // public Expression Expression;
        // public Expression Recipient;

        public override Type Typecheck(TypecheckingState state)
        {
            var variableType = Expression.Typecheck(state);
            state.EnterScope();
            state.BindVariable(Name, variableType);
            var type = Recipient.Typecheck(state);
            state.ExitScope();
            return type;
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

        public override Type Typecheck(TypecheckingState state)
        {
            state.EnterScope();
            state.BindFunction(Name, this);

            // type check the body once
            state.EnterScope();
            state.BindVariable(ArgumentName, ArgumentType);
            var returnType = Body.Typecheck(state);

            if (returnType != ReturnType)
            {
                TypeError("Return type mismatch");
            }
            state.ExitScope();

            var type = Recipient.Typecheck(state);

            state.ExitScope();

            return type;
        }
    }

    public partial class ApplicationExpression : Expression
    {
        // public string Name;
        // public Expression Argument;

        public override Type Typecheck(TypecheckingState state)
        {
            try
            {
                var fun = state.LookupFunction(Name);
                var argumentType = Argument.Typecheck(state);

                if (argumentType != fun.ArgumentType)
                {
                    TypeError($"Argument type mismatch in call to {Name}");
                }

                return fun.ReturnType;
            } catch(TypechekingStateException e)
            {
                TypeError(e.Message);
            }

            throw new ImpossibleException();
        }
    }

    public partial class SequenceExpression : Expression
    {
        // public Expression Expression1;
        // public Expression Expression2;

        public override Type Typecheck(TypecheckingState state)
        {
            Expression1.Typecheck(state);
            return Expression2.Typecheck(state);
        }
    }

    public partial class BinaryOperatorExpression : Expression
    {
        // public BinaryOperator Operator;
        // public Expression Expression1;
        // public Expression Expression2;

        public override Type Typecheck(TypecheckingState state)
        {
            var type1 = Expression1.Typecheck(state);
            var type2 = Expression2.Typecheck(state);


            switch (Operator)
            {
                case BinaryOperator.Add:
                    if (type1 != Type.NumType && type2 != Type.NumType)
                    {
                        TypeError("+ expects number operands");
                    }
                    return Type.NumType;

                case BinaryOperator.Sub:
                    if (type1 != Type.NumType && type2 != Type.NumType)
                    {
                        TypeError("- expects number operands");
                    }
                    return Type.NumType;

                case BinaryOperator.Eq:
                    if (type1 != type2)
                    {
                        TypeError("== expects operands of the same type");
                    }
                    return Type.BoolType;

                case BinaryOperator.Lt:
                    if (type1 != Type.NumType && type2 != Type.NumType)
                    {
                        TypeError("- expects number operands");
                    }
                    return Type.BoolType;
            }

            throw new ImpossibleException();
        }
    }

    public partial class VariableExpression : Expression
    {
        // public string Name;

        public override Type Typecheck(TypecheckingState state)
        {
            try
            {
                var type = state.LookupVariable(Name);
                return type;
            } catch (TypechekingStateException e)
            {
                TypeError(e.Message);
            }

            throw new ImpossibleException();
        }
    }

    public partial class NumberExpression : Expression
    {
        // public string Value;

        public override Type Typecheck(TypecheckingState state)
        {
            return Type.NumType;
        }
    }


    public partial class BoolExpression : Expression
    {
        // public bool Value;

        public override Type Typecheck(TypecheckingState state)
        {
            return Type.BoolType;
        }
    }


}
