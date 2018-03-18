# -*- coding: utf-8 -*-
"""
Maintains an in-memory LED state that can be synchronized to a device. L3D
indexes at the start far back, bottom right corner and count upward, wrapping to
the right, then forward.
"""
class led_state:
  led_state = []

  def __init__(self, controller):
    self.controller = controller
    self.clear()

  def __getitem__(self, index):
    return self.led_state[index]

  def __setitem__(self, index, value):
    self.led_state[index] = value

  def get_point_index(self, x, y, z):
    """Gets the LED state offset for the given point"""
    raise NotImplementedError

  def get_point(self, x, y, z):
    """Gets the LED state at the given point"""
    raise NotImplementedError

  def set_point(self, x, y, z, state):
    """Sets the LED state at the given point"""
    self.led_state[self.get_point_index(x, y, z)] = state

  def clear(self):
    self.fill([0, 0, 0])

  def sync(self):
    """Synchronizes in-memory LED state with device"""
    raise NotImplementedError