# -*- coding: utf-8 -*-
"""
Basic support for 'graphing' using the L3D cube; new 8x8 frames of lighting can
be inserted at the front and existing frames are shifted back, with the last
(now 9th) frame being popping from memory.
"""
import random
import time

class graph:
  frames = []

  def __init__(self, controller):
    self.controller = controller
    self.empty_frame = []
    for i in range(8):
      row = []
      for j in range(8):
        row.append([0, 0, 0])
      self.empty_frame.append(row)

    for i in range(8):
      self.frames.append(self.empty_frame)

  def slide(self, frame):
    self.frames.pop()
    self.frames.insert(0, frame)
    self.sync()

  def sync(self):
    self.debug()
    data = bytearray()
    max_index = len(self.frames) - 1
    led_count = 0
    for i in range(len(self.frames)):
      frame = self.frames[max_index - i]
      for col in range(8):
        for row in range(8):
          led_count += 1
          for rgb_value in frame[row][col]:
          	data.append(rgb_value)
          if led_count % self.controller.LED_PER_PACKET == 0:
            self.controller.send_colors(led_count - self.controller.LED_PER_PACKET, data)
            data = bytearray()
    self.controller.send_refresh()

  def debug(self):
    if not self.controller.get_debug():
      return;
    frame_id = 0
    for frame in self.frames:
      print("FRAME %d" % frame_id)
      for row in frame:
        print(row)
      print
      frame_id += 1
