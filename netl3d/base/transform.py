import abc

from netl3d.hardware.l3dcube import CubeFrame


class FrameTransform(abc.ABC):
  @abc.abstractmethod
  def apply(self, input: CubeFrame) -> CubeFrame:
    raise NotImplementedError