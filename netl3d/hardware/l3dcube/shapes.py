# -*- coding: utf-8 -*-
"""
Different lighting shapes for the L3D cube.
"""
from .frame import CubeFrame

class Shapes:
  def __init__(self, controller):
    self.controller = controller

  def null(self):
      pass

  def wall(self, z):
    frame = CubeFrame()
    for x in range(frame.face_size):
      for y in range(frame.face_size):
        frame.set_led((x, y, z), self.controller.get_color(1, 1, 1))
    return frame

  def slice(self, x):
    frame = CubeFrame()
    for y in range(frame.face_size):
      for z in range(frame.face_size):
        frame.set_led((x, y, z), self.controller.get_color(1, 1, 1))
    return frame

  def sheet(self, y):
    frame = CubeFrame()
    for x in range(frame.face_size):
      for z in range(frame.face_size):
        frame.set_led((x, y, z), self.controller.get_color(1, 1, 1))
    return frame

  def centered_cube(self, size, fill=True):
    frame = CubeFrame()
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
          frame.set_led((x, y, z), self.controller.get_color(1, 1, 1))
    return frame
