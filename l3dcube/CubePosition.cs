using netl3d.Interfaces;

namespace netl3d.l3dcube
{
    public class CubePosition : PlanePosition, IFramePosition
    {
        public int z { get; set; } = 0;
    }
}
