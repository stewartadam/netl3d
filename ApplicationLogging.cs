using System;
using Microsoft.Extensions.Logging;

namespace netl3d
{
    public class ApplicationLogging
    {
        private static ILoggerFactory? _factory;

        public static void Initialize(ILoggerFactory factory)
        {
            _factory = factory;
        }

        public static ILoggerFactory GetFactory()
        {
            if (_factory is null)
            {
                throw new NullReferenceException();
            }
            return _factory;
        }
    }
}
