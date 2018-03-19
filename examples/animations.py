#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Orchestrates individual shapes into animations, rotation animations every 10s
"""
import itertools
import time
import pygame

import netl3d
from netl3d.l3dcube.led_state import led_state

import config
import shapes

class animations:
  def __init__(self, controller, led_state):
    self.controller = controller
    self.led_state = led_state
    self.shapes = shapes.shapes(self.controller, self.led_state)

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
        if time.time() - t1 >= 10:
          break
        self.led_state.clear()
        next(step)
        self.led_state.sync()
        time.sleep(.1)

  def outer_square(self):
    while True:
      self.shapes.wall(0)
      yield self.led_state
      self.shapes.slice(7)
      yield self.led_state
      self.shapes.wall(7)
      yield self.led_state
      self.shapes.slice(0)
      yield self.led_state

  def expanding_cube(self):
    while True:
      for i in range(2, 9, 2):
        self.shapes.centered_cube(i, fill=False)
        yield self.led_state

  def heartbeat_cube(self):
    while True:
      self.controller.adjust_color_mask(1)
      for i in range(2, 9, 2):
        self.shapes.centered_cube(i, fill=False)
        yield self.led_state
      for i in range(2, 7, 2):
        self.shapes.centered_cube(8-i, fill=False)
        yield self.led_state

if __name__ == '__main__':
  controller = netl3d.netl3d(config.L3D_DEVICE_IP)
  controller.set_debug(config.DEBUG)
  led_state = led_state(controller)
  a = animations(controller, led_state)

  controller.handshake()
  a.run()


