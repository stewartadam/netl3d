#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Generates and sends graph frames, rotating graph types every 10s.
"""
import itertools
import pygame
import random
import time

import config
import netl3d
from netl3d.l3dcube import graph

controller = netl3d.netl3d(config.L3D_DEVICE_IP)
controller.set_debug(config.DEBUG)
controller.handshake()
g = graph(controller)

def generate_frame_random():
  while True:
    values = []
    for i in range(8):
      values.append(random.randint(0, 8))
    frame = []
    for i in range(8):
      row = []
      for j in range(len(values)):
        controller.set_color_mask(j)
        row.append(controller.get_color(1, 1, 1) if values[j] >= i else [0, 0, 0])
      frame.append(row)
    yield frame

def generate_frame_increment():
  static_value = 1
  while True:
    values = []
    for i in range(8):
      values.append(static_value)
    static_value = (static_value + 1) % 8

    frame = []
    for i in range(8):
      row = []
      for value in values:
        row.append([128, 128, 128] if value == i else [0, 0, 0])
      frame.append(row)
    yield frame

def generate_frame_sheet():
  sheet_counter = 0
  while True:
    frame = []
    for i in range(8):
      row = []
      for j in range(8):
        row.append([128, 128, 128] if sheet_counter == 0 else [0, 0, 0])
      frame.append(row)
    sheet_counter = (sheet_counter + 1) % 8
    yield frame

def run():
  graphs = itertools.cycle([
    generate_frame_sheet,
    generate_frame_increment,
    generate_frame_random
  ])
  for graph in graphs:
    step = graph()
    t1 = time.time()
    while True:
      if time.time() - t1 >= 2:
        break
      frame = next(step)
      g.slide(frame)
      g.sync()
      pygame.time.wait(100)

if __name__ == "__main__":
  run()
