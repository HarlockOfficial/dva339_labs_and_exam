using System;
using System.Collections.Generic;
using System.Text;

namespace LectureLanguage
{
    public class PrettyBuilder
    {
        StringBuilder builder = new StringBuilder();
        int indent = 0;

        public void Indent() {
            indent += 2;
        }
        public void Unindent() {
            indent -= 2;
        }

        public void Append(string text)
        {
            builder.Append(text);
        }

        public void NewLine()
        {
            builder.Append("\n");
            if (indent > 0)
            {
                builder.Append(new string(' ', indent));
            }
        }

        public override string ToString()
        {
            return builder.ToString();
        }

    }
}
