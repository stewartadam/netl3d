using System.Net;
using System.Threading;
using System.Threading.Tasks;
using Colourful;
using Microsoft.Extensions.Hosting;
using Microsoft.Extensions.Logging;
using netl3d.l3dcube;

namespace netl3d
{
    public class Netl3dService : IHostedService
    {
        private readonly ILogger _logger;

        public Netl3dService(ILogger<Netl3dService> logger, ILoggerFactory loggerFactory, IHostApplicationLifetime appLifetime)
        {
            _logger = logger;
            ApplicationLogging.Initialize(loggerFactory);

            appLifetime.ApplicationStarted.Register(OnStarted);
            appLifetime.ApplicationStopping.Register(OnStopping);
            appLifetime.ApplicationStopped.Register(OnStopped);
        }

        public async Task StartAsync(CancellationToken cancellationToken)
        {
            _logger.LogInformation("1. StartAsync has been called.");
            var controller = new L3DController(IPAddress.Parse("10.0.1.230"), 65506);

            var frame = new CubeFrame();
            for (var i = 0; i < 3; i++)
            {
                var r = i % 3 == 0 ? 1 : 0;
                var g = i % 3 == 1 ? 1 : 0;
                var b = i % 3 == 2 ? 1 : 0;

                _logger.LogDebug($"Filling RGB ({r}, {g}, {b})");

                frame.Fill(new RGBColor(r, g, b));
                await controller.SendFrameAsync(frame).ConfigureAwait(false);

                if (cancellationToken.IsCancellationRequested)
                {
                    break;
                }

                Thread.Sleep(1000);
            }
        }

        public Task StopAsync(CancellationToken cancellationToken)
        {
            _logger.LogInformation("2. StopAsync has been called.");
            return Task.CompletedTask;
        }

        private void OnStarted()
        {
            _logger.LogInformation("2. OnStarted has been called.");
        }

        private void OnStopping()
        {
            _logger.LogInformation("3. OnStopping has been called.");
        }

        private void OnStopped()
        {
            _logger.LogInformation("5. OnStopped has been called.");
        }
    }
}
