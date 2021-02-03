using System;
namespace LectureLanguage
{
    public class ImpossibleException : Exception
    {
        public ImpossibleException()
        {
        }

        public ImpossibleException(string msg) : base(msg)
        {
        }
    }

}
