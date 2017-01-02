# -*- coding: utf-8 -*-
"""
Basic support for 'graphing' using the L3D cube; new 8x8 frames of lighting can
be inserted at the front and existing frames are shifted back, with the last
(now 9th) frame being popping from memory.
"""
import random
import time

import config
import netl3d

class graph:
  led_state = []

  def __init__(self, controller):
    self.controller = controller
    self.empty_frame = []
    for i in range(8):
      row = []
      for j in range(8):
        row.append([0, 0, 0])
      self.empty_frame.append(row)

    for i in range(8):
      self.led_state.append(self.empty_frame)

  def slide(self, frame):
    self.led_state.pop()
    self.led_state.insert(0, frame)

    self.push_to_cube_bulk()

  # this causes out of order packets, corrupting the image
  def push_to_cube(self):
    self.debug()
    data = bytearray()
    max_index = len(self.led_state) - 1
    for i in range(max_index):
      frame = self.led_state[max_index - i]
      for col in range(8):
        for row in range(8):
          for rgb_value in frame[row][col]:
            data.append(rgb_value)
      self.controller.send_colors(i, data)
    self.controller.send_refresh()

  def push_to_cube_bulk(self):
    self.debug()
    data = bytearray()
    max_index = len(self.led_state) - 1
    led_count = 0
    for i in range(len(self.led_state)):
      frame = self.led_state[max_index - i]
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
    if not self.controller.debug:
      return;
    frame_id = 0
    for frame in self.led_state:
      print("FRAME %d" % frame_id)
      for row in frame:
        print(row)
      print
      frame_id += 1

if __name__ == '__main__':
  controller = netl3d.netl3d(config.DEVICE_IP)
  controller.debug = True
  g = graph(controller)

  static_value = 1

  def generate_frame_random():
    global static_value
    values = []
    for i in range(8):
      values.append(random.randint(0, 8))
    static_value = (static_value + 1) % 8

    frame = []
    for i in range(8):
      row = []
      for j in range(len(values)):
        controller.set_color_mask(j)
        row.append(controller.get_color(1, 1, 1) if values[j] >= i else [0, 0, 0])
      frame.append(row)
    # print('static_value = %d ' % static_value)
    # print('frame_generated:')
    # for row in frame:
    #   print(row)
    return frame

  def generate_frame_increment():
    global static_value
    values = []
    for i in range(8):
      #values.append(random.randint(0, 8))
      values.append(static_value)
    static_value = (static_value + 1) % 8

    frame = []
    for i in range(8):
      row = []
      for value in values:
        row.append([128, 128, 128] if value == i else [0, 0, 0])
      frame.append(row)
    # print('static_value = %d ' % static_value)
    # print('frame_generated:')
    # for row in frame:
    #   print(row)
    return frame

  sheet_counter = 0
  def generate_frame_sheet():
    global sheet_counter

    frame = []
    for i in range(8):
      row = []
      for j in range(8):
        row.append([128, 128, 128] if sheet_counter == 0 else [0, 0, 0])
      frame.append(row)
    # print('static_value = %d ' % static_value)
    # print('frame_generated:')
    # for row in frame:
    #   print(row)

    sheet_counter = (sheet_counter + 1) % 8
    return frame

  while 1:
    #frame = generate_frame_sheet()
    #frame = generate_frame_increment()
    frame = generate_frame_random()
    g.slide(frame)
    time.sleep(0.1)
