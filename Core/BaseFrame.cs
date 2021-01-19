using System;
using System.Collections.Generic;
using System.Threading;
using System.Threading.Tasks;
using Colourful;
using netl3d.Interfaces;

namespace netl3d.Core
{
    /// <summary>
    /// Pipeline where frames are pulled from the pipeline synchronously using
    /// get_frame(). The base generator has its frame buffered.
    /// </summary>
    public abstract class BaseFrame<TPosition> : IFrame<TPosition> where TPosition : IFramePosition
    {
        protected RGBColor[] _leds; // fixme should be readonly

        public BaseFrame(int ledCount)
        {
            _leds = new RGBColor[ledCount];
        }

        protected abstract int ConvertToArrayPosition(TPosition pos);

        public RGBColor GetLed(TPosition pos) => _leds[ConvertToArrayPosition(pos)];

        // fixme this is by reference, it should be readonly
        public RGBColor[] GetAllLeds() => _leds;

        // fixme optimize
        public void SetLed(TPosition pos, RGBColor led) => _leds[ConvertToArrayPosition(pos)] = led;

        public void SetAllLeds(RGBColor[] leds)
        {
            if (leds.Length != _leds.Length)
            {
                throw new ArgumentException("Supplied LEDs array does not match length of LEDs in frame");
            }

            // fixme optimize and by-reference when it should copy
            Array.Copy(leds, _leds, _leds.Length);
        }

        public void Fill(RGBColor color)
        {
            for (int i = 0; i < _leds.Length; i++)
            {
                _leds[i] = color;
            }
        }

        public void Clear() => Fill(new RGBColor(0, 0, 0));
    }
}
