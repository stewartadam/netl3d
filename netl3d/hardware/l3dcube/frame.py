# -*- coding: utf-8 -*-
import spectra

from netl3d.hardware.frame import Frame as GenericFrame

class CubeFrame(GenericFrame):
  """Represents a frame for the L3D Cube"""
  _state_linear = []

  def __init__(self, face_size=8):
    self.face_size = face_size
    GenericFrame.__init__(self)

  def _within_bounds(self, pos):
    (x, y, z) = pos
    f = lambda i: max(0, min(i, self.face_size-1))
    return (f(x), f(y), f(z))

  def _is_within_bounds(self, pos):
    (x, y, z) = pos
    f = lambda i: max(0, min(i, self.face_size-1))
    return (f(x), f(y), f(z)) == pos

  def _get_point_index(self, pos):
    (x, y, z) = self._within_bounds(pos)
    """Gets the offset on the 1D LED state array given 3D point co-ordinates"""
    return z*(self.face_size**2) + x*self.face_size + y

  def get_led_raw(self, pos):
    """Returns the LED state at the given 3D point co-ordinates"""
    (x, y, z) = pos
    return self._state_linear[self._get_point_index(pos)]

  def set_led(self, pos, state, verify_bounds=False):
    """Sets the LED state at the given 3D point co-ordinates"""
    (x, y, z) = pos
    if verify_bounds and not self._is_within_bounds(pos):
      return
    self._state_linear[self._get_point_index(pos)] = state

  def fill(self, color):
    self._state_linear = [color]*self.face_size**3


class GraphFrame(GenericFrame):
  """Represents a frame for the L3D Cube"""
  _state_linear = []

  def __init__(self, face_size=8):
    self.face_size = face_size
    GenericFrame.__init__(self)

  def _get_point_index(self, pos):
    (x, y) = pos
    """Gets the offset on the 1D LED state array given 3D point co-ordinates"""
    return x*self.face_size + y

  def get_led_raw(self, pos):
    """Returns the LED state at the given 3D point co-ordinates"""
    (x, y) = pos
    return self._state_linear[self._get_point_index(pos)]

  def set_led(self, pos, state):
    """Sets the LED state at the given 3D point co-ordinates"""
    (x, y) = pos
    self._state_linear[self._get_point_index(pos)] = state

  def fill(self, color):
    self._state_linear = [color]*self.face_size**3
