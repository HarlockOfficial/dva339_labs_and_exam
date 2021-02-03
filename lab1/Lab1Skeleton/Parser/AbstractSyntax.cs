using System;
using System.Text;
using System.Collections.Generic;

namespace Parser
{
	// statements

	public abstract class Statement
	{
		public abstract void Pretty(StringBuilder builder);
	
		public override string ToString()
		{
			var builder = new StringBuilder();
			Pretty(builder);
			return builder.ToString();
		}
	}

	public class SequenceStatement : Statement
	{
		public Statement head;
		public Statement tail;

		public SequenceStatement(Statement head, Statement tail)
		{
			this.head = head;
			this.tail = tail;
		}

		override public void Pretty(StringBuilder builder)
		{
			head.Pretty(builder);
			builder.Append("; ");
			tail.Pretty(builder);
		}
	}

	public class PrintStatement : Statement
	{
		public LinkedList<Expression> exprList;

		public PrintStatement(LinkedList<Expression> exprList)
		{
			this.exprList = exprList;
		}

		override public void Pretty(StringBuilder builder)
		{	
			builder.Append("print (");
			bool first = true;
			foreach (var expr in exprList)
			{
				if (!first) builder.Append(", ");
				expr.Pretty(builder);
				first = false;
			}
			builder.Append(")");
		}

	}

	public class AssignmentStatement : Statement
	{
		public string id;
		public Expression expr;

		public AssignmentStatement(string id, Expression expr)
		{
			this.id = id;
			this.expr = expr;
		}

		override public void Pretty(StringBuilder builder)
		{
			builder.Append(id + " := ");
			expr.Pretty(builder);
		}
	}

	// expressions

	public abstract class Expression 
	{
		public abstract void Pretty(StringBuilder builder);

		public override string ToString()
		{
			var builder = new StringBuilder();
			Pretty(builder);
			return builder.ToString();
		}
	}

	public class IdentifierExpression : Expression
	{
		public string id;

		public IdentifierExpression(string id)
		{
			this.id = id;
		}

		override public void Pretty(StringBuilder builder)
		{
			builder.Append(id);
		}

	}

	public class NumberExpression : Expression
	{
		public int num;

		public NumberExpression(string num)
		{
			this.num = Convert.ToInt32(num);
		}

		override public void Pretty(StringBuilder builder)
		{
			builder.Append(num);
		}

	}

	public class BinaryOperatorExpression : Expression
	{
		public Type type;
		public Expression left;
		public Expression right;

		public enum Type { ADD }

		public BinaryOperatorExpression(Type type, Expression left, Expression right)
		{
			this.type = type;
			this.left = left;
			this.right = right;
		}

		override public void Pretty(StringBuilder builder)
		{
			left.Pretty(builder);
			builder.Append(" + ");
			right.Pretty(builder);
		}

	}

	public class LetExpression : Expression
	{
		public Statement stmt;
		public Expression expr;

		public LetExpression(Statement stmt, Expression expr)
		{
			this.stmt = stmt;
			this.expr = expr;
		}

		override public void Pretty(StringBuilder builder)
		{
			builder.Append("(");
			stmt.Pretty(builder);
			builder.Append(",");
			expr.Pretty(builder);
			builder.Append(")");
		}

	}


}
