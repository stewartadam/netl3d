# -*- coding: utf-8 -*-
"""
Orchestrates individual shapes into animations, rotation animations every 10s
"""
import itertools
import time
import pygame

import netl3d
from netl3d.hardware import l3dcube

def outer_square(frame):
  while True:
    yield l3dcube.shapes.wall(0, frame)
    yield l3dcube.shapes.slice(7, frame)
    yield l3dcube.shapes.wall(7, frame)
    yield l3dcube.shapes.slice(0, frame)
    frame.adjust_color_mask(1)

def expanding_cube(frame):
  while True:
    frame.adjust_color_mask(1)
    for i in range(2, 9, 2):
      yield l3dcube.shapes.centered_cube(i, frame=frame, fill=False)

def heartbeat_cube(frame):
  while True:
    frame.adjust_color_mask(1)
    for i in range(2, 9, 2):
      yield l3dcube.shapes.centered_cube(i, frame=frame, fill=False)
    for i in range(2, 7, 2):
      yield l3dcube.shapes.centered_cube(8-i, frame=frame, fill=False)

def pulse(frame):
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
      yield l3dcube.shapes.centered_cube(8, frame=frame, fill=True)

if __name__ == '__main__':
  config = netl3d.parse_config()
  debug = config['debug']
  ip = config['hardware']['l3dcube']['ip']
  port = config['hardware']['l3dcube']['port']

  controller = l3dcube.Controller(ip, port)
  controller.set_debug(debug)
  controller.handshake()

  animations = itertools.cycle([
    pulse,
    expanding_cube,
    outer_square,
    heartbeat_cube,
    outer_square,
  ])
  for animation in animations:
    frame = l3dcube.CubeFrame()
    step = animation(frame)
    t1 = time.time()
    while 1:
      if time.time() - t1 >= 4:
        break
      frame.clear()
      frame = next(step)
      controller.sync(frame)
      time.sleep(.075)
