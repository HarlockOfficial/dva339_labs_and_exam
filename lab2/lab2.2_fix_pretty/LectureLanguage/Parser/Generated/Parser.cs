// This code was generated by the Gardens Point Parser Generator
// Copyright (c) Wayne Kelly, John Gough, QUT 2005-2014
// (see accompanying GPPGcopyright.rtf)

// GPPG version 1.5.2
// Machine:  DESKTOP-64EK7A4
// DateTime: 11/26/2020 2:19:49 PM
// UserName: dhn03
// Input file <.\Parser.y - 11/26/2020 2:18:01 PM>

// options: lines gplex

using System;
using System.Collections.Generic;
using System.CodeDom.Compiler;
using System.Globalization;
using System.Text;
using QUT.Gppg;

namespace Parser
{
public enum Tokens {error=2,EOF=3,ID=4,NUM=5,LEXERR=6,
    LET=7,IN=8,ASN=9,ADD=10,SUB=11,MUL=12,
    DIV=13,COMMA=14,LPAR=15,RPAR=16};

public struct ValueType
#line 4 ".\Parser.y"
       {
	public string Value;
	public Expression Expression;
}
#line default
// Abstract base class for GPLEX scanners
[GeneratedCodeAttribute( "Gardens Point Parser Generator", "1.5.2")]
public abstract class ScanBase : AbstractScanner<ValueType,LexLocation> {
  private LexLocation __yylloc = new LexLocation();
  public override LexLocation yylloc { get { return __yylloc; } set { __yylloc = value; } }
  protected virtual bool yywrap() { return true; }
}

// Utility class for encapsulating token information
[GeneratedCodeAttribute( "Gardens Point Parser Generator", "1.5.2")]
public class ScanObj {
  public int token;
  public ValueType yylval;
  public LexLocation yylloc;
  public ScanObj( int t, ValueType val, LexLocation loc ) {
    this.token = t; this.yylval = val; this.yylloc = loc;
  }
}

[GeneratedCodeAttribute( "Gardens Point Parser Generator", "1.5.2")]
public class Parser: ShiftReduceParser<ValueType, LexLocation>
{
#pragma warning disable 649
  private static Dictionary<int, string> aliases;
#pragma warning restore 649
  private static Rule[] rules = new Rule[19];
  private static State[] states = new State[38];
  private static string[] nonTerms = new string[] {
      "E", "E1", "E2", "E3", "E4", "E5", "P", "$accept", };

  static Parser() {
    states[0] = new State(new int[]{7,7,4,18,15,20,5,28},new int[]{-7,1,-1,3,-2,23,-3,13,-4,24,-5,29,-6,27});
    states[1] = new State(new int[]{3,2});
    states[2] = new State(-1);
    states[3] = new State(new int[]{3,4,14,5});
    states[4] = new State(-2);
    states[5] = new State(new int[]{7,7,4,18,15,20,5,28},new int[]{-2,6,-3,13,-4,24,-5,29,-6,27});
    states[6] = new State(-3);
    states[7] = new State(new int[]{4,8});
    states[8] = new State(new int[]{9,9,4,33});
    states[9] = new State(new int[]{7,7,4,18,15,20,5,28},new int[]{-1,10,-2,23,-3,13,-4,24,-5,29,-6,27});
    states[10] = new State(new int[]{8,11,14,5});
    states[11] = new State(new int[]{7,7,4,18,15,20,5,28},new int[]{-2,12,-3,13,-4,24,-5,29,-6,27});
    states[12] = new State(-5);
    states[13] = new State(new int[]{10,14,11,31,3,-7,14,-7,8,-7,16,-7});
    states[14] = new State(new int[]{4,18,15,20,5,28},new int[]{-4,15,-5,29,-6,27});
    states[15] = new State(new int[]{12,16,13,25,10,-8,11,-8,3,-8,14,-8,8,-8,16,-8});
    states[16] = new State(new int[]{4,18,15,20,5,28},new int[]{-5,17,-6,27});
    states[17] = new State(-11);
    states[18] = new State(new int[]{15,20,4,30,5,28,12,-17,13,-17,10,-17,11,-17,3,-17,14,-17,8,-17,16,-17},new int[]{-6,19});
    states[19] = new State(-14);
    states[20] = new State(new int[]{7,7,4,18,15,20,5,28},new int[]{-1,21,-2,23,-3,13,-4,24,-5,29,-6,27});
    states[21] = new State(new int[]{16,22,14,5});
    states[22] = new State(-16);
    states[23] = new State(-4);
    states[24] = new State(new int[]{12,16,13,25,10,-10,11,-10,3,-10,14,-10,8,-10,16,-10});
    states[25] = new State(new int[]{4,18,15,20,5,28},new int[]{-5,26,-6,27});
    states[26] = new State(-12);
    states[27] = new State(-15);
    states[28] = new State(-18);
    states[29] = new State(-13);
    states[30] = new State(-17);
    states[31] = new State(new int[]{4,18,15,20,5,28},new int[]{-4,32,-5,29,-6,27});
    states[32] = new State(new int[]{12,16,13,25,10,-9,11,-9,3,-9,14,-9,8,-9,16,-9});
    states[33] = new State(new int[]{9,34});
    states[34] = new State(new int[]{7,7,4,18,15,20,5,28},new int[]{-1,35,-2,23,-3,13,-4,24,-5,29,-6,27});
    states[35] = new State(new int[]{8,36,14,5});
    states[36] = new State(new int[]{7,7,4,18,15,20,5,28},new int[]{-2,37,-3,13,-4,24,-5,29,-6,27});
    states[37] = new State(-6);

    for (int sNo = 0; sNo < states.Length; sNo++) states[sNo].number = sNo;

    rules[1] = new Rule(-8, new int[]{-7,3});
    rules[2] = new Rule(-7, new int[]{-1,3});
    rules[3] = new Rule(-1, new int[]{-1,14,-2});
    rules[4] = new Rule(-1, new int[]{-2});
    rules[5] = new Rule(-2, new int[]{7,4,9,-1,8,-2});
    rules[6] = new Rule(-2, new int[]{7,4,4,9,-1,8,-2});
    rules[7] = new Rule(-2, new int[]{-3});
    rules[8] = new Rule(-3, new int[]{-3,10,-4});
    rules[9] = new Rule(-3, new int[]{-3,11,-4});
    rules[10] = new Rule(-3, new int[]{-4});
    rules[11] = new Rule(-4, new int[]{-4,12,-5});
    rules[12] = new Rule(-4, new int[]{-4,13,-5});
    rules[13] = new Rule(-4, new int[]{-5});
    rules[14] = new Rule(-5, new int[]{4,-6});
    rules[15] = new Rule(-5, new int[]{-6});
    rules[16] = new Rule(-6, new int[]{15,-1,16});
    rules[17] = new Rule(-6, new int[]{4});
    rules[18] = new Rule(-6, new int[]{5});

    aliases = new Dictionary<int, string>();
    aliases.Add(7, "let");
    aliases.Add(8, "in");
    aliases.Add(9, "=");
    aliases.Add(10, "+");
    aliases.Add(11, "-");
    aliases.Add(12, "*");
    aliases.Add(13, "/");
    aliases.Add(14, ",");
    aliases.Add(15, "(");
    aliases.Add(16, ")");
  }

  protected override void Initialize() {
    this.InitSpecialTokens((int)Tokens.error, (int)Tokens.EOF);
    this.InitStates(states);
    this.InitRules(rules);
    this.InitNonTerminals(nonTerms);
  }

  protected override void DoAction(int action)
  {
#pragma warning disable 162, 1522
    switch (action)
    {
      case 2: // P -> E, EOF
#line 31 ".\Parser.y"
               { Program = ValueStack[ValueStack.Depth-2].Expression; }
#line default
        break;
      case 3: // E -> E, ",", E1
#line 34 ".\Parser.y"
                    { CurrentSemanticValue.Expression = new SequenceExpression(ValueStack[ValueStack.Depth-3].Expression, ValueStack[ValueStack.Depth-1].Expression); CurrentSemanticValue.Expression.SetLocation(CurrentLocationSpan); }
#line default
        break;
      case 4: // E -> E1
#line 35 ".\Parser.y"
             { CurrentSemanticValue.Expression = ValueStack[ValueStack.Depth-1].Expression; }
#line default
        break;
      case 5: // E1 -> "let", ID, "=", E, "in", E1
#line 38 ".\Parser.y"
                             { CurrentSemanticValue.Expression = new LetExpression(ValueStack[ValueStack.Depth-5].Value, ValueStack[ValueStack.Depth-3].Expression, ValueStack[ValueStack.Depth-1].Expression); CurrentSemanticValue.Expression.SetLocation(CurrentLocationSpan); }
#line default
        break;
      case 6: // E1 -> "let", ID, ID, "=", E, "in", E1
#line 39 ".\Parser.y"
                                { CurrentSemanticValue.Expression = new LetRecExpression(ValueStack[ValueStack.Depth-6].Value, ValueStack[ValueStack.Depth-5].Value, ValueStack[ValueStack.Depth-3].Expression, ValueStack[ValueStack.Depth-1].Expression); CurrentSemanticValue.Expression.SetLocation(CurrentLocationSpan); }
#line default
        break;
      case 7: // E1 -> E2
#line 40 ".\Parser.y"
             { CurrentSemanticValue.Expression = ValueStack[ValueStack.Depth-1].Expression; }
#line default
        break;
      case 8: // E2 -> E2, "+", E3
#line 43 ".\Parser.y"
                  { CurrentSemanticValue.Expression = new BinaryOperatorExpression(BinaryOperator.Add, ValueStack[ValueStack.Depth-3].Expression, ValueStack[ValueStack.Depth-1].Expression); CurrentSemanticValue.Expression.SetLocation(CurrentLocationSpan); }
#line default
        break;
      case 9: // E2 -> E2, "-", E3
#line 44 ".\Parser.y"
                  { CurrentSemanticValue.Expression = new BinaryOperatorExpression(BinaryOperator.Sub, ValueStack[ValueStack.Depth-3].Expression, ValueStack[ValueStack.Depth-1].Expression); CurrentSemanticValue.Expression.SetLocation(CurrentLocationSpan); }
#line default
        break;
      case 10: // E2 -> E3
#line 45 ".\Parser.y"
             { CurrentSemanticValue.Expression = ValueStack[ValueStack.Depth-1].Expression; }
#line default
        break;
      case 11: // E3 -> E3, "*", E4
#line 48 ".\Parser.y"
                  { CurrentSemanticValue.Expression = new BinaryOperatorExpression(BinaryOperator.Mul, ValueStack[ValueStack.Depth-3].Expression, ValueStack[ValueStack.Depth-1].Expression); CurrentSemanticValue.Expression.SetLocation(CurrentLocationSpan); }
#line default
        break;
      case 12: // E3 -> E3, "/", E4
#line 49 ".\Parser.y"
                  { CurrentSemanticValue.Expression = new BinaryOperatorExpression(BinaryOperator.Div, ValueStack[ValueStack.Depth-3].Expression, ValueStack[ValueStack.Depth-1].Expression); CurrentSemanticValue.Expression.SetLocation(CurrentLocationSpan); }
#line default
        break;
      case 13: // E3 -> E4
#line 50 ".\Parser.y"
             { CurrentSemanticValue.Expression = ValueStack[ValueStack.Depth-1].Expression; }
#line default
        break;
      case 14: // E4 -> ID, E5
#line 53 ".\Parser.y"
                  { CurrentSemanticValue.Expression = new ApplicationExpression(ValueStack[ValueStack.Depth-2].Value, ValueStack[ValueStack.Depth-1].Expression); CurrentSemanticValue.Expression.SetLocation(CurrentLocationSpan); }
#line default
        break;
      case 15: // E4 -> E5
#line 54 ".\Parser.y"
             { CurrentSemanticValue.Expression = ValueStack[ValueStack.Depth-1].Expression; }
#line default
        break;
      case 16: // E5 -> "(", E, ")"
#line 57 ".\Parser.y"
                  { CurrentSemanticValue.Expression = ValueStack[ValueStack.Depth-2].Expression; }
#line default
        break;
      case 17: // E5 -> ID
#line 58 ".\Parser.y"
             { CurrentSemanticValue.Expression = new VariableExpression(ValueStack[ValueStack.Depth-1].Value); CurrentSemanticValue.Expression.SetLocation(CurrentLocationSpan); }
#line default
        break;
      case 18: // E5 -> NUM
#line 59 ".\Parser.y"
              { CurrentSemanticValue.Expression = new NumberExpression(ValueStack[ValueStack.Depth-1].Value); CurrentSemanticValue.Expression.SetLocation(CurrentLocationSpan); }
#line default
        break;
    }
#pragma warning restore 162, 1522
  }

  protected override string TerminalToString(int terminal)
  {
    if (aliases != null && aliases.ContainsKey(terminal))
        return aliases[terminal];
    else if (((Tokens)terminal).ToString() != terminal.ToString(CultureInfo.InvariantCulture))
        return ((Tokens)terminal).ToString();
    else
        return CharToString((char)terminal);
  }

#line 63 ".\Parser.y"

public Expression Program;

public Parser(Scanner s) : base(s) { }
#line default
}
}
