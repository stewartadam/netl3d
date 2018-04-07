#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Orchestrates individual shapes into animations, rotation animations every 10s
"""
import itertools
import time
import pygame

import netl3d
from netl3d.hardware import l3dcube

import config

class animations:
  def __init__(self, controller):
    self.controller = controller
    self.shapes = l3dcube.Shapes(self.controller)

  def run(self):
    animations = itertools.cycle([
      self.heartbeat_cube,
      self.outer_square,
      self.expanding_cube,
      self.heartbeat_cube
    ])
    for animation in animations:
      step = animation()
      t1 = time.time()
      while 1:
        if time.time() - t1 >= 2:
          break
        frame = next(step)
        self.controller.sync(frame)
        time.sleep(.1)

  def outer_square(self):
    while True:
      yield self.shapes.wall(0)
      yield self.shapes.slice(7)
      yield self.shapes.wall(7)
      yield self.shapes.slice(0)

  def expanding_cube(self):
    while True:
      for i in range(2, 9, 2):
        yield self.shapes.centered_cube(i, fill=False)

  def heartbeat_cube(self):
    while True:
      self.controller.adjust_color_mask(1)
      for i in range(2, 9, 2):
        yield self.shapes.centered_cube(i, fill=False)
      for i in range(2, 7, 2):
        yield self.shapes.centered_cube(8-i, fill=False)

if __name__ == '__main__':
  controller = l3dcube.Controller(config.L3D_DEVICE_IP)
  controller.set_debug(config.DEBUG)
  a = animations(controller)

  controller.handshake()
  a.run()


