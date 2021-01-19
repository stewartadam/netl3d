using System;
using System.Collections.Generic;
using System.Net;
using System.Net.Sockets;
using System.Threading;
using System.Threading.Tasks;
using Microsoft.Extensions.Logging;
using netl3d.Interfaces;

namespace netl3d.l3dcube
{
    public class L3DController : IController
    {
        private const int LED_PER_PACKET = 256;
        private const int MAX_SEQUENCE_NUM = 256;
        private readonly UdpClient NetClient = new UdpClient();
        private readonly IPEndPoint DeviceEndpoint;
        private byte _sequenceNumber;
        private bool _initialized = false;

        private readonly ILogger<L3DController> _logger;


        public L3DController(IPAddress deviceIP, int port)
        {
            DeviceEndpoint = new IPEndPoint(deviceIP, port);
            _sequenceNumber = 0;

            _logger = ApplicationLogging.GetFactory().CreateLogger<L3DController>();
        }

        private async Task HandshakeAsync()
        {
            _logger.LogDebug("\t[{deviceIP}] Issuing handshake", DeviceEndpoint.Address);

            var data = new byte[] { (byte) _sequenceNumber };
            await SendPacketAsync((byte) PacketType.HANDSHAKE, data).ConfigureAwait(false);
        }

        private async Task SendColorsAsync(int startLED, byte[] pixelData)
        {
            _logger.LogDebug("\t[{deviceIP}] Sending color data", DeviceEndpoint.Address);

            var data = new byte[pixelData.Length + 2];
            data[0] = (byte) (startLED >> 8);
            data[1] = (byte) (startLED % 256);
            pixelData.CopyTo(data, 2);
            await SendPacketAsync((byte) PacketType.LED_STATE, data).ConfigureAwait(false);
        }

        private async Task SendRefreshAsync()
        {
            _logger.LogDebug("\t[{deviceIP}] Sending refresh", DeviceEndpoint.Address);
            await SendPacketAsync((byte) PacketType.REFRESH).ConfigureAwait(false);
        }

        private async Task SendPacketAsync(int controlValue, byte[]? data = null)
        {
            var size = 2 + (data is null ? 0 : data.Length); // 2 = control value and sequence number
            var payload = new byte[size];

            payload[0] = (byte)controlValue;
            payload[1] = (byte)_sequenceNumber;
            data?.CopyTo(payload, 2);

            _logger.LogDebug("\t\t[{deviceIP}] Sending packet {data}", DeviceEndpoint.Address, BitConverter.ToString(payload).Replace("-",""));

            await NetClient.SendAsync(payload, size, DeviceEndpoint).ConfigureAwait(false);
            _sequenceNumber = (byte) ((_sequenceNumber + 1) % MAX_SEQUENCE_NUM);
        }

        public async Task SendFrameAsync(CubeFrame frame)
        {
            _logger.LogDebug("[{deviceIP}] Sending frame", DeviceEndpoint.Address);

            if (!_initialized)
            {
                await HandshakeAsync();
                _initialized = true;
            }

            var currentLed = 0;
            var ledCount = frame.GetAllLeds().Length;
            var colorData = new byte[Math.Min(LED_PER_PACKET, ledCount) * 3]; // 3=r,g,b byte per LED

            // z is reversed - see note at top about L3D cube hardware indexing
            for (int z = frame.FaceLength - 1; z >= 0; z--)
            {
                for (int y = 0; y < frame.FaceLength; y++)
                {
                    for (int x = 0; x < frame.FaceLength; x++)
            {
                        var led = frame.GetLed(new CubePosition() { x = x, y = y, z = z });
                        var offset = currentLed % LED_PER_PACKET * 3;
                        colorData[offset+0] = (byte) (led.R*255);
                        colorData[offset+1] = (byte) (led.G*255);
                        colorData[offset+2] = (byte) (led.B*255);
                        currentLed++;
                    }

                    // post-increment; 0 through N-1 (for total of N) packets exist in colorData
                    if (currentLed % LED_PER_PACKET == 0)
                    {
                        var sentPacketCount = Math.Max(0, (currentLed / LED_PER_PACKET) - 1); // -1 because ledCount is 1 ahead of the last LED in the packet
                        var offset = sentPacketCount * 256;

                        await SendColorsAsync(offset, colorData).ConfigureAwait(false);
                        colorData = new byte[Math.Min(LED_PER_PACKET, ledCount - currentLed) * 3];
                    }
                }
            }
            await SendRefreshAsync().ConfigureAwait(false);
        }
    }
}
