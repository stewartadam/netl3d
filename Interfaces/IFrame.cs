using Colourful;

namespace netl3d.Interfaces
{
    public interface IFrame<TPosition> where TPosition : IFramePosition
    {
        RGBColor GetLed(TPosition pos);
        void SetLed(TPosition pos, RGBColor led);
    }
}
