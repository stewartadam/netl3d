#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Generates and sends graph frames, rotating graph types every 10s.
"""
import itertools
import random
import spectra
import time

import netl3d
from netl3d.hardware import l3dcube

def generate_frame_random():
  i = 0
  while True:
    frame = l3dcube.GraphFrame()
    fill_heights = [random.randint(0, 8) for x in range(frame.face_size)]

    for x in range(frame.face_size):
      frame.set_color_mask(x)
      for y in range(fill_heights[x]+1):
        frame.set_led((x, y), frame._apply_masks(spectra.rgb(1, 1, 1)))
    yield frame

def generate_frame_increment():
  fill_height = 0
  while True:
    fill_height = (fill_height + 1) % 9

    frame = l3dcube.GraphFrame()
    for x in range(frame.face_size):
      for y in range(fill_height):
        frame.set_led((x, y), spectra.rgb(1, 1, 1))

    yield frame

def generate_frame_sheet():
  color_mask = 1
  while True:
    frame = l3dcube.GraphFrame()
    frame.set_color_mask(color_mask)

    for x in range(frame.face_size):
      for y in range(frame.face_size):
        frame.set_led((x, y), spectra.rgb(1, 1, 1))

    color_mask = max(1, (color_mask + 1) % 8)
    yield frame

    for i in range(3):
      yield l3dcube.GraphFrame()

if __name__ == "__main__":
  config = netl3d.parse_config()
  netl3d.configure_logging(config)
  ip = config['hardware']['l3dcube']['ip']
  port = config['hardware']['l3dcube']['port']

  controller = l3dcube.L3DGraphController(ip, port)
  controller.handshake()

  graphs = itertools.cycle([
    generate_frame_sheet,
    generate_frame_increment,
    generate_frame_random
  ])
  for graph in graphs:
    step = graph()
    t1 = time.time()
    while True:
      if time.time() - t1 >= 4:
        break
      frame = next(step)
      controller.sync(frame)
      time.sleep(0.25)
