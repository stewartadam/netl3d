# -*- coding: utf-8 -*-
"""
Different lighting shapes for the L3D cube.
"""
class shapes:
  def __init__(self, controller, led_state):
    self.controller = controller
    self.led_state = led_state

  def null(self):
      pass

  def wall(self, offset):
    for i in range (offset*64, (offset+1)*64):
      self.led_state[i] = self.controller.get_color(1, 1, 1)

  def slice(self, offset):
    for i in range(8):
      for j in range(8):
        self.led_state[offset*8 + i*64+j] = self.controller.get_color(1, 1, 1)

  def sheet(self, offset):
    for i in range(self.controller.LED_NUM // 8):
      self.led_state[offset + i*8] = self.controller.get_color(1, 1, 1)

  def centered_cube(self, size, fill=True):
    if size % 2 == 1:
      raise ValueError("Cube size must be divisible by two.")
    # -1 because for size=2 we want offset=0
    offset = int(size / 2) - 1
    # +1 because we want 4+offset (inclusive)
    sizing = range(3-offset, 4+offset+1)
    limits = [max(sizing), min(sizing)]
    for x in sizing:
      for y in sizing:
        for z in sizing:
          if not fill and x not in limits and y not in limits and z not in limits:
            continue
          self.led_state.set_point(x, y, z, self.controller.get_color(1, 1, 1))
