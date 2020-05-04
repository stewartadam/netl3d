"""
Different lighting shapes for the L3D cube.
"""
import spectra

from .l3dframe import CubeFrame

def null() -> CubeFrame:
    pass

def solid_fill(color: spectra.rgb, frame: CubeFrame = None) -> CubeFrame:
  if frame is None:
    frame = CubeFrame()
  frame.fill(color)
  return frame

def column(x: int, z: int, color: spectra.rgb, frame: CubeFrame = None) -> CubeFrame:
  if frame is None:
    frame = CubeFrame()
  for y in range(frame.face_size):
    frame.set_led((x, y, z), color)
  return frame

def wall(z: int, frame: CubeFrame = None) -> CubeFrame:
  if frame is None:
    frame = CubeFrame()
  for x in range(frame.face_size):
    for y in range(frame.face_size):
      frame.set_led((x, y, z), frame.get_color(1, 1, 1))
  return frame

def slice(x: int, frame: CubeFrame = None) -> CubeFrame:
  if frame is None:
    frame = CubeFrame()
  for y in range(frame.face_size):
    for z in range(frame.face_size):
      frame.set_led((x, y, z), frame.get_color(1, 1, 1))
  return frame

def sheet(y: int, frame: CubeFrame = None) -> CubeFrame:
  if frame is None:
    frame = CubeFrame()
  for x in range(frame.face_size):
    for z in range(frame.face_size):
      frame.set_led((x, y, z), frame.get_color(1, 1, 1))
  return frame

def centered_cube(size: int, frame: CubeFrame = None, fill: bool = True) -> CubeFrame:
  if frame is None:
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
        frame.set_led((x, y, z), frame.get_color(1, 1, 1))
  return frame
