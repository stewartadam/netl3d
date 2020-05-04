"""
Orchestrates individual shapes into animations, rotation animations every 10s
"""
import random
import time

from netl3d.base import FramePublisher
from netl3d.hardware import l3dcube

from .rain import rain

def random_col(frame: l3dcube.CubeFrame, fp: FramePublisher, speed: float = 0.5) -> None:
  while True:
    x = random.randint(0, frame.face_size-1)
    y = random.randint(0, frame.face_size-1)
    l3dcube.shapes.column(x, y, frame.get_color(1, 0, 1, 255), frame)
    time.sleep(speed)
    frame.clear()

def strobe(frame: l3dcube.CubeFrame, fp: FramePublisher, speed: float = 0.05) -> None:
  while True:
    l3dcube.shapes.solid_fill(frame.get_color(1, 1, 1, 255), frame=frame)
    time.sleep(speed)
    frame.clear()
    l3dcube.shapes.solid_fill(frame.get_color(1, 1, 1, 0), frame=frame)
    time.sleep(speed)
    frame.clear()

def outer_square(frame: l3dcube.CubeFrame, fp: FramePublisher, speed: float = 0.25) -> None:
  while True:
    l3dcube.shapes.wall(0, frame)
    time.sleep(speed)
    frame.clear()
    l3dcube.shapes.slice(7, frame)
    time.sleep(speed)
    frame.clear()
    l3dcube.shapes.wall(7, frame)
    time.sleep(speed)
    frame.clear()
    l3dcube.shapes.slice(0, frame)
    time.sleep(speed)
    frame.clear()
    frame.adjust_color_mask(1)

def expanding_cube(frame: l3dcube.CubeFrame, fp: FramePublisher, speed: float = 0.1) -> None:
  while True:
    frame.adjust_color_mask(1)
    for i in range(2, 9, 2):
      l3dcube.shapes.centered_cube(i, frame=frame, fill=False)
      time.sleep(speed)
      frame.clear()

def heartbeat_cube(frame: l3dcube.CubeFrame, fp: FramePublisher, speed: float = 0.1) -> None:
  while True:
    frame.adjust_color_mask(1)
    for i in range(2, 9, 2):
      l3dcube.shapes.centered_cube(i, frame=frame, fill=False)
      time.sleep(speed)
      frame.clear()
    for i in range(2, 7, 2):
      l3dcube.shapes.centered_cube(8-i, frame=frame, fill=False)
      time.sleep(speed)
      frame.clear()

def pulse(frame: l3dcube.CubeFrame, fp: FramePublisher, speed: float = 0.5) -> None:
  # Terrible way of going about this, but it works for now/demo purposes
  while True:
    frame.adjust_color_mask(1)
    # frame length, target brightness
    steps = [(2, .9), (0, None), (7, .2)]
    num_frames = sum([x[0] for x in steps])
    for i in range(num_frames):
      if i <= steps[0][0]:
        length = steps[0][0]
        brightness = steps[0][1]
        brightness = i/length * brightness + 0.1
      # elif i > steps[0][0] and i <= steps[0][0] + steps[1][0]:
      #   start = steps[0][0] + 1
      #   length = steps[1][0]
      #   brightness = 1-steps[0][1]
      #   start_brightness = steps[0][1] + 0.1
      #   brightness = (i-start)/length * brightness + start_brightness
      else:
        start = (num_frames - steps[2][0]) + 1
        length = steps[2][0]
        inverse_brightness = 1 - steps[2][1]
        brightness = 1 - ( (i-start)/length * inverse_brightness )
      frame.set_brightness_mask(brightness)
      l3dcube.shapes.centered_cube(8, frame=frame, fill=True)
      time.sleep(speed)
      frame.clear()
