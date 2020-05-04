from __future__ import annotations # https://stackoverflow.com/a/33533514

import spectra
import threading

from typing import List, Tuple

from netl3d import base

CubePositionType = Tuple[int, int, int]
PlanePositionType = Tuple[int, int]

class CubeFrame(base.Frame[CubePositionType]):
  """Represents a frame for the L3D Cube"""
  _state_linear: List[spectra.rgb] = []

  def __init__(self, face_size: int = 8) -> None:
    self.face_size = face_size
    super().__init__()

  def _within_bounds(self, pos: CubePositionType) -> CubePositionType:
    (x, y, z) = pos
    f = lambda i: max(0, min(i, self.face_size-1))
    return (f(x), f(y), f(z))

  def _is_within_bounds(self, pos: CubePositionType) -> bool:
    (x, y, z) = pos
    f = lambda i: max(0, min(i, self.face_size-1))
    return (f(x), f(y), f(z)) == pos

  def _get_point_index(self, pos: CubePositionType) -> int:
    (x, y, z) = self._within_bounds(pos)
    """Gets the offset on the 1D LED state array given 3D point co-ordinates"""
    return z*(self.face_size**2) + x*self.face_size + y

  def get_led_raw(self, pos: CubePositionType) -> spectra.rgb:
    """Returns the LED state at the given 3D point co-ordinates"""
    (x, y, z) = pos
    return self._state_linear[self._get_point_index(pos)]

  def set_led(self, pos: CubePositionType, state: spectra.rgb, verify_bounds: bool=False) -> None:
    """Sets the LED state at the given 3D point co-ordinates"""
    (x, y, z) = pos
    if verify_bounds and not self._is_within_bounds(pos):
      return
    self._state_linear[self._get_point_index(pos)] = state

  def copy(self) -> CubeFrame:
    frame = CubeFrame()
    frame._state_linear = list(self._state_linear)
    return frame

  def fill(self, color: spectra.rgb) -> None:
    self._state_linear = [color]*self.face_size**3


class GraphFrame(base.Frame[PlanePositionType]):
  """Represents a frame for the L3D Cube"""
  _state_linear: List[spectra.rgb] = []

  def __init__(self, face_size: int = 8) -> None:
    self.face_size = face_size
    base.Frame.__init__(self)

  def _get_point_index(self, pos: PlanePositionType) -> int:
    (x, y) = pos
    """Gets the offset on the 1D LED state array given 3D point co-ordinates"""
    return x*self.face_size + y

  def get_led_raw(self, pos: PlanePositionType) -> spectra.rgb:
    """Returns the LED state at the given 3D point co-ordinates"""
    (x, y) = pos
    return self._state_linear[self._get_point_index(pos)]

  def set_led(self, pos: PlanePositionType, state: spectra.rgb) -> None:
    """Sets the LED state at the given 3D point co-ordinates"""
    (x, y) = pos
    self._state_linear[self._get_point_index(pos)] = state

  def copy(self) -> GraphFrame:
    frame = GraphFrame()
    frame._state_linear = list(self._state_linear)
    return frame

  def fill(self, color: spectra.rgb) -> None:
    self._state_linear = [color]*self.face_size**3
