using System;
using Colourful;
using netl3d.Core;

namespace netl3d.l3dcube
{
    public class CubeFrame : BaseFrame<CubePosition>
    {
        public int FaceLength { get; private set; }

        public CubeFrame(int faceLength = 8) : base((int)Math.Pow(faceLength, 3))
        {
            FaceLength = faceLength;
        }

        public CubeFrame(int faceLength, RGBColor[] leds) : base((int)Math.Pow(faceLength, 3))
        {
            if (leds.Length != _leds.Length)
            {
                throw new ArgumentException("Number of LEDs received is not the cube of face size");
            }

            Array.Copy(leds, _leds, _leds.Length);
        }

        /// <summary>
        /// Gets the offset on the 1D LED state array given 3D point co-ordinates
        /// </summary>
        protected override int ConvertToArrayPosition(CubePosition pos)
        {
            return (pos.z * (int)Math.Pow(FaceLength, 2)) + (pos.x * FaceLength) + pos.y;
        }

        public CubeFrame AsCopy() => new CubeFrame(FaceLength, _leds);
    }
}
