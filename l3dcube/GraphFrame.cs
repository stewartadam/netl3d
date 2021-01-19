using System;
using Colourful;
using netl3d.Core;

namespace netl3d.l3dcube
{
    public class GraphFrame : BaseFrame<PlanePosition>
    {
        public int FaceLength { get; private set; }
        private readonly RGBColor[] _leds;

        public GraphFrame(int faceLength = 8) : base((int)Math.Pow(faceLength, 3))
        {
            FaceLength = faceLength;

            var ledCount = (int)Math.Pow(FaceLength, 2);
            _leds = new RGBColor[ledCount];
        }

        public GraphFrame(int faceLength, RGBColor[] leds) : base((int)Math.Pow(faceLength, 3))
        {
            var ledCount = (int)Math.Pow(FaceLength, 2);
            if (leds.Length != ledCount)
            {
                throw new ArgumentException("Number of LEDs received is not the square of face size");
            }

            Array.Copy(leds, _leds, ledCount);
        }

        /// <summary>
        /// Gets the offset on the 1D LED state array given 3D point co-ordinates
        /// </summary>
        protected override int ConvertToArrayPosition(PlanePosition pos)
        {
            return (pos.x * FaceLength) + pos.y;
        }

        public GraphFrame AsCopy() => new GraphFrame(FaceLength, _leds);
    }
}
