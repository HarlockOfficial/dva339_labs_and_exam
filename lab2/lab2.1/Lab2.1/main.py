import sys
from MyLexer import MyLexer, find_column
from MyParser import MyParser


def main():
    '''if len(sys.argv) == 1:
        print(f"Usage; {sys.argv[0]} [-t | <file_name>]")
        return
    string = None
    if sys.argv[1] == "-t":
        string = sys.stdin.read()
    else:
        with open(sys.argv[1], "r") as f:
            string = f.read()
    if string is None:
        print("Unknown Error, try again")
        return'''
    #string = sys.stdin.read()
    string ="""
    int main(){
        int x;
        x = 5;
        print(0, x, false);
        return 0;
    }
    """
    lexer = MyLexer()
    token_list = []
    for token in lexer.tokenize(string):
        token.index = find_column(string, token)
        token_list.append(token)
    parser = MyParser(token_list)
    out = parser.parse(iter(token_list))
    if out is None:
        print(False)
    else:
        print(out[1])


if __name__ == "__main__":
    main()

